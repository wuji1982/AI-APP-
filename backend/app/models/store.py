"""
门店与团队数据模型
四级线下体系: 省→市→区县→门店
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class StoreStatus(str, enum.Enum):
    """门店状态"""
    PENDING = "pending"       # 待审核
    ACTIVE = "active"         # 正常营业
    SUSPENDED = "suspended"   # 暂停营业
    CLOSED = "closed"         # 已关闭


class Store(Base):
    """线下门店表"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_no = Column(String(20), unique=True, nullable=False, comment="门店编号")
    name = Column(String(100), nullable=False, comment="门店名称")
    status = Column(Enum(StoreStatus), default=StoreStatus.PENDING)

    # 所属区域
    province = Column(String(50), nullable=False, comment="省")
    city = Column(String(50), nullable=False, comment="市")
    district = Column(String(50), nullable=False, comment="区县")
    address = Column(String(200), comment="详细地址")

    # 代理归属
    province_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="所属省级代理")
    city_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="所属市级代理")
    district_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="所属区县代理")

    # 推荐人
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="推荐门店人")

    # 业绩统计
    total_performance = Column(Float, default=0.0, comment="累计总业绩")
    monthly_performance = Column(Float, default=0.0, comment="当月新增业绩")
    member_count = Column(Integer, default=0, comment="门店会员数")

    # 联系方式
    contact_name = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    members = relationship("User", back_populates="store", foreign_keys="User.store_id")

    __table_args__ = (
        Index("idx_store_status", "status"),
        Index("idx_store_area", "province", "city", "district"),
    )


class TeamMember(Base):
    """团队成员关系表(四级团队)"""
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="成员用户ID")
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="上级用户ID")
    level = Column(Integer, nullable=False, comment="层级: 1直推/2间推/3间间推/4间间间推")
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True, comment="所属门店")

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_team_parent", "parent_id", "level"),
    )


class StoreMonthlyPerformance(Base):
    """门店月度业绩统计表"""
    __tablename__ = "store_monthly_performance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    year_month = Column(String(7), nullable=False, comment="年月如2024-01")

    new_performance = Column(Float, default=0.0, comment="当月新增业绩")
    new_members = Column(Integer, default=0, comment="当月新增会员")
    new_customers = Column(Integer, default=0, comment="当月新增客户")
    total_orders = Column(Integer, default=0, comment="当月总订单数")

    rank = Column(Integer, nullable=True, comment="全网排名")
    tier = Column(Integer, nullable=True, comment="阶梯等级1-4")

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_store_perf_month", "store_id", "year_month", unique=True),
    )
