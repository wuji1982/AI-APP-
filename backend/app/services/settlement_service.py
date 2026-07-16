"""
分润结算服务
线下四级分润: 省级1%, 市级2%, 区县4%, 门店8%, 推荐门店1%
平台100%分配模型自动对账
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.settlement import SettlementRecord, SettlementType, SettlementStatus, StoreMonthlyDividend, PlatformDailyFinance
from app.models.user import User, UserRole
from app.models.store import Store


class SettlementService:
    """分润结算服务"""

    @staticmethod
    async def settle_group_buy_win(
        db: AsyncSession,
        session_id: int,
        amount: float,
        winner_id: int,
        store_id: Optional[int] = None,
    ) -> list:
        """拼团成功分润结算
        按100%分配模型记录各方分润
        """
        records = []
        discount = amount * settings.GLOBAL_DISCOUNT_RATIO

        # 1. 代理支出 7% (省1%+市2%+区县4%)
        if store_id:
            store_result = await db.execute(select(Store).where(Store.id == store_id))
            store = store_result.scalar_one_or_none()
            if store:
                agent_splits = [
                    (store.province_agent_id, settings.PROFIT_PROVINCE_RATIO, "province_agent"),
                    (store.city_agent_id, settings.PROFIT_CITY_RATIO, "city_agent"),
                    (store.district_agent_id, settings.PROFIT_DISTRICT_RATIO, "district_agent"),
                ]
                for agent_id, ratio, rtype in agent_splits:
                    if agent_id:
                        record = SettlementService._create_settlement(
                            settlement_type=SettlementType.GROUP_BUY_WIN,
                            base_amount=amount, total_discount=discount,
                            recipient_id=agent_id, recipient_type=rtype,
                            ratio=ratio, amount=amount * ratio,
                            related_session_id=session_id,
                        )
                        records.append(record)
                        db.add(record)

        # 2. 门店分账 8%
        if store_id:
            record = SettlementService._create_settlement(
                settlement_type=SettlementType.GROUP_BUY_WIN,
                base_amount=amount, total_discount=discount,
                recipient_id=None, recipient_type="store",
                ratio=settings.PROFIT_STORE_RATIO, amount=amount * settings.PROFIT_STORE_RATIO,
                related_session_id=session_id,
            )
            records.append(record)
            db.add(record)

        # 3. 推荐门店 1%
        if store_id and store:
            store_result2 = await db.execute(select(Store).where(Store.id == store_id))
            store2 = store_result2.scalar_one_or_none()
            if store2 and store2.referrer_id:
                record = SettlementService._create_settlement(
                    settlement_type=SettlementType.GROUP_BUY_WIN,
                    base_amount=amount, total_discount=discount,
                    recipient_id=store2.referrer_id, recipient_type="referral_store",
                    ratio=settings.PROFIT_REFERRAL_STORE_RATIO,
                    amount=amount * settings.PROFIT_REFERRAL_STORE_RATIO,
                    related_session_id=session_id,
                )
                records.append(record)
                db.add(record)

        await db.flush()
        return records

    @staticmethod
    async def settle_store_monthly_dividend(db: AsyncSession, year_month: str) -> dict:
        """门店月度阶梯分红结算
        阶梯一: 3-5万 → 0.5%
        阶梯二: 5-10万 → 0.5%
        阶梯三: 10-50万 → 0.5%
        阶梯四: 50万+ → 1%
        """
        from app.models.store import StoreMonthlyPerformance

        # 获取所有门店当月业绩
        result = await db.execute(
            select(StoreMonthlyPerformance)
            .where(StoreMonthlyPerformance.year_month == year_month)
            .order_by(StoreMonthlyPerformance.new_performance.desc())
        )
        performances = result.scalars().all()

        settled = []
        rank = 1
        for perf in performances:
            amount = perf.new_performance
            tier, ratio = SettlementService._get_tier(amount)

            if tier > 0:
                dividend_amount = amount * ratio
                record = StoreMonthlyDividend(
                    store_id=perf.store_id,
                    year_month=year_month,
                    monthly_new_performance=amount,
                    tier=tier,
                    dividend_ratio=ratio,
                    dividend_amount=dividend_amount,
                    rank=rank,
                    settled_at=datetime.utcnow(),
                )
                db.add(record)
                settled.append(record)

                # 更新门店排名
                perf.rank = rank
                perf.tier = tier

            rank += 1

        await db.flush()
        return {"settled_count": len(settled), "year_month": year_month}

    @staticmethod
    def _get_tier(amount: float) -> tuple:
        """根据业绩确定阶梯等级和分红比例"""
        if amount >= settings.STORE_TIER4_MIN:
            return 4, settings.STORE_TIER4_DIVIDEND
        elif amount >= settings.STORE_TIER3_MIN:
            return 3, settings.STORE_TIER3_DIVIDEND
        elif amount >= settings.STORE_TIER2_MIN:
            return 2, settings.STORE_TIER2_DIVIDEND
        elif amount >= settings.STORE_TIER1_MIN:
            return 1, settings.STORE_TIER1_DIVIDEND
        return 0, 0.0

    @staticmethod
    def _create_settlement(
        settlement_type, base_amount, total_discount,
        recipient_id, recipient_type, ratio, amount,
        related_order_id=None, related_session_id=None,
    ) -> SettlementRecord:
        return SettlementRecord(
            settlement_type=settlement_type,
            status=SettlementStatus.PENDING,
            base_amount=base_amount,
            total_discount=total_discount,
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            ratio=ratio,
            amount=amount,
            related_order_id=related_order_id,
            related_session_id=related_session_id,
        )
