"""
门店与团队管理服务
四级线下体系: 省→市→区县→门店
团队业绩统计、门店阶梯分红
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import Store, TeamMember, StoreMonthlyPerformance, StoreStatus
from app.models.user import User


class StoreService:
    """门店与团队管理服务"""

    @staticmethod
    async def create_store(
        db: AsyncSession,
        store_no: str,
        name: str,
        province: str,
        city: str,
        district: str,
        address: str,
        contact_name: str,
        contact_phone: str,
        province_agent_id: Optional[int] = None,
        city_agent_id: Optional[int] = None,
        district_agent_id: Optional[int] = None,
        referrer_id: Optional[int] = None,
    ) -> Store:
        """创建门店"""
        store = Store(
            store_no=store_no,
            name=name,
            province=province,
            city=city,
            district=district,
            address=address,
            contact_name=contact_name,
            contact_phone=contact_phone,
            province_agent_id=province_agent_id,
            city_agent_id=city_agent_id,
            district_agent_id=district_agent_id,
            referrer_id=referrer_id,
            status=StoreStatus.PENDING,
        )
        db.add(store)
        await db.flush()
        return store

    @staticmethod
    async def update_monthly_performance(
        db: AsyncSession,
        store_id: int,
        year_month: str,
        new_performance: float,
        new_members: int = 0,
        new_customers: int = 0,
        total_orders: int = 0,
    ) -> StoreMonthlyPerformance:
        """更新门店月度业绩"""
        result = await db.execute(
            select(StoreMonthlyPerformance).where(
                and_(
                    StoreMonthlyPerformance.store_id == store_id,
                    StoreMonthlyPerformance.year_month == year_month,
                )
            )
        )
        perf = result.scalar_one_or_none()

        if perf:
            perf.new_performance += new_performance
            perf.new_members += new_members
            perf.new_customers += new_customers
            perf.total_orders += total_orders
        else:
            perf = StoreMonthlyPerformance(
                store_id=store_id,
                year_month=year_month,
                new_performance=new_performance,
                new_members=new_members,
                new_customers=new_customers,
                total_orders=total_orders,
            )
            db.add(perf)

        # 同步更新门店总业绩
        store_result = await db.execute(select(Store).where(Store.id == store_id))
        store = store_result.scalar_one_or_none()
        if store:
            store.total_performance += new_performance
            store.monthly_performance += new_performance

        await db.flush()
        return perf

    @staticmethod
    async def get_team_members(
        db: AsyncSession,
        user_id: int,
        level: int = 1,
    ) -> list:
        """获取团队成员
        level: 1直推/2间推/3间间推/4间间间推
        """
        result = await db.execute(
            select(TeamMember).where(
                and_(
                    TeamMember.parent_id == user_id,
                    TeamMember.level == level,
                )
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_store_ranking(
        db: AsyncSession,
        year_month: str,
        limit: int = 100,
    ) -> list:
        """获取门店月度排名"""
        result = await db.execute(
            select(StoreMonthlyPerformance)
            .where(StoreMonthlyPerformance.year_month == year_month)
            .order_by(StoreMonthlyPerformance.new_performance.desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_store_list(
        db: AsyncSession,
        province: Optional[str] = None,
        city: Optional[str] = None,
        status: Optional[StoreStatus] = None,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        """获取门店列表"""
        query = select(Store)
        if province:
            query = query.where(Store.province == province)
        if city:
            query = query.where(Store.city == city)
        if status:
            query = query.where(Store.status == status)

        count_query = select(func.count()).select_from(Store)
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        result = await db.execute(query.offset((page - 1) * size).limit(size))
        stores = result.scalars().all()

        return {"total": total, "page": page, "size": size, "items": stores}
