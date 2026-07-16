"""
风控数据模型
AI智能风控Agent: 实时监控限购/异常操作/违规开团
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum, ForeignKey, Index, Boolean
)
from app.database import Base


class RiskLevel(str, enum.Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAction(str, enum.Enum):
    """风控动作"""
    ALLOW = "allow"         # 放行
    WARN = "warn"           # 警告
    BLOCK = "block"         # 拦截
    FREEZE = "freeze"       # 冻结账号


class RiskRuleType(str, enum.Enum):
    """风控规则类型"""
    DAILY_LIMIT = "daily_limit"           # 单日参与上限
    SESSION_LIMIT = "session_limit"       # 单场参与上限
    ORDER_LIMIT = "order_limit"           # 单ID单组最多5单
    ABNORMAL_BEHAVIOR = "abnormal"        # 异常操作检测
    ILLEGAL_GROUP = "illegal_group"       # 违规开团检测
    AMOUNT_ANOMALY = "amount_anomaly"     # 金额异常检测
    FREQUENCY_ANOMALY = "frequency"       # 频率异常检测


class RiskControlLog(Base):
    """风控日志表"""
    __tablename__ = "risk_control_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    rule_type = Column(Enum(RiskRuleType), nullable=False, comment="触发规则类型")
    risk_level = Column(Enum(RiskLevel), nullable=False, comment="风险等级")
    action = Column(Enum(RiskAction), nullable=False, comment="执行动作")

    # 详情
    description = Column(String(500), nullable=False, comment="风控描述")
    detail = Column(String(2000), comment="详细信息JSON")
    ip_address = Column(String(50), comment="IP地址")
    device_info = Column(String(200), comment="设备信息")

    # 处理状态
    is_resolved = Column(Boolean, default=False, comment="是否已处理")
    resolved_by = Column(String(50), nullable=True, comment="处理人")
    resolved_at = Column(DateTime, nullable=True)

    # 关联
    related_session_id = Column(Integer, nullable=True)
    related_order_id = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_risk_user_time", "user_id", "created_at"),
        Index("idx_risk_level", "risk_level"),
    )


class UserRiskScore(Base):
    """用户风险评分表"""
    __tablename__ = "user_risk_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    risk_score = Column(Float, default=0.0, comment="风险评分0-100")
    total_warnings = Column(Integer, default=0, comment="累计警告次数")
    total_blocks = Column(Integer, default=0, comment="累计拦截次数")
    is_blacklisted = Column(Boolean, default=False, comment="是否黑名单")
    last_risk_event = Column(DateTime, nullable=True, comment="最近风控事件时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
