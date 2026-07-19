"""
钱包服务
提供余额流水查询、充值、提现等功能
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserWalletLog


class WalletService:
    """钱包服务"""

    @staticmethod
    async def get_balance_logs(
        db: AsyncSession,
        user_id: int,
        asset_type: Optional[str] = None,
        change_type: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        """
        查询余额流水
        :param db: 数据库会话
        :param user_id: 用户ID
        :param asset_type: 资产类型筛选 (balance/contribution/points/coupon)
        :param change_type: 变动类型筛选 (income/expense/lock/unlock)
        :param page: 页码
        :param size: 每页数量
        :return: 流水列表
        """
        query = select(UserWalletLog).where(UserWalletLog.user_id == user_id)

        if asset_type:
            query = query.where(UserWalletLog.asset_type == asset_type)
        if change_type:
            query = query.where(UserWalletLog.change_type == change_type)

        # 总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页查询
        query = query.order_by(desc(UserWalletLog.created_at))
        query = query.offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        logs = result.scalars().all()

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [
                {
                    "id": log.id,
                    "asset_type": log.asset_type,
                    "change_type": log.change_type,
                    "amount": log.amount,
                    "balance_before": log.balance_before,
                    "balance_after": log.balance_after,
                    "description": log.description or "",
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ]
        }

    @staticmethod
    async def recharge(
        db: AsyncSession,
        user_id: int,
        amount: float,
        description: str = "余额充值",
    ) -> Dict[str, Any]:
        """
        充值余额
        :param db: 数据库会话
        :param user_id: 用户ID
        :param amount: 充值金额
        :param description: 充值说明
        :return: 充值结果
        """
        if amount <= 0:
            raise ValueError("充值金额必须大于0")

        # 获取用户
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("用户不存在")

        # 记录变动前余额
        balance_before = user.balance or 0

        # 更新余额
        user.balance = balance_before + amount
        user.updated_at = datetime.utcnow()

        # 写入流水
        wallet_log = UserWalletLog(
            user_id=user_id,
            asset_type="balance",
            change_type="income",
            amount=amount,
            balance_before=balance_before,
            balance_after=user.balance,
            description=description,
            created_at=datetime.utcnow(),
        )
        db.add(wallet_log)
        await db.commit()
        await db.refresh(user)

        return {
            "balance": user.balance,
            "recharged": amount,
            "message": f"充值成功 ¥{amount:.2f}"
        }

    @staticmethod
    async def withdraw(
        db: AsyncSession,
        user_id: int,
        amount: float,
        description: str = "余额提现",
    ) -> Dict[str, Any]:
        """
        提现余额
        :param db: 数据库会话
        :param user_id: 用户ID
        :param amount: 提现金额
        :param description: 提现说明
        :return: 提现结果
        """
        if amount <= 0:
            raise ValueError("提现金额必须大于0")

        # 获取用户
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("用户不存在")

        balance = user.balance or 0
        if balance < amount:
            raise ValueError(f"余额不足，当前余额 ¥{balance:.2f}")

        # 记录变动前余额
        balance_before = balance

        # 更新余额
        user.balance = balance_before - amount
        user.updated_at = datetime.utcnow()

        # 写入流水
        wallet_log = UserWalletLog(
            user_id=user_id,
            asset_type="balance",
            change_type="expense",
            amount=amount,
            balance_before=balance_before,
            balance_after=user.balance,
            description=description,
            created_at=datetime.utcnow(),
        )
        db.add(wallet_log)
        await db.commit()
        await db.refresh(user)

        return {
            "balance": user.balance,
            "withdrawn": amount,
            "message": f"提现成功 ¥{amount:.2f}"
        }

    @staticmethod
    async def get_wallet_summary(
        db: AsyncSession,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        获取钱包汇总信息（含今日收支）
        :param db: 数据库会话
        :param user_id: 用户ID
        :return: 钱包汇总
        """
        # 获取用户钱包信息
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("用户不存在")

        # 今日收入
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        income_query = select(func.coalesce(func.sum(UserWalletLog.amount), 0)).where(
            UserWalletLog.user_id == user_id,
            UserWalletLog.change_type == "income",
            UserWalletLog.created_at >= today_start,
        )
        income_result = await db.execute(income_query)
        today_income = income_result.scalar() or 0

        # 今日支出
        expense_query = select(func.coalesce(func.sum(UserWalletLog.amount), 0)).where(
            UserWalletLog.user_id == user_id,
            UserWalletLog.change_type == "expense",
            UserWalletLog.created_at >= today_start,
        )
        expense_result = await db.execute(expense_query)
        today_expense = expense_result.scalar() or 0

        return {
            "balance": user.balance or 0,
            "contribution_value": user.contribution_value or 0,
            "points": user.points or 0,
            "coupon_balance": user.coupon_balance or 0,
            "today_income": today_income,
            "today_expense": today_expense,
        }
