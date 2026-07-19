"""
通知数据模型
包含: 系统通知、订单通知、拼团通知、活动通知
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Index, Text
from app.database import Base


class NotificationType(str, enum.Enum):
    """通知类型"""
    ORDER = "order"         # 订单通知
    GROUP = "group"         # 拼团通知
    SYSTEM = "system"       # 系统通知
    ACTIVITY = "activity"   # 活动通知


class Notification(Base):
    """通知记录表"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="接收用户ID")
    type = Column(Enum(NotificationType), nullable=False, comment="通知类型")
    title = Column(String(100), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    action_text = Column(String(50), nullable=True, comment="操作按钮文字")
    action_url = Column(String(200), nullable=True, comment="操作跳转路径")
    is_read = Column(Boolean, default=False, comment="是否已读")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        Index("idx_notif_user_type", "user_id", "type"),
        Index("idx_notif_user_read", "user_id", "is_read"),
        Index("idx_notif_created", "created_at"),
    )
