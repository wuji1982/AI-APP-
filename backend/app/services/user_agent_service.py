"""
用户智能体服务
每个注册用户拥有独立的AI智能体实例
"""
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_agent import UserAgent, UserAgentMemory, AgentKnowledgeSource
from app.services.dify_client import dify_client
from app.config import settings

logger = logging.getLogger(__name__)


# 平台共享知识（所有用户智能体都可访问）
PLATFORM_KNOWLEDGE = [
    {
        "name": "平台规则",
        "content": """
AI星木共享商城平台规则：
1. 拼团机制：每场31人，满员自动开团，未满足自动退款
2. 贡献值分配：初级288元→2880贡献值，高级1440元→17280贡献值，SVIP 11520元→172800贡献值
3. 贡献值释放：每日释放0.3%，需完成浏览/分享任务加速
4. 积分通缩：总量1200万枚，贡献值兑换比例逐月递减10%
5. 消费券：积分按递减比例兑换，每月1日刷新
6. 门店分红：每月销售额10-50万→0.5%，50万以上→1%
7. 线下分润：一代10%、二代5%、三代3%
"""
    },
    {
        "name": "拼团指南",
        "content": """
拼团参与指南：
- 每日10:00/14:00/20:00 三个场次
- 可选择初级(288元)、高级(1440元)、SVIP(11520元)商品
- 拼团成功后获得对应贡献值
- 贡献值每日释放0.3%到积分账户
- 可通过邀请好友获得额外贡献值奖励
- 团队消费可获得分润奖励
"""
    },
    {
        "name": "收益计算",
        "content": """
收益计算方式：
1. 直推奖励：邀请好友参团，获得好友贡献值的10%
2. 团队分润：一级团队成员消费额的10%
3. 门店分红：成为店主后享受门店销售额分红
4. 积分兑换：积分可兑换消费券，用于下次购物抵扣
5. 贡献值加速：完成每日任务可加速贡献值释放
"""
    }
]


class UserAgentService:
    """用户智能体服务"""

    def __init__(self):
        self.dify = dify_client

    async def create_agent_for_user(
        self,
        db: AsyncSession,
        user_id: int,
        phone: str,
        nickname: str
    ) -> UserAgent:
        """
        为新注册用户创建独立的AI智能体
        在用户注册时自动调用
        """
        logger.info(f"为用户 {user_id} 创建智能体...")

        # 1. 在Dify创建用户专属知识库
        dataset = await self.dify.create_dataset(
            name=f"用户{user_id}_知识库",
            description=f"用户{phone}的私有知识库"
        )
        dataset_id = dataset.get("id", "")

        # 2. 上传平台共享知识
        for knowledge in PLATFORM_KNOWLEDGE:
            await self.dify.upload_document(
                dataset_id=dataset_id,
                name=knowledge["name"],
                text=knowledge["content"]
            )

        # 3. 创建用户专属Agent应用
        app = await self.dify.create_app(
            name=f"用户{user_id}_智能助手",
            mode="chat",
            description=f"用户{nickname}的专属AI助手"
        )
        app_id = app.get("id", "")
        api_key = app.get("api_key", "")

        # 4. 保存智能体配置到数据库
        agent = UserAgent(
            user_id=user_id,
            dify_app_id=app_id,
            dify_api_key=api_key,
            dify_dataset_id=dataset_id,
            agent_name=f"{nickname}的AI助手",
            agent_avatar="",
            system_prompt=self._build_system_prompt(nickname, user_id),
            is_active=True,
            created_at=datetime.now()
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)

        logger.info(f"用户 {user_id} 智能体创建成功，AppID: {app_id}")
        return agent

    async def get_user_agent(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Optional[UserAgent]:
        """获取用户的智能体"""
        result = await db.execute(
            select(UserAgent).where(
                UserAgent.user_id == user_id,
                UserAgent.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def chat(
        self,
        db: AsyncSession,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        用户与智能体对话
        返回: {"answer": str, "conversation_id": str, "sources": list}
        """
        agent = await self.get_user_agent(db, user_id)
        if not agent:
            raise ValueError("智能体不存在，请先注册")

        # 调用Dify对话API
        response = await self.dify.chat(
            api_key=agent.dify_api_key,
            query=message,
            user=str(user_id),
            conversation_id=conversation_id
        )

        # 保存对话记忆
        await self._save_memory(db, agent.id, message, response.get("answer", ""))

        return {
            "answer": response.get("answer", ""),
            "conversation_id": response.get("conversation_id", ""),
            "sources": response.get("retriever_resources", [])
        }

    async def chat_stream(
        self,
        db: AsyncSession,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None
    ):
        """流式对话"""
        agent = await self.get_user_agent(db, user_id)
        if not agent:
            raise ValueError("智能体不存在")

        async for chunk in self.dify.chat_stream(
            api_key=agent.dify_api_key,
            query=message,
            user=str(user_id),
            conversation_id=conversation_id
        ):
            yield chunk

    async def add_personal_knowledge(
        self,
        db: AsyncSession,
        user_id: int,
        title: str,
        content: str
    ) -> Dict:
        """
        添加用户私有知识
        例如：个人偏好、特殊需求等
        """
        agent = await self.get_user_agent(db, user_id)
        if not agent:
            raise ValueError("智能体不存在")

        result = await self.dify.upload_document(
            dataset_id=agent.dify_dataset_id,
            name=title,
            text=content
        )

        # 记录知识来源
        source = AgentKnowledgeSource(
            agent_id=agent.id,
            source_type="personal",
            title=title,
            content=content,
            created_at=datetime.now()
        )
        db.add(source)
        await db.commit()

        return result

    async def update_user_context(
        self,
        db: AsyncSession,
        user_id: int,
        user_data: Dict[str, Any]
    ) -> None:
        """
        更新用户上下文信息到知识库
        当用户数据变化时调用（如消费、贡献值变化）
        """
        agent = await self.get_user_agent(db, user_id)
        if not agent:
            return

        # 构建用户上下文
        context = f"""
用户最新数据（{datetime.now().strftime('%Y-%m-%d %H:%M')}）：
- 贡献值余额：{user_data.get('contribution_balance', 0)}
- 积分余额：{user_data.get('points_balance', 0)}
- 消费券余额：{user_data.get('coupon_balance', 0)}
- 团队人数：{user_data.get('team_count', 0)}
- 本月消费：{user_data.get('monthly_spending', 0)}
- 会员等级：{user_data.get('level', '普通用户')}
"""
        # 更新到知识库
        await self.dify.upload_document(
            dataset_id=agent.dify_dataset_id,
            name="用户实时数据",
            text=context
        )

    async def get_conversations(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[Dict]:
        """获取用户的历史对话"""
        agent = await self.get_user_agent(db, user_id)
        if not agent:
            return []
        return await self.dify.get_conversations(
            api_key=agent.dify_api_key,
            user=str(user_id)
        )

    async def _save_memory(
        self,
        db: AsyncSession,
        agent_id: int,
        user_message: str,
        agent_response: str
    ) -> None:
        """保存对话记忆"""
        memory = UserAgentMemory(
            agent_id=agent_id,
            role="user",
            content=user_message,
            created_at=datetime.now()
        )
        db.add(memory)
        
        memory2 = UserAgentMemory(
            agent_id=agent_id,
            role="assistant",
            content=agent_response,
            created_at=datetime.now()
        )
        db.add(memory2)
        await db.commit()

    def _build_system_prompt(self, nickname: str, user_id: int) -> str:
        """构建智能体系统提示词"""
        return f"""
你是{nickname}的专属AI助手，服务于AI星木共享商城平台。

你的职责：
1. 解答用户关于平台规则、拼团机制、收益计算等问题
2. 根据用户的消费历史和偏好，提供个性化建议
3. 帮助用户优化收益策略（如何更快积累贡献值、如何最大化分红）
4. 提醒用户重要事项（拼团时间、消费券过期、分红到账）
5. 协助用户进行团队管理建议

注意事项：
- 回答要简洁、友好、专业
- 涉及具体金额计算时，要给出清晰的计算过程
- 不确定的信息要明确告知用户
- 保护用户隐私，不泄露其他用户信息
- 引导用户合理消费，理性参与拼团

用户ID: {user_id}
"""


# 全局服务实例
user_agent_service = UserAgentService()
