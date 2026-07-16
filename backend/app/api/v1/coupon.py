"""消费券API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.coupon_service import CouponService
from app.utils.auth import get_current_user_id

router = APIRouter()


@router.get("/my")
async def get_my_coupons(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取我的消费券列表"""
    coupons = await CouponService.get_user_coupons(db, user_id)
    return {"items": coupons}
