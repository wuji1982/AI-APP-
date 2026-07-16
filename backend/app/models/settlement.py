"""
分润结算数据模型
线下四级分润: 省级1%, 市级2%, 区县4%, 门店8%, 推荐门店1%
平台收支分配(100%): 代理7%+门店8%+推荐门店1%+拼中商品10%+拼中贡献值20%+拼中积分20%+拼失败广告21%+拼失败推荐人3%+平台利润10%
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum, ForeignKey, Index
)
from app.database import Base


class SettlementType(str, enum.Enum):
    """结算类型"""
    GROUP_BUY_WIN = "group_buy_win"       # 拼团成功结算
    GROUP_BUY_LOSE = "group_buy_lose"     # 拼团失败结算
    ONLINE_ORDER = "online_order"         # 线上零售订单结算
    OFFLINE_ORDER = "offline_order"       # 线下门店消费结算
    STORE_DIVIDEND = "store_dividend"     # 门店阶梯分红


class SettlementStatus(str, enum.Enum):
    """结算状态"""
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"


class SettlementRecord(Base):
    """分润结算记录表
    每笔交易产生分润时, 按角色分别记录
    """
    __tablename__ = "settlement_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    settlement_type = Column(Enum(SettlementType), nullable=False, comment="结算类型")
    status = Column(Enum(SettlementStatus), default=SettlementStatus.PENDING)

    # 交易信息
    base_amount = Column(Float, nullable=False, comment="交易金额")
    total_discount = Column(Float, default=0.0, comment="总让利金额")

    # 分润接收方
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="接收方用户ID")
    recipient_type = Column(String(20), nullable=False, comment="接收方类型: province_agent/city_agent/district_agent/store/referral_store/consumer/platform")
    recipient_name = Column(String(100), nullable=True, comment="接收方名称")

    # 分润计算
    ratio = Column(Float, nullable=False, comment="分润比例")
    amount = Column(Float, nullable=False, comment="分润金额")

    # 关联
    related_order_id = Column(Integer, nullable=True)
    related_session_id = Column(Integer, nullable=True)

    settled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_settlement_type_status", "settlement_type", "status"),
        Index("idx_settlement_recipient", "recipient_id", "recipient_type"),
    )


class StoreMonthlyDividend(Base):
    """门店月度阶梯分红记录表
    阶梯一: 3-5万 → 0.5%
    阶梯二: 5-10万 → 0.5%
    阶梯三: 10-50万 → 0.5%
    阶梯四: 50万+ → 1%
    """
    __tablename__ = "store_monthly_dividends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    year_month = Column(String(7), nullable=False, comment="年月如2024-01")

    # 业绩统计
    monthly_new_performance = Column(Float, nullable=False, comment="当月新增业绩")
    tier = Column(Integer, nullable=False, comment="阶梯等级1-4")
    dividend_ratio = Column(Float, nullable=False, comment="分红比例")
    dividend_amount = Column(Float, nullable=False, comment="分红金额")

    # 排名
    rank = Column(Integer, nullable=True, comment="全网排名")

    settled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_store_div_store_month", "store_id", "year_month", unique=True),
    )


class PlatformDailyFinance(Base):
    """平台每日财务汇总表
    记录平台每日收支明细, 确保100%分配
    """
    __tablename__ = "platform_daily_finance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True, comment="统计日期")

    # 收入
    total_revenue = Column(Float, default=0.0, comment="平台总收益")
    platform_profit = Column(Float, default=0.0, comment="平台利润10%")

    # 支出明细
    agent_payout = Column(Float, default=0.0, comment="代理支出7%")
    store_payout = Column(Float, default=0.0, comment="门店分账8%")
    referral_store_payout = Column(Float, default=0.0, comment="推荐门店1%")
    win_product_payout = Column(Float, default=0.0, comment="拼中商品权益10%")
    win_contrib_payout = Column(Float, default=0.0, comment="拼中贡献值20%")
    win_points_payout = Column(Float, default=0.0, comment="拼中积分20%")
    lose_ad_payout = Column(Float, default=0.0, comment="拼失败广告补贴21%")
    lose_referral_payout = Column(Float, default=0.0, comment="拼失败推荐人补贴3%")

    total_payout = Column(Float, default=0.0, comment="总支出")
    balance_check = Column(Float, default=0.0, comment="收支平衡校验(应为0)")

    created_at = Column(DateTime, default=datetime.utcnow)
