"""
贡献值数据模型
全网统一贡献值核算: 线上零售消费、拼团成功让利、线下门店消费 三大场景通用
公式: 各方贡献值 = 让利金额 × 分配比例 × 10
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class ContribSource(str, enum.Enum):
    """贡献值来源场景"""
    ONLINE_RETAIL = "online_retail"       # 线上零售消费
    GROUP_BUY_WIN = "group_buy_win"       # 拼团成功让利
    OFFLINE_STORE = "offline_store"       # 线下门店消费


class ContribRole(str, enum.Enum):
    """贡献值归属角色"""
    CONSUMER = "consumer"                 # 消费者 50%
    MERCHANT = "merchant"                 # 合作商家/门店 20%
    REFERRAL_MERCHANT = "referral_merchant"  # 推荐商家 8%
    REFERRAL_CONSUMER = "referral_consumer"  # 推荐消费者 5%
    AGENT = "agent"                       # 省/市/区县代理 7%
    PLATFORM = "platform"                 # 平台利润 10%


class ContributionRecord(Base):
    """贡献值记录表
    每笔交易产生贡献值时, 按6个角色分别记录
    """
    __tablename__ = "contribution_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    source = Column(Enum(ContribSource), nullable=False, comment="来源场景")
    role = Column(Enum(ContribRole), nullable=False, comment="归属角色")

    # 计算明细
    base_amount = Column(Float, nullable=False, comment="消费/交易金额")
    discount_amount = Column(Float, nullable=False, comment="让利金额(金额*20%)")
    ratio = Column(Float, nullable=False, comment="分配比例(如0.50)")
    contrib_value = Column(Float, nullable=False, comment="贡献值=让利金额*比例*10")

    # 递减兑换相关
    remaining_value = Column(Float, nullable=True, comment="剩余可兑换贡献值")
    daily_rate = Column(Float, default=0.0005, comment="当期日利率")
    weekly_coupon_generated = Column(Float, default=0.0, comment="本周已兑换消费券")

    # 分红相关
    is_dividend_settled = Column(Integer, default=0, comment="是否已参与本期分红: 0否1是")
    last_dividend_date = Column(DateTime, nullable=True, comment="上次分红日期")

    # 关联
    related_order_id = Column(Integer, nullable=True, comment="关联订单ID")
    related_session_id = Column(Integer, nullable=True, comment="关联拼团场次ID")

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="contribution_records")

    __table_args__ = (
        Index("idx_contrib_user_source", "user_id", "source"),
        Index("idx_contrib_role", "role"),
    )


class ContribWeeklySettlement(Base):
    """贡献值每周结算表
    每周一统一结算: 当周消费券 = 有效贡献值 × 日利率 × 7
    """
    __tablename__ = "contrib_weekly_settlements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    week_start = Column(DateTime, nullable=False, comment="本周起始日期(周一)")
    week_end = Column(DateTime, nullable=False, comment="本周结束日期(周日)")

    # 核算数据
    effective_contrib = Column(Float, nullable=False, comment="当期有效贡献值")
    daily_rate = Column(Float, nullable=False, comment="适用日利率")
    weekly_coupon = Column(Float, nullable=False, comment="本周兑换消费券=贡献值*日利率*7")

    # 分红数据
    total_network_contrib = Column(Float, nullable=True, comment="全网总贡献值")
    platform_pool = Column(Float, nullable=True, comment="平台20%收益池金额")
    dividend_coupon = Column(Float, default=0.0, comment="个人分红消费券")

    # 迭代后剩余贡献值
    remaining_contrib = Column(Float, nullable=False, comment="结算后剩余贡献值")

    settled_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_weekly_user_week", "user_id", "week_start", unique=True),
    )


class GlobalContribStats(Base):
    """全网贡献值统计表(用于分红计算)"""
    __tablename__ = "global_contrib_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True, comment="统计日期")
    total_contrib = Column(Float, default=0.0, comment="全网总贡献值")
    platform_revenue = Column(Float, default=0.0, comment="平台总收益")
    platform_pool_20 = Column(Float, default=0.0, comment="平台20%收益池")
    total_dividend_paid = Column(Float, default=0.0, comment="已发放分红总额")

    created_at = Column(DateTime, default=datetime.utcnow)
