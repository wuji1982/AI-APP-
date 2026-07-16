"""
拼团数据模型（核心业务模块）
包含: 拼团场次、拼团订单、拼团结果
法库啤酒专属拼团: 初级团/高级团/SVIP团
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class GroupBuyLevel(str, enum.Enum):
    """拼团板块级别"""
    JUNIOR = "junior"   # 初级团: 288x1=288元(1箱)
    SENIOR = "senior"   # 高级团: 288x5=1440元(5箱)
    SVIP = "svip"       # SVIP团: 288x40=11520元(40箱)


class SessionStatus(str, enum.Enum):
    """场次状态"""
    PENDING = "pending"       # 等待开团
    ACTIVE = "active"         # 进行中(未满31人)
    FULL = "full"             # 已满员(等待判定)
    COMPLETED = "completed"   # 已完成(已判定结果)
    CANCELLED = "cancelled"   # 已取消
    EXPIRED = "expired"       # 已过期


class OrderStatus(str, enum.Enum):
    """拼团订单状态"""
    PENDING = "pending"       # 待确认
    LOCKED = "locked"         # 已锁定(本金已扣)
    WON = "won"               # 拼中
    LOST = "lost"             # 拼失败
    REFUNDED = "refunded"     # 已退款(失败退回)
    CANCELLED = "cancelled"   # 已取消


class GroupBuySession(Base):
    """拼团场次表
    每日10:00-22:00, 每小时1场, 每场31人, 1人拼中30人失败
    """
    __tablename__ = "group_buy_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_no = Column(String(32), unique=True, nullable=False, index=True, comment="场次编号")

    # 板块类型
    level = Column(Enum(GroupBuyLevel), nullable=False, comment="拼团级别")
    price_per_box = Column(Float, default=288.0, comment="单箱定价288元")
    box_multiplier = Column(Integer, nullable=False, comment="箱数倍数(1/5/40)")
    total_price = Column(Float, nullable=False, comment="参团金额=288*倍数")

    # 人数规则
    total_players = Column(Integer, default=31, comment="每场31人")
    winner_count = Column(Integer, default=1, comment="拼中名额1人")
    loser_count = Column(Integer, default=30, comment="拼失败30人")
    current_players = Column(Integer, default=0, comment="当前参与人数")

    # 状态与时间
    status = Column(Enum(SessionStatus), default=SessionStatus.PENDING)
    start_time = Column(DateTime, nullable=False, comment="场次开始时间")
    end_time = Column(DateTime, nullable=False, comment="场次截止时间")
    settled_at = Column(DateTime, nullable=True, comment="结算时间")

    # 开团来源
    is_custom = Column(Boolean, default=False, comment="是否门店自定义开团")
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True, comment="自定义开团门店ID")

    # 拼中用户ID（结算后填入）
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="拼中用户ID")

    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    orders = relationship("GroupBuyOrder", back_populates="session")
    winner = relationship("User", foreign_keys=[winner_id])
    store = relationship("Store")

    __table_args__ = (
        Index("idx_session_level_status", "level", "status"),
        Index("idx_session_time", "start_time", "end_time"),
    )


class GroupBuyOrder(Base):
    """拼团订单表
    单ID单组最多参与5单, 单日无场次上限
    """
    __tablename__ = "group_buy_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("group_buy_sessions.id"), nullable=False, index=True)

    # 金额
    amount = Column(Float, nullable=False, comment="参团金额")

    # 状态
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    result = Column(String(10), nullable=True, comment="结果: won/lost")

    # 拼中权益记录
    product_benefit = Column(Float, default=0.0, comment="商品权益(10%)")
    contrib_benefit = Column(Float, default=0.0, comment="贡献值权益(20%)")
    points_benefit = Column(Float, default=0.0, comment="积分权益(20%)")

    # 拼失败补贴记录
    ad_subsidy = Column(Float, default=0.0, comment="广告补贴(0.7%)")
    referral_subsidy = Column(Float, default=0.0, comment="推荐人补贴(0.1%)")

    # 推荐人信息
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="推荐人ID")

    created_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)

    # 关系
    session = relationship("GroupBuySession", back_populates="orders")
    user = relationship("User", foreign_keys=[user_id], back_populates="group_orders")
    referrer = relationship("User", foreign_keys=[referrer_id])

    __table_args__ = (
        Index("idx_gb_order_user_session", "user_id", "session_id"),
        Index("idx_gb_order_status", "status"),
    )


class GroupBuyDailyStats(Base):
    """拼团每日统计表"""
    __tablename__ = "group_buy_daily_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True, comment="统计日期")

    # 各级别场次统计
    junior_sessions = Column(Integer, default=0, comment="初级团场次")
    senior_sessions = Column(Integer, default=0, comment="高级团场次")
    svip_sessions = Column(Integer, default=0, comment="SVIP团场次")
    total_sessions = Column(Integer, default=0, comment="总场次")

    # 交易量
    total_orders = Column(Integer, default=0, comment="总参团订单数")
    total_amount = Column(Float, default=0.0, comment="总交易金额")
    total_winners = Column(Integer, default=0, comment="拼中总人次")
    total_losers = Column(Integer, default=0, comment="拼失败总人次")

    # 补贴支出
    total_ad_subsidy = Column(Float, default=0.0, comment="广告补贴总支出")
    total_referral_subsidy = Column(Float, default=0.0, comment="推荐人补贴总支出")

    created_at = Column(DateTime, default=datetime.utcnow)
