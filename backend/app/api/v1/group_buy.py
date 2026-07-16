"""拼团API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.group_buy import GroupBuyLevel
from app.schemas.main import JoinGroupBuyRequest
from app.services.group_buy_service import GroupBuyService
from app.utils.auth import get_current_user_id

router = APIRouter()


@router.get("/sessions")
async def get_active_sessions(
    level: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取当前可参与的拼团场次"""
    level_enum = GroupBuyLevel(level) if level else None
    sessions = await GroupBuyService.get_active_sessions(db, level_enum)
    return {"items": sessions}


@router.post("/join")
async def join_group_buy(
    req: JoinGroupBuyRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """参与拼团"""
    try:
        result = await GroupBuyService.join_group_buy(db, user_id, req.session_id)
        return {"code": 0, "message": "参团成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders")
async def get_my_orders(
    page: int = 1,
    size: int = 20,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取我的拼团订单"""
    result = await GroupBuyService.get_user_orders(db, user_id, page, size)
    return result


@router.get("/sessions/{session_id}")
async def get_session_detail(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取拼团场次详情"""
    from sqlalchemy import select
    from app.models.group_buy import GroupBuySession
    result = await db.execute(select(GroupBuySession).where(GroupBuySession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="场次不存在")
    return session
