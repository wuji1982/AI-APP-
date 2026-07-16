"""
消费券数据模型
消费券不可提现, 仅用于商城消费抵扣
来源: 拼失败补贴、贡献值递减兑换、分红发放
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class CouponRecord(Base):
    """消费券记录表"""
    __tablename__ = "coupon_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 来源类型
    source_type = Column(String(30), nullable=False, comment="来源: group_lose_ad/group_lose_referral/contrib_exchange/dividend")
    amount = Column(Float, nullable=False, comment="消费券金额")

    # 使用记录
    used_amount = Column(Float, default=0.0, comment="已使用金额")
    remaining = Column(Float, nullable=False, comment="剩余可用金额")
    is_fully_used = Column(Integer, default=0, comment="是否已用完: 0否1是")

    # 关联
    related_order_id = Column(Integer, nullable=True)
    related_session_id = Column(Integer, nullable=True)
    related_contrib_id = Column(Integer, nullable=True, comment="关联贡献值记录ID")

    created_at = Column(DateTime, default=datetime.utcnow)
    expire_at = Column(DateTime, nullable=True, comment="过期时间")

    user = relationship("User", back_populates="coupon_records")

    __table_args__ = (
        Index("idx_coupon_user_source", "user_id", "source_type"),
    )


class CouponUsageLog(Base):
    """消费券使用明细表"""
    __tablename__ = "coupon_usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    coupon_record_id = Column(Integer, ForeignKey("coupon_records.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False, comment="使用金额")
    created_at = Column(DateTime, default=datetime.utcnow)
