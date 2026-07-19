"""
通知服务
处理通知的创建、查询、标记已读、删除等操作
"""
import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType

logger = logging.getLogger(__name__)


async def create_notification(
    db: AsyncSession,
    user_id: int,
    type: NotificationType,
    title: str,
    content: str,
    action_text: Optional[str] = None,
    action_url: Optional[str] = None,
) -> Notification:
    """创建一条通知"""
    notif = Notification(
        user_id=user_id,
        type=type,
        title=title,
        content=content,
        action_text=action_text,
        action_url=action_url,
    )
    db.add(notif)
    await db.flush()
    logger.info(f"[通知] 创建通知: user={user_id}, type={type.value}, title={title}")
    return notif


async def get_notifications(
    db: AsyncSession,
    user_id: int,
    type_filter: Optional[str] = None,
    page: int = 1,
    size: int = 20,
) -> dict:
    """分页查询通知列表"""
    query = select(Notification).where(Notification.user_id == user_id)

    if type_filter and type_filter != "all":
        try:
            notif_type = NotificationType(type_filter)
            query = query.where(Notification.type == notif_type)
        except ValueError:
            pass

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页数据
    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"total": total, "page": page, "size": size, "items": items}


async def mark_as_read(db: AsyncSession, notification_id: int, user_id: int) -> bool:
    """标记单条通知为已读"""
    stmt = (
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    return result.rowcount > 0


async def mark_all_read(db: AsyncSession, user_id: int) -> int:
    """标记所有通知为已读，返回更新数量"""
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    return result.rowcount


async def delete_notification(db: AsyncSession, notification_id: int, user_id: int) -> bool:
    """删除单条通知"""
    stmt = (
        delete(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.rowcount > 0


async def get_unread_count(db: AsyncSession, user_id: int) -> dict:
    """获取各类型未读通知数"""
    query = (
        select(Notification.type, func.count().label("count"))
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .group_by(Notification.type)
    )
    result = await db.execute(query)
    rows = result.all()

    counts = {"order": 0, "group": 0, "system": 0, "activity": 0}
    total = 0
    for row_type, row_count in rows:
        key = row_type.value if hasattr(row_type, "value") else str(row_type)
        counts[key] = row_count
        total += row_count

    counts["total"] = total
    return counts


async def batch_create_notifications(
    db: AsyncSession,
    user_ids: List[int],
    type: NotificationType,
    title: str,
    content: str,
    action_text: Optional[str] = None,
    action_url: Optional[str] = None,
) -> int:
    """批量创建通知（给多个用户）"""
    count = 0
    for uid in user_ids:
        await create_notification(db, uid, type, title, content, action_text, action_url)
        count += 1
    logger.info(f"[通知] 批量创建通知: {count}条, type={type.value}, title={title}")
    return count
