"""
Agent编排调度器
协调7大Agent的执行顺序和数据传递
"""
import logging
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.group_buy_agent import GroupBuyAgent
from app.agents.all_agents import (
    SettlementAgent, RightsAgent, DividendAgent,
    UserOpsAgent, TeamAgent, RiskAgent,
)

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Agent编排调度器 - 协调7大Agent协作"""

    def __init__(self):
        self.agents = {
            "group_buy": GroupBuyAgent(),
            "settlement": SettlementAgent(),
            "rights": RightsAgent(),
            "dividend": DividendAgent(),
            "user_ops": UserOpsAgent(),
            "team": TeamAgent(),
            "risk": RiskAgent(),
        }

    async def run_group_buy_pipeline(self, db: AsyncSession, session_id: int) -> Dict[str, Any]:
        """拼团完整流水线: 风控→结算→权益→通知"""
        results = {}

        # 1. 风控Agent检查
        risk_result = await self.agents["risk"].run({"db": db, "session_id": session_id})
        results["risk"] = risk_result

        # 2. 分账Agent结算
        settlement_result = await self.agents["settlement"].run({"db": db, "session_id": session_id})
        results["settlement"] = settlement_result

        # 3. 权益核算Agent发放
        rights_result = await self.agents["rights"].run({"db": db, "session_id": session_id})
        results["rights"] = rights_result

        # 4. 用户运营Agent通知
        notify_result = await self.agents["user_ops"].run({"db": db, "action": "notify_result"})
        results["user_ops"] = notify_result

        return results

    async def run_daily_routine(self, db: AsyncSession) -> Dict[str, Any]:
        """每日例行任务"""
        results = {}

        # 1. 创建今日场次
        create_result = await self.agents["group_buy"].run({"db": db, "action": "create_sessions"})
        results["create_sessions"] = create_result

        # 2. 检查过期场次
        expire_result = await self.agents["group_buy"].run({"db": db, "action": "check_expired"})
        results["check_expired"] = expire_result

        # 3. 结算已满场次
        settle_result = await self.agents["group_buy"].run({"db": db, "action": "check_and_settle"})
        results["check_and_settle"] = settle_result

        return results

    async def run_weekly_settlement(self, db: AsyncSession) -> Dict[str, Any]:
        """每周一结算任务: 贡献值递减兑换 + 分红"""
        results = {}

        # 1. 分红结算
        dividend_result = await self.agents["dividend"].run({"db": db})
        results["dividend"] = dividend_result

        return results

    async def run_monthly_store_dividend(self, db: AsyncSession, year_month: str) -> Dict[str, Any]:
        """月度门店阶梯分红"""
        result = await self.agents["team"].run({"db": db, "year_month": year_month})
        return {"team_dividend": result}

    def get_agent_status(self) -> Dict[str, str]:
        """获取所有Agent状态"""
        return {name: agent.description for name, agent in self.agents.items()}


# 全局编排器实例
orchestrator = AgentOrchestrator()
