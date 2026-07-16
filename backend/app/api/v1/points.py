"""积分API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.main import PointsConvertRequest
from app.services.points_service import PointsService
from app.utils.auth import get_current_user_id

router = APIRouter()


@router.get("/pool")
async def get_pool_status(db: AsyncSession = Depends(get_db)):
    """获取积分池状态"""
    return await PointsService.get_pool_status(db)


@router.post("/convert")
async def convert_points_to_coupon(
    req: PointsConvertRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """积分兑换消费券"""
    try:
        result = await PointsService.convert_to_coupon(db, user_id, req.points_amount)
        return {"code": 0, "message": "兑换成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
