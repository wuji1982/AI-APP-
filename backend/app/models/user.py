"""
用户数据模型
包含: 普通用户、推荐人关系、代理(省/市/区县)、门店
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    """用户角色"""
    CONSUMER = "consumer"           # 普通消费者
    REFERRER = "referrer"           # 推荐消费者
    STORE = "store"                 # 线下门店
    REFERRAL_STORE = "referral_store"  # 推荐门店
    DISTRICT_AGENT = "district_agent"  # 区县代理
    CITY_AGENT = "city_agent"       # 市级代理
    PROVINCE_AGENT = "province_agent"  # 省级代理
    ADMIN = "admin"                 # 平台管理员


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False, index=True, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(50), comment="昵称")
    avatar_url = Column(String(500), comment="头像URL")
    role = Column(Enum(UserRole), default=UserRole.CONSUMER, comment="用户角色")
    is_active = Column(Boolean, default=True, comment="是否活跃")

    # 推荐关系
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="推荐人ID")

    # 钱包余额（四大资产）
    balance = Column(Float, default=0.0, comment="余额(拼团本金)")
    contribution_value = Column(Float, default=0.0, comment="贡献值")
    points = Column(Float, default=0.0, comment="增值积分")
    coupon_balance = Column(Float, default=0.0, comment="消费券余额")

    # 代理/门店关联
    agent_level = Column(String(20), nullable=True, comment="代理级别: province/city/district")
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True, comment="所属门店ID")

    # 代理区域信息
    province = Column(String(50), nullable=True, comment="省")
    city = Column(String(50), nullable=True, comment="市")
    district = Column(String(50), nullable=True, comment="区县")

    created_at = Column(DateTime, default=datetime.utcnow, comment="注册时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    referrer = relationship("User", remote_side=[id], backref="referrals")
    store = relationship("Store", back_populates="members", foreign_keys=[store_id])
    group_orders = relationship("GroupBuyOrder", back_populates="user", foreign_keys="GroupBuyOrder.user_id")
    contribution_records = relationship("ContributionRecord", back_populates="user")
    points_records = relationship("PointsRecord", back_populates="user")
    coupon_records = relationship("CouponRecord", back_populates="user")

    __table_args__ = (
        Index("idx_user_role", "role"),
        Index("idx_user_referrer", "referrer_id"),
        Index("idx_user_store", "store_id"),
    )


class UserWalletLog(Base):
    """用户钱包流水表（余额/贡献值/积分/消费券变动记录）"""
    __tablename__ = "user_wallet_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    asset_type = Column(String(20), nullable=False, comment="资产类型: balance/contribution/points/coupon")
    change_type = Column(String(20), nullable=False, comment="变动类型: income/expense/lock/unlock")
    amount = Column(Float, nullable=False, comment="变动金额")
    balance_before = Column(Float, nullable=False, comment="变动前余额")
    balance_after = Column(Float, nullable=False, comment="变动后余额")
    related_order_id = Column(Integer, nullable=True, comment="关联订单ID")
    related_session_id = Column(Integer, nullable=True, comment="关联拼团场次ID")
    description = Column(String(200), comment="变动说明")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_wallet_log_user_asset", "user_id", "asset_type"),
    )
