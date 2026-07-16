"""门店/团队API"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.store_service import StoreService
from app.utils.auth import get_current_user_id

router = APIRouter()


@router.get("/list")
async def get_store_list(
    province: Optional[str] = None,
    city: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取门店列表"""
    result = await StoreService.get_store_list(db, province, city, page=page, size=size)
    return result


@router.get("/ranking")
async def get_store_ranking(
    year_month: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取门店排名"""
    from datetime import datetime
    if not year_month:
        year_month = datetime.now().strftime("%Y-%m")
    ranking = await StoreService.get_store_ranking(db, year_month)
    return {"items": ranking, "year_month": year_month}


@router.get("/team")
async def get_my_team(
    level: int = Query(1, ge=1, le=4),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取我的团队成员"""
    members = await StoreService.get_team_members(db, user_id, level)
    return {"items": members, "level": level}
