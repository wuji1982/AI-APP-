"""
消费券管理服务
消费券不可提现, 仅用于商城消费抵扣
"""
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coupon import CouponRecord, CouponUsageLog
from app.models.user import User, UserWalletLog


class CouponService:
    """消费券服务"""

    @staticmethod
    async def use_coupon(
        db: AsyncSession,
        user_id: int,
        order_id: int,
        amount: float,
    ) -> dict:
        """使用消费券抵扣订单
        按先进先出原则使用消费券
        """
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one()

        if user.coupon_balance < amount:
            raise ValueError("消费券余额不足")

        # 获取可用消费券(按创建时间排序)
        result = await db.execute(
            select(CouponRecord).where(
                and_(
                    CouponRecord.user_id == user_id,
                    CouponRecord.remaining > 0,
                    CouponRecord.is_fully_used == 0,
                )
            ).order_by(CouponRecord.created_at)
        )
        coupons = result.scalars().all()

        remaining_amount = amount
        for coupon in coupons:
            if remaining_amount <= 0:
                break
            use_amount = min(remaining_amount, coupon.remaining)
            coupon.remaining -= use_amount
            coupon.used_amount += use_amount
            if coupon.remaining <= 0:
                coupon.is_fully_used = 1

            # 记录使用明细
            db.add(CouponUsageLog(
                user_id=user_id,
                coupon_record_id=coupon.id,
                order_id=order_id,
                amount=use_amount,
            ))
            remaining_amount -= use_amount

        # 更新用户消费券余额
        old_coupon = user.coupon_balance
        user.coupon_balance -= amount

        db.add(UserWalletLog(
            user_id=user_id, asset_type="coupon", change_type="expense",
            amount=-amount, balance_before=old_coupon, balance_after=user.coupon_balance,
            related_order_id=order_id,
            description=f"消费券抵扣订单",
        ))

        await db.flush()
        return {"used_amount": amount, "remaining_balance": user.coupon_balance}

    @staticmethod
    async def get_user_coupons(db: AsyncSession, user_id: int) -> list:
        """获取用户消费券列表"""
        result = await db.execute(
            select(CouponRecord)
            .where(CouponRecord.user_id == user_id)
            .order_by(CouponRecord.created_at.desc())
        )
        return result.scalars().all()
