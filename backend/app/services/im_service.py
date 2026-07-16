"""
IM业务服务层
处理用户注册同步、拼团建群、消息推送等业务逻辑
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.group_buy import GroupBuySession, GroupBuyOrder
from app.services.openim_client import openim_client

logger = logging.getLogger(__name__)


class IMService:
    """IM业务服务"""

    def __init__(self):
        self.client = openim_client

    # ========== 用户IM账号管理 ==========

    async def sync_user_to_im(
        self,
        user_id: int,
        nickname: str,
        avatar: str = "",
        phone: str = ""
    ) -> bool:
        """
        用户注册时同步创建IM账号
        在用户注册后台任务中调用
        """
        try:
            await self.client.register_user(
                user_id=str(user_id),
                name=nickname,
                face_url=avatar,
                phone=phone
            )
            logger.info(f"用户 {user_id} IM账号创建成功")
            return True
        except Exception as e:
            logger.error(f"用户 {user_id} IM账号创建失败: {e}")
            return False

    async def update_user_im_info(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        avatar: Optional[str] = None
    ) -> bool:
        """更新用户IM信息"""
        try:
            kwargs = {}
            if nickname:
                kwargs["name"] = nickname
            if avatar:
                kwargs["face_url"] = avatar
            
            await self.client.update_user_info(str(user_id), **kwargs)
            return True
        except Exception as e:
            logger.error(f"更新用户 {user_id} IM信息失败: {e}")
            return False

    # ========== 好友关系管理 ==========

    async def auto_add_friends(
        self,
        user_id: int,
        referrer_id: Optional[int] = None
    ) -> bool:
        """
        自动建立好友关系
        - 用户与推荐人自动成为好友
        """
        try:
            if referrer_id:
                await self.client.add_friend(
                    from_id=str(user_id),
                    to_id=str(referrer_id),
                    req_msg="我是您推荐的用户"
                )
                # 自动同意申请
                await self.client.process_friend_application(
                    user_id=str(referrer_id),
                    friend_user_id=str(user_id),
                    handle_result=1
                )
                logger.info(f"用户 {user_id} 与推荐人 {referrer_id} 自动成为好友")
            return True
        except Exception as e:
            logger.error(f"自动添加好友失败: {e}")
            return False

    async def get_user_friends(self, user_id: int) -> List[Dict]:
        """获取用户好友列表"""
        try:
            return await self.client.get_friend_list(str(user_id))
        except Exception as e:
            logger.error(f"获取用户 {user_id} 好友列表失败: {e}")
            return []

    # ========== 群组管理 ==========

    async def create_group_buy_group(
        self,
        session_id: int,
        creator_id: int,
        member_ids: List[int],
        level_name: str = "拼团"
    ) -> Optional[str]:
        """
        拼团成功后自动创建临时群
        用于团成员交流
        """
        try:
            group_id = f"group_buy_{session_id}"
            group_name = f"{level_name}团 #{session_id}"
            
            await self.client.create_group(
                group_id=group_id,
                group_name=group_name,
                owner_id=str(creator_id),
                member_ids=[str(uid) for uid in member_ids],
                introduction=f"拼团场次 #{session_id} 的临时交流群"
            )
            
            # 发送欢迎消息
            await self.client.send_group_message(
                send_id=str(creator_id),
                group_id=group_id,
                content=f"🎉 欢迎来到{level_name}团！祝大家都能拼中！"
            )
            
            logger.info(f"拼团群 {group_id} 创建成功")
            return group_id
        except Exception as e:
            logger.error(f"创建拼团群失败: {e}")
            return None

    async def create_team_group(
        self,
        team_id: int,
        leader_id: int,
        member_ids: List[int],
        team_name: str = ""
    ) -> Optional[str]:
        """
        创建团队群
        用于团队成员沟通
        """
        try:
            group_id = f"team_{team_id}"
            group_name = team_name or f"团队 #{team_id}"
            
            await self.client.create_group(
                group_id=group_id,
                group_name=group_name,
                owner_id=str(leader_id),
                member_ids=[str(uid) for uid in member_ids],
                introduction="团队成员交流群"
            )
            
            logger.info(f"团队群 {group_id} 创建成功")
            return group_id
        except Exception as e:
            logger.error(f"创建团队群失败: {e}")
            return None

    async def create_store_group(
        self,
        store_id: int,
        owner_id: int,
        staff_ids: List[int],
        store_name: str = ""
    ) -> Optional[str]:
        """
        创建门店员工群
        """
        try:
            group_id = f"store_{store_id}"
            group_name = store_name or f"门店 #{store_id}"
            
            await self.client.create_group(
                group_id=group_id,
                group_name=group_name,
                owner_id=str(owner_id),
                member_ids=[str(uid) for uid in staff_ids],
                introduction="门店员工交流群"
            )
            
            logger.info(f"门店群 {group_id} 创建成功")
            return group_id
        except Exception as e:
            logger.error(f"创建门店群失败: {e}")
            return None

    async def dismiss_group_buy_group(self, session_id: int) -> bool:
        """拼团结束后解散临时群"""
        try:
            group_id = f"group_buy_{session_id}"
            await self.client.dismiss_group(group_id)
            logger.info(f"拼团群 {group_id} 已解散")
            return True
        except Exception as e:
            logger.error(f"解散拼团群失败: {e}")
            return False

    # ========== 消息推送 ==========

    async def send_order_notification(
        self,
        user_id: int,
        order_no: str,
        status: str
    ) -> bool:
        """发送订单状态通知"""
        try:
            status_map = {
                "created": "订单已创建",
                "paid": "订单已支付",
                "shipped": "订单已发货",
                "completed": "订单已完成",
                "cancelled": "订单已取消"
            }
            msg = f"📦 您的订单 {order_no} {status_map.get(status, status)}"
            
            await self.client.send_business_notification(
                send_id="system",
                recv_id=str(user_id),
                notification=msg
            )
            return True
        except Exception as e:
            logger.error(f"发送订单通知失败: {e}")
            return False

    async def send_group_buy_notification(
        self,
        user_id: int,
        session_id: int,
        result: str  # "win" or "lose"
    ) -> bool:
        """发送拼团结果通知"""
        try:
            if result == "win":
                msg = f"🎉 恭喜！您在拼团 #{session_id} 中拼中成功！"
            else:
                msg = f"😢 很遗憾，您在拼团 #{session_id} 中未拼中，已自动退款"
            
            await self.client.send_business_notification(
                send_id="system",
                recv_id=str(user_id),
                notification=msg
            )
            return True
        except Exception as e:
            logger.error(f"发送拼团通知失败: {e}")
            return False

    async def send_contribution_notification(
        self,
        user_id: int,
        amount: float,
        source: str
    ) -> bool:
        """发送贡献值变动通知"""
        try:
            msg = f"🎯 您获得 {amount} 贡献值（来源：{source}）"
            
            await self.client.send_business_notification(
                send_id="system",
                recv_id=str(user_id),
                notification=msg
            )
            return True
        except Exception as e:
            logger.error(f"发送贡献值通知失败: {e}")
            return False

    async def send_settlement_notification(
        self,
        user_id: int,
        amount: float,
        settlement_type: str
    ) -> bool:
        """发送结算通知"""
        try:
            type_map = {
                "dividend": "门店分红",
                "profit_share": "团队分润",
                "contribution": "贡献值结算"
            }
            msg = f"💰 {type_map.get(settlement_type, '结算')}到账：{amount} 元"
            
            await self.client.send_business_notification(
                send_id="system",
                recv_id=str(user_id),
                notification=msg
            )
            return True
        except Exception as e:
            logger.error(f"发送结算通知失败: {e}")
            return False

    async def push_offline_notification(
        self,
        user_ids: List[int],
        title: str,
        content: str,
        ext: Optional[Dict] = None
    ) -> bool:
        """发送离线推送"""
        try:
            await self.client.push_message(
                user_ids=[str(uid) for uid in user_ids],
                title=title,
                content=content,
                ext=ext
            )
            return True
        except Exception as e:
            logger.error(f"发送离线推送失败: {e}")
            return False


# 全局服务实例
im_service = IMService()
