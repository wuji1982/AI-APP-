"""
风控服务
AI智能风控Agent: 实时监控限购/异常操作/违规开团
"""
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.risk_control import RiskControlLog, UserRiskScore, RiskLevel, RiskAction, RiskRuleType
from app.models.group_buy import GroupBuyOrder, OrderStatus


class RiskService:
    """风控服务"""

    @staticmethod
    async def check_join_risk(
        db: AsyncSession,
        user_id: int,
        session_id: int,
    ) -> dict:
        """检查用户参团风控
        规则:
        1. 单ID单组最多5单
        2. 检查用户风险评分
        3. 检查异常频率
        """
        # 1. 检查黑名单
        risk_score_result = await db.execute(
            select(UserRiskScore).where(UserRiskScore.user_id == user_id)
        )
        risk_score = risk_score_result.scalar_one_or_none()
        if risk_score and risk_score.is_blacklisted:
            return {"allowed": False, "reason": "用户已被列入黑名单", "risk_level": "critical"}

        # 2. 检查单组参与次数
        result = await db.execute(
            select(func.count()).select_from(GroupBuyOrder).where(
                and_(
                    GroupBuyOrder.user_id == user_id,
                    GroupBuyOrder.session_id == session_id,
                    GroupBuyOrder.status.in_([OrderStatus.PENDING, OrderStatus.LOCKED]),
                )
            )
        )
        count = result.scalar()
        if count >= settings.GROUP_BUY_MAX_ORDERS_PER_USER:
            # 记录风控日志
            log = RiskControlLog(
                user_id=user_id,
                rule_type=RiskRuleType.ORDER_LIMIT,
                risk_level=RiskLevel.MEDIUM,
                action=RiskAction.BLOCK,
                description=f"用户{user_id}单组参与{count}次, 超过上限{settings.GROUP_BUY_MAX_ORDERS_PER_USER}",
                related_session_id=session_id,
            )
            db.add(log)
            return {"allowed": False, "reason": f"超过单组{settings.GROUP_BUY_MAX_ORDERS_PER_USER}单上限", "risk_level": "medium"}

        # 3. 检查风险评分
        if risk_score and risk_score.risk_score > 80:
            log = RiskControlLog(
                user_id=user_id,
                rule_type=RiskRuleType.ABNORMAL_BEHAVIOR,
                risk_level=RiskLevel.HIGH,
                action=RiskAction.WARN,
                description=f"用户风险评分{risk_score.risk_score}, 超过阈值80",
                related_session_id=session_id,
            )
            db.add(log)
            return {"allowed": True, "reason": "高风险用户, 已记录警告", "risk_level": "high", "warning": True}

        return {"allowed": True, "reason": "通过风控检查", "risk_level": "low"}

    @staticmethod
    async def update_risk_score(
        db: AsyncSession,
        user_id: int,
        event_type: str,
    ) -> None:
        """更新用户风险评分"""
        result = await db.execute(
            select(UserRiskScore).where(UserRiskScore.user_id == user_id)
        )
        score = result.scalar_one_or_none()

        if not score:
            score = UserRiskScore(user_id=user_id, risk_score=0)
            db.add(score)

        # 根据事件类型增加风险分
        score_map = {
            "order_limit_exceed": 10,
            "abnormal_frequency": 20,
            "illegal_group": 50,
            "amount_anomaly": 15,
        }
        score.risk_score += score_map.get(event_type, 5)
        score.total_warnings += 1
        score.last_risk_event = datetime.utcnow()

        # 超过阈值加入黑名单
        if score.risk_score >= 100:
            score.is_blacklisted = True

        await db.flush()

    @staticmethod
    async def get_risk_logs(
        db: AsyncSession,
        user_id: int = None,
        risk_level: RiskLevel = None,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        """获取风控日志"""
        query = select(RiskControlLog)
        if user_id:
            query = query.where(RiskControlLog.user_id == user_id)
        if risk_level:
            query = query.where(RiskControlLog.risk_level == risk_level)

        count_query = select(func.count()).select_from(RiskControlLog)
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        result = await db.execute(
            query.order_by(RiskControlLog.created_at.desc())
            .offset((page - 1) * size).limit(size)
        )
        logs = result.scalars().all()

        return {"total": total, "page": page, "size": size, "items": logs}
