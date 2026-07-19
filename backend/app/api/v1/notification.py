"""
通知API
提供通知列表查询、标记已读、删除、未读数统计等接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils.auth import get_current_user_id
from app.schemas.main import NotificationInfo, NotificationListResponse, UnreadCountResponse
from app.services import notification_service

router = APIRouter()


@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    type: Optional[str] = Query(None, description="通知类型过滤: order/group/system/activity"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取通知列表（分页，支持类型过滤）"""
    result = await notification_service.get_notifications(db, user_id, type, page, size)
    return NotificationListResponse(**result)


@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取各类型未读通知数"""
    counts = await notification_service.get_unread_count(db, user_id)
    return UnreadCountResponse(**counts)


@router.put("/notifications/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """标记单条通知为已读"""
    success = await notification_service.mark_as_read(db, notification_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="通知不存在")
    return {"message": "已标记已读"}


@router.put("/notifications/read-all")
async def mark_all_read(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """全部标记已读"""
    count = await notification_service.mark_all_read(db, user_id)
    return {"message": f"已标记 {count} 条通知为已读", "count": count}


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """删除单条通知"""
    success = await notification_service.delete_notification(db, notification_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="通知不存在")
    return {"message": "已删除"}
