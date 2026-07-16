"""
积分增值系统数据模型
总发行量恒定1200万, 20%利润值+20%通缩, 动态单价递增
积分仅可兑换消费券, 不可直接消费
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class PointsPool(Base):
    """积分总池表(全局单例)
    总发行量1200万, 永不超发
    """
    __tablename__ = "points_pool"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_supply = Column(Float, default=12_000_000, comment="总发行量1200万")
    total_issued = Column(Float, default=0.0, comment="已发放积分总量")
    total_deflated = Column(Float, default=0.0, comment="已通缩积分总量")
    total_converted = Column(Float, default=0.0, comment="已兑换消费券积分总量")
    current_unit_price = Column(Float, default=1.0, comment="当前积分单价")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PointsRecord(Base):
    """积分变动记录表
    每次消费: 新增20%利润值积分, 同时20%通缩
    动态单价 = 累计总金额 / 累计通缩数量
    """
    __tablename__ = "points_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 变动类型
    change_type = Column(String(20), nullable=False, comment="类型: earn/deflate/convert")
    points_amount = Column(Float, nullable=False, comment="积分变动数量")
    unit_price_at_time = Column(Float, nullable=False, comment="当时积分单价")
    total_value = Column(Float, nullable=False, comment="对应金额=积分*单价")

    # 通缩相关
    deflation_amount = Column(Float, default=0.0, comment="本次通缩积分数量")
    profit_amount = Column(Float, default=0.0, comment="本次新增利润值积分")

    # 关联
    related_order_id = Column(Integer, nullable=True)
    related_session_id = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="points_records")

    __table_args__ = (
        Index("idx_points_user_type", "user_id", "change_type"),
    )


class PointsConvertRecord(Base):
    """积分兑换消费券记录表
    积分 → 消费券, 按当前单价折算
    """
    __tablename__ = "points_convert_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    points_amount = Column(Float, nullable=False, comment="兑换积分数量")
    unit_price = Column(Float, nullable=False, comment="兑换时单价")
    coupon_amount = Column(Float, nullable=False, comment="获得消费券金额")

    created_at = Column(DateTime, default=datetime.utcnow)
