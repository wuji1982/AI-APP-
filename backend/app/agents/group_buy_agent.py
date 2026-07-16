"""
AI拼团调度Agent
职责: 定时触发开团→检查人数→匹配板块→核验订单→判定结果→触发分账
"""
from typing import Any, Dict
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.models.group_buy import GroupBuySession, SessionStatus
from app.services.group_buy_service import GroupBuyService


class GroupBuyAgent(BaseAgent):
    """拼团调度Agent"""

    def __init__(self):
        super().__init__("group_buy_agent", "AI拼团调度Agent-管控全场拼团启停/人数监控/结果判定")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        db: AsyncSession = context["db"]
        action = context.get("action", "check_sessions")

        if action == "create_sessions":
            # 创建每日场次
            date = context.get("date", datetime.utcnow())
            sessions = await GroupBuyService.create_daily_sessions(db, date)
            return {"action": "create_sessions", "created": len(sessions)}

        elif action == "check_and_settle":
            # 检查已满场次并结算
            result = await db.execute(
                select(GroupBuySession).where(
                    GroupBuySession.status == SessionStatus.FULL
                )
            )
            full_sessions = result.scalars().all()
            settled = []
            for session in full_sessions:
                try:
                    settle_result = await GroupBuyService.settle_session(db, session.id)
                    settled.append(settle_result)
                except Exception as e:
                    self.logger.error(f"场次{session.id}结算失败: {e}")
            return {"action": "check_and_settle", "settled_count": len(settled)}

        elif action == "check_expired":
            # 处理过期场次
            now = datetime.utcnow()
            result = await db.execute(
                select(GroupBuySession).where(
                    GroupBuySession.status.in_([SessionStatus.PENDING, SessionStatus.ACTIVE]),
                    GroupBuySession.end_time < now,
                )
            )
            expired = result.scalars().all()
            for session in expired:
                session.status = SessionStatus.EXPIRED
            await db.flush()
            return {"action": "check_expired", "expired_count": len(expired)}

        return {"action": action, "message": "未知操作"}

    async def should_continue(self, context: Dict[str, Any]) -> bool:
        return False  # 单次执行即可
