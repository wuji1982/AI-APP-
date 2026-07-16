"""贡献值API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.contribution_service import ContributionService
from app.utils.auth import get_current_user_id

router = APIRouter()


@router.get("/my")
async def get_my_contributions(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取我的贡献值记录"""
    records = await ContributionService.get_user_contributions(db, user_id)
    return {"items": records}


@router.get("/total")
async def get_total_network_contrib(db: AsyncSession = Depends(get_db)):
    """获取全网总贡献值"""
    total = await ContributionService.get_total_network_contrib(db)
    return {"total_network_contribution": total}
