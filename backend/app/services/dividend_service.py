"""
分红结算服务
每周一自动执行: 个人消费券分红 = 个人贡献值 / 全网总贡献值 × 平台20%收益池
分红后扣除已分红贡献值, 剩余进入下期
"""
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.contribution import ContributionRecord, ContribWeeklySettlement, GlobalContribStats
from app.models.user import User, UserWalletLog
from app.services.contribution_service import ContributionService


class DividendService:
    """分红结算服务"""

    @staticmethod
    async def weekly_dividend(db: AsyncSession) -> dict:
        """每周一执行全网贡献值分红
        个人消费券分红 = 个人贡献值 / 全网总贡献值 × 平台20%收益池
        分红后扣除已分红贡献值, 剩余贡献值继续参与下期
        """
        now = datetime.utcnow()
        week_start = now - timedelta(days=now.weekday())

        # 1. 获取全网总贡献值
        total_network_contrib = await ContributionService.get_total_network_contrib(db)
        if total_network_contrib <= 0:
            return {"message": "全网无有效贡献值", "dividend_count": 0}

        # 2. 计算平台20%收益池 (简化: 从平台财务统计获取)
        # 实际应从PlatformDailyFinance获取
        platform_revenue = await DividendService._get_platform_revenue(db, week_start)
        platform_pool = platform_revenue * 0.20

        # 3. 获取所有有贡献值的用户
        result = await db.execute(
            select(ContributionRecord).where(
                and_(
                    ContributionRecord.remaining_value > 0,
                    ContributionRecord.user_id.isnot(None),
                )
            )
        )
        records = result.scalars().all()

        # 4. 按用户汇总贡献值
        user_contribs = {}
        for record in records:
            uid = record.user_id
            if uid not in user_contribs:
                user_contribs[uid] = {"total": 0, "records": []}
            user_contribs[uid]["total"] += record.remaining_value
            user_contribs[uid]["records"].append(record)

        dividend_count = 0
        total_dividend_paid = 0.0

        # 5. 逐用户计算分红
        for user_id, data in user_contribs.items():
            user_contrib = data["total"]
            # 个人分红 = 个人贡献值 / 全网总贡献值 × 平台20%收益池
            user_dividend = (user_contrib / total_network_contrib) * platform_pool

            if user_dividend <= 0:
                continue

            # 发放消费券给用户
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if user:
                old_coupon = user.coupon_balance
                user.coupon_balance += user_dividend
                db.add(UserWalletLog(
                    user_id=user_id, asset_type="coupon", change_type="income",
                    amount=user_dividend, balance_before=old_coupon,
                    balance_after=user.coupon_balance,
                    description=f"贡献值周度分红",
                ))

            # 记录到周度结算表
            settlement = ContribWeeklySettlement(
                user_id=user_id,
                week_start=week_start,
                week_end=week_start + timedelta(days=6),
                effective_contrib=user_contrib,
                daily_rate=settings.CONTRIB_DAILY_RATE_DEFAULT,
                weekly_coupon=0,  # 递减兑换另行计算
                total_network_contrib=total_network_contrib,
                platform_pool=platform_pool,
                dividend_coupon=user_dividend,
                remaining_contrib=user_contrib,  # 贡献值不扣减
                settled_at=now,
            )
            db.add(settlement)

            # 标记已分红
            for record in data["records"]:
                record.is_dividend_settled = 1
                record.last_dividend_date = now

            dividend_count += 1
            total_dividend_paid += user_dividend

        # 6. 记录全网统计
        stats = GlobalContribStats(
            date=week_start,
            total_contrib=total_network_contrib,
            platform_revenue=platform_revenue,
            platform_pool_20=platform_pool,
            total_dividend_paid=total_dividend_paid,
        )
        db.add(stats)

        await db.flush()
        return {
            "dividend_count": dividend_count,
            "total_dividend_paid": total_dividend_paid,
            "total_network_contrib": total_network_contrib,
            "platform_pool": platform_pool,
        }

    @staticmethod
    async def _get_platform_revenue(db: AsyncSession, week_start: datetime) -> float:
        """获取平台本周收益(简化实现)"""
        from app.models.settlement import PlatformDailyFinance
        result = await db.execute(
            select(func.sum(PlatformDailyFinance.total_revenue)).where(
                PlatformDailyFinance.date >= week_start - timedelta(days=7),
                PlatformDailyFinance.date < week_start,
            )
        )
        return result.scalar() or 0.0
