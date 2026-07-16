"""
积分增值系统服务
总发行量1200万, 20%利润值+20%通缩, 动态单价递增
积分仅可兑换消费券
"""
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.points import PointsPool, PointsRecord, PointsConvertRecord
from app.models.user import User, UserWalletLog


class PointsService:
    """积分增值服务"""

    @staticmethod
    async def _get_or_create_pool(db: AsyncSession) -> PointsPool:
        """获取或创建积分池(全局单例)"""
        result = await db.execute(select(PointsPool).where(PointsPool.id == 1))
        pool = result.scalar_one_or_none()
        if not pool:
            pool = PointsPool(id=1, total_supply=settings.POINTS_TOTAL_SUPPLY)
            db.add(pool)
            await db.flush()
        return pool

    @staticmethod
    async def earn_points(
        db: AsyncSession,
        user_id: int,
        consume_amount: float,
        related_order_id: int = None,
    ) -> dict:
        """消费获得积分 + 通缩处理
        每次消费: 新增20%利润值积分, 同时20%通缩
        动态单价 = 累计总金额 / 累计通缩数量
        """
        pool = await PointsService._get_or_create_pool(db)

        # 20%利润值 → 新增积分
        profit_points = consume_amount * settings.POINTS_PROFIT_RATIO
        # 20%通缩 → 减少积分
        deflation_points = profit_points * settings.POINTS_DEFLATION_RATIO
        # 净新增积分
        net_points = profit_points - deflation_points

        # 更新积分池
        pool.total_issued += profit_points
        pool.total_deflated += deflation_points

        # 计算新单价: 累计总金额 / 累计通缩数量
        if pool.total_deflated > 0:
            pool.current_unit_price = pool.total_issued / pool.total_deflated
        pool.updated_at = datetime.utcnow()

        # 更新用户积分
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one()
        old_points = user.points
        user.points += net_points

        # 记录积分变动
        record = PointsRecord(
            user_id=user_id,
            change_type="earn",
            points_amount=net_points,
            unit_price_at_time=pool.current_unit_price,
            total_value=net_points * pool.current_unit_price,
            deflation_amount=deflation_points,
            profit_amount=profit_points,
            related_order_id=related_order_id,
        )
        db.add(record)

        # 钱包流水
        db.add(UserWalletLog(
            user_id=user_id, asset_type="points", change_type="income",
            amount=net_points, balance_before=old_points, balance_after=user.points,
            related_order_id=related_order_id,
            description=f"消费获得积分(利润{profit_points:.2f}-通缩{deflation_points:.2f})",
        ))

        await db.flush()
        return {
            "earned_points": net_points,
            "profit_points": profit_points,
            "deflation_points": deflation_points,
            "current_unit_price": pool.current_unit_price,
            "total_user_points": user.points,
        }

    @staticmethod
    async def convert_to_coupon(
        db: AsyncSession,
        user_id: int,
        points_amount: float,
    ) -> dict:
        """积分兑换消费券
        按当前单价折算为消费券金额
        """
        pool = await PointsService._get_or_create_pool(db)

        # 检查用户积分余额
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one()
        if user.points < points_amount:
            raise ValueError("积分余额不足")

        # 检查积分池剩余
        remaining = pool.total_supply - pool.total_issued + pool.total_deflated
        if points_amount > remaining:
            raise ValueError("积分池余额不足")

        # 计算消费券金额
        coupon_amount = points_amount * pool.current_unit_price

        # 扣减用户积分
        old_points = user.points
        user.points -= points_amount

        # 增加消费券
        old_coupon = user.coupon_balance
        user.coupon_balance += coupon_amount

        # 更新池
        pool.total_converted += points_amount

        # 记录
        convert_record = PointsConvertRecord(
            user_id=user_id,
            points_amount=points_amount,
            unit_price=pool.current_unit_price,
            coupon_amount=coupon_amount,
        )
        db.add(convert_record)

        # 积分变动记录
        db.add(PointsRecord(
            user_id=user_id,
            change_type="convert",
            points_amount=-points_amount,
            unit_price_at_time=pool.current_unit_price,
            total_value=-coupon_amount,
        ))

        # 钱包流水
        db.add(UserWalletLog(
            user_id=user_id, asset_type="points", change_type="expense",
            amount=-points_amount, balance_before=old_points, balance_after=user.points,
            description=f"积分兑换消费券",
        ))
        db.add(UserWalletLog(
            user_id=user_id, asset_type="coupon", change_type="income",
            amount=coupon_amount, balance_before=old_coupon, balance_after=user.coupon_balance,
            description=f"积分兑换消费券获得",
        ))

        await db.flush()
        return {
            "points_spent": points_amount,
            "coupon_gained": coupon_amount,
            "unit_price": pool.current_unit_price,
            "remaining_points": user.points,
        }

    @staticmethod
    async def get_pool_status(db: AsyncSession) -> dict:
        """获取积分池状态"""
        pool = await PointsService._get_or_create_pool(db)
        return {
            "total_supply": pool.total_supply,
            "total_issued": pool.total_issued,
            "total_deflated": pool.total_deflated,
            "total_converted": pool.total_converted,
            "current_unit_price": pool.current_unit_price,
            "remaining": pool.total_supply - pool.total_issued + pool.total_deflated - pool.total_converted,
        }
