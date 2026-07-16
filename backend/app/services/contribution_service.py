"""
贡献值核算服务
全网统一公式: 各方贡献值 = 让利金额 × 分配比例 × 10
三大场景通用: 线上零售/拼团成功/线下门店消费
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.contribution import ContributionRecord, ContribSource, ContribRole, ContribWeeklySettlement, GlobalContribStats
from app.models.user import User, UserWalletLog


class ContributionService:
    """贡献值核算服务"""

    # 六大角色分配比例
    ROLE_RATIOS = {
        ContribRole.CONSUMER: settings.CONTRIB_CONSUMER_RATIO,           # 50%
        ContribRole.MERCHANT: settings.CONTRIB_MERCHANT_RATIO,           # 20%
        ContribRole.REFERRAL_MERCHANT: settings.CONTRIB_REFERRAL_MERCHANT_RATIO,  # 8%
        ContribRole.REFERRAL_CONSUMER: settings.CONTRIB_REFERRAL_CONSUMER_RATIO,  # 5%
        ContribRole.AGENT: settings.CONTRIB_AGENT_RATIO,                 # 7%
        ContribRole.PLATFORM: settings.CONTRIB_PLATFORM_RATIO,           # 10%
    }

    @staticmethod
    def calculate_contribution(base_amount: float, ratio: float) -> float:
        """通用贡献值计算公式
        贡献值 = 让利金额 × 分配比例 × 10
        让利金额 = 消费金额 × 20%
        """
        discount_amount = base_amount * settings.GLOBAL_DISCOUNT_RATIO
        return discount_amount * ratio * settings.CONTRIB_MULTIPLIER

    @staticmethod
    async def generate_contributions(
        db: AsyncSession,
        base_amount: float,
        source: ContribSource,
        consumer_id: int,
        merchant_id: Optional[int] = None,
        referrer_merchant_id: Optional[int] = None,
        referrer_consumer_id: Optional[int] = None,
        agent_ids: Optional[dict] = None,  # {"province": x, "city": y, "district": z}
        related_order_id: Optional[int] = None,
        related_session_id: Optional[int] = None,
    ) -> list:
        """为单笔交易生成全角色贡献值记录
        按6个角色分别计算并记录
        """
        discount_amount = base_amount * settings.GLOBAL_DISCOUNT_RATIO
        records = []

        # 1. 消费者贡献值 (50%)
        consumer_contrib = ContributionService.calculate_contribution(
            base_amount, settings.CONTRIB_CONSUMER_RATIO
        )
        records.append(ContributionService._create_record(
            user_id=consumer_id, source=source, role=ContribRole.CONSUMER,
            base_amount=base_amount, discount_amount=discount_amount,
            ratio=settings.CONTRIB_CONSUMER_RATIO, contrib_value=consumer_contrib,
            remaining_value=consumer_contrib,
            related_order_id=related_order_id, related_session_id=related_session_id,
        ))

        # 2. 合作商家贡献值 (20%)
        if merchant_id:
            merchant_contrib = ContributionService.calculate_contribution(
                base_amount, settings.CONTRIB_MERCHANT_RATIO
            )
            records.append(ContributionService._create_record(
                user_id=merchant_id, source=source, role=ContribRole.MERCHANT,
                base_amount=base_amount, discount_amount=discount_amount,
                ratio=settings.CONTRIB_MERCHANT_RATIO, contrib_value=merchant_contrib,
                remaining_value=merchant_contrib,
                related_order_id=related_order_id, related_session_id=related_session_id,
            ))

        # 3. 推荐商家贡献值 (8%)
        if referrer_merchant_id:
            ref_merchant_contrib = ContributionService.calculate_contribution(
                base_amount, settings.CONTRIB_REFERRAL_MERCHANT_RATIO
            )
            records.append(ContributionService._create_record(
                user_id=referrer_merchant_id, source=source, role=ContribRole.REFERRAL_MERCHANT,
                base_amount=base_amount, discount_amount=discount_amount,
                ratio=settings.CONTRIB_REFERRAL_MERCHANT_RATIO, contrib_value=ref_merchant_contrib,
                remaining_value=ref_merchant_contrib,
                related_order_id=related_order_id, related_session_id=related_session_id,
            ))

        # 4. 推荐消费者贡献值 (5%)
        if referrer_consumer_id:
            ref_consumer_contrib = ContributionService.calculate_contribution(
                base_amount, settings.CONTRIB_REFERRAL_CONSUMER_RATIO
            )
            records.append(ContributionService._create_record(
                user_id=referrer_consumer_id, source=source, role=ContribRole.REFERRAL_CONSUMER,
                base_amount=base_amount, discount_amount=discount_amount,
                ratio=settings.CONTRIB_REFERRAL_CONSUMER_RATIO, contrib_value=ref_consumer_contrib,
                remaining_value=ref_consumer_contrib,
                related_order_id=related_order_id, related_session_id=related_session_id,
            ))

        # 5. 代理贡献值 (7%) - 省/市/区县合计
        if agent_ids:
            agent_contrib = ContributionService.calculate_contribution(
                base_amount, settings.CONTRIB_AGENT_RATIO
            )
            # 按比例分配给省1%+市2%+区县4%
            for level, ratio_share in [("province", 1/7), ("city", 2/7), ("district", 4/7)]:
                agent_id = agent_ids.get(level)
                if agent_id:
                    share = agent_contrib * ratio_share
                    records.append(ContributionService._create_record(
                        user_id=agent_id, source=source, role=ContribRole.AGENT,
                        base_amount=base_amount, discount_amount=discount_amount,
                        ratio=settings.CONTRIB_AGENT_RATIO * ratio_share,
                        contrib_value=share, remaining_value=share,
                        related_order_id=related_order_id, related_session_id=related_session_id,
                    ))

        # 6. 平台贡献值 (10%)
        platform_contrib = ContributionService.calculate_contribution(
            base_amount, settings.CONTRIB_PLATFORM_RATIO
        )
        records.append(ContributionService._create_record(
            user_id=None, source=source, role=ContribRole.PLATFORM,
            base_amount=base_amount, discount_amount=discount_amount,
            ratio=settings.CONTRIB_PLATFORM_RATIO, contrib_value=platform_contrib,
            remaining_value=platform_contrib,
            related_order_id=related_order_id, related_session_id=related_session_id,
        ))

        # 写入数据库
        for record in records:
            db.add(record)
        await db.flush()

        return records

    @staticmethod
    def _create_record(
        user_id, source, role, base_amount, discount_amount, ratio, contrib_value, remaining_value,
        related_order_id=None, related_session_id=None,
    ) -> ContributionRecord:
        return ContributionRecord(
            user_id=user_id,
            source=source,
            role=role,
            base_amount=base_amount,
            discount_amount=discount_amount,
            ratio=ratio,
            contrib_value=contrib_value,
            remaining_value=remaining_value,
            daily_rate=settings.CONTRIB_DAILY_RATE_DEFAULT,
        )

    @staticmethod
    async def weekly_settle(db: AsyncSession) -> dict:
        """每周一贡献值递减兑换结算
        当周消费券 = 有效贡献值 × 日利率 × 7
        兑换后剩余贡献值继续参与下期
        """
        daily_rate = settings.CONTRIB_DAILY_RATE_DEFAULT
        now = datetime.utcnow()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)

        # 获取所有有剩余贡献值的用户
        result = await db.execute(
            select(ContributionRecord).where(
                and_(
                    ContributionRecord.remaining_value > 0,
                    ContributionRecord.user_id.isnot(None),
                )
            )
        )
        records = result.scalars().all()

        # 按用户分组计算
        user_settlements = {}
        for record in records:
            uid = record.user_id
            if uid not in user_settlements:
                user_settlements[uid] = {"total_remaining": 0, "records": []}
            user_settlements[uid]["total_remaining"] += record.remaining_value
            user_settlements[uid]["records"].append(record)

        settled_count = 0
        total_coupon_generated = 0.0

        for user_id, data in user_settlements.items():
            effective_contrib = data["total_remaining"]
            # 当周消费券 = 贡献值 × 日利率 × 7
            weekly_coupon = effective_contrib * daily_rate * 7

            # 更新用户消费券余额
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if user:
                old_coupon = user.coupon_balance
                user.coupon_balance += weekly_coupon
                db.add(UserWalletLog(
                    user_id=user_id, asset_type="coupon", change_type="income",
                    amount=weekly_coupon, balance_before=old_coupon,
                    balance_after=user.coupon_balance,
                    description=f"贡献值周度递减兑换消费券",
                ))

            # 记录周度结算
            settlement = ContribWeeklySettlement(
                user_id=user_id,
                week_start=week_start,
                week_end=week_end,
                effective_contrib=effective_contrib,
                daily_rate=daily_rate,
                weekly_coupon=weekly_coupon,
                remaining_contrib=effective_contrib,  # 贡献值不扣减, 继续参与下期
                settled_at=now,
            )
            db.add(settlement)

            # 更新各条贡献值记录的周兑换量
            for record in data["records"]:
                record.weekly_coupon_generated += weekly_coupon * (record.remaining_value / effective_contrib)

            settled_count += 1
            total_coupon_generated += weekly_coupon

        await db.flush()
        return {
            "settled_users": settled_count,
            "total_coupon_generated": total_coupon_generated,
            "daily_rate": daily_rate,
            "week_start": week_start.isoformat(),
        }

    @staticmethod
    async def get_user_contributions(db: AsyncSession, user_id: int) -> list:
        """获取用户贡献值记录"""
        result = await db.execute(
            select(ContributionRecord)
            .where(ContributionRecord.user_id == user_id)
            .order_by(ContributionRecord.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_total_network_contrib(db: AsyncSession) -> float:
        """获取全网总贡献值(用于分红计算)"""
        result = await db.execute(
            select(func.sum(ContributionRecord.remaining_value)).where(
                ContributionRecord.remaining_value > 0
            )
        )
        return result.scalar() or 0.0
