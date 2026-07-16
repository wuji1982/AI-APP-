"""
支付与售后数据模型
包含: 支付记录、物流单、退款/退货
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
import enum

from app.database import Base


# ========== 枚举定义 ==========

class PayMethod(str, enum.Enum):
    alipay = "alipay"
    wechat = "wechat"
    wechat_app = "wechat_app"
    balance = "balance"       # 余额支付
    coupon = "coupon"         # 消费券支付


class PayStatus(str, enum.Enum):
    pending = "pending"       # 待支付
    paid = "paid"             # 已支付
    failed = "failed"         # 支付失败
    refunded = "refunded"     # 已退款
    partial_refund = "partial_refund"  # 部分退款


class RefundStatus(str, enum.Enum):
    pending = "pending"       # 待审核
    approved = "approved"     # 已同意
    rejected = "rejected"     # 已拒绝
    processing = "processing" # 退款中
    completed = "completed"   # 已完成
    failed = "failed"         # 退款失败


class LogisticsStatus(str, enum.Enum):
    pending = "pending"       # 待发货
    shipped = "shipped"       # 已发货
    in_transit = "in_transit" # 运输中
    delivered = "delivered"   # 已签收
    returned = "returned"     # 已退回


# ========== 支付记录 ==========

class PaymentRecord(Base):
    """支付记录"""
    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)

    # 支付信息
    out_trade_no = Column(String(64), unique=True, nullable=False, index=True, comment="商户订单号")
    trade_no = Column(String(100), comment="第三方交易号")
    pay_method = Column(SAEnum(PayMethod), nullable=False, comment="支付方式")
    pay_status = Column(SAEnum(PayStatus), default=PayStatus.pending, comment="支付状态")

    # 金额
    amount = Column(Float, nullable=False, comment="支付金额(元)")
    paid_amount = Column(Float, default=0.0, comment="实际支付金额")
    refunded_amount = Column(Float, default=0.0, comment="已退款金额")

    # 支付时间
    paid_at = Column(DateTime, comment="支付时间")
    expire_at = Column(DateTime, comment="过期时间")

    # 回调数据
    notify_data = Column(Text, comment="支付回调原始数据")

    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ========== 物流单 ==========

class LogisticsOrder(Base):
    """物流单"""
    __tablename__ = "logistics_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 物流信息
    company_code = Column(String(50), nullable=False, comment="快递公司编码")
    company_name = Column(String(100), comment="快递公司名称")
    tracking_number = Column(String(100), comment="快递单号")
    status = Column(SAEnum(LogisticsStatus), default=LogisticsStatus.pending, comment="物流状态")

    # 收发件人
    sender_name = Column(String(50), comment="寄件人")
    sender_phone = Column(String(20), comment="寄件人电话")
    sender_address = Column(Text, comment="寄件地址")

    receiver_name = Column(String(50), comment="收件人")
    receiver_phone = Column(String(20), comment="收件人电话")
    receiver_address = Column(Text, comment="收件地址")

    # 物流轨迹
    latest_trace = Column(Text, comment="最新物流信息")
    subscribed = Column(Boolean, default=False, comment="是否已订阅推送")

    # 时间
    shipped_at = Column(DateTime, comment="发货时间")
    delivered_at = Column(DateTime, comment="签收时间")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ========== 退款/退货 ==========

class RefundOrder(Base):
    """退款/退货单"""
    __tablename__ = "refund_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payment_records.id"), nullable=True)

    # 退款单号
    refund_no = Column(String(64), unique=True, nullable=False, index=True, comment="退款单号")
    out_refund_no = Column(String(64), comment="第三方退款单号")

    # 退款类型
    refund_type = Column(String(20), nullable=False, comment="退款类型: only_refund(仅退款)/return_refund(退货退款)")
    reason = Column(String(500), nullable=False, comment="退款原因")
    description = Column(Text, comment="详细说明")
    images = Column(Text, comment="凭证图片(JSON数组)")

    # 金额
    refund_amount = Column(Float, nullable=False, comment="申请退款金额")
    actual_refund_amount = Column(Float, default=0.0, comment="实际退款金额")

    # 退货物流
    return_tracking_number = Column(String(100), comment="退货快递单号")
    return_company = Column(String(50), comment="退货快递公司")

    # 状态
    status = Column(SAEnum(RefundStatus), default=RefundStatus.pending, comment="退款状态")
    reject_reason = Column(String(500), comment="拒绝原因")
    reviewed_by = Column(Integer, comment="审核人")
    reviewed_at = Column(DateTime, comment="审核时间")

    # 退款完成
    refunded_at = Column(DateTime, comment="退款完成时间")

    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ========== 售后工单 ==========

class AfterSaleTicket(Base):
    """售后工单"""
    __tablename__ = "after_sale_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    refund_id = Column(Integer, ForeignKey("refund_orders.id"), nullable=True)

    # 工单信息
    ticket_no = Column(String(64), unique=True, nullable=False, comment="工单编号")
    title = Column(String(200), nullable=False, comment="工单标题")
    content = Column(Text, nullable=False, comment="工单内容")
    priority = Column(String(20), default="normal", comment="优先级: low/normal/high/urgent")
    status = Column(String(20), default="open", comment="状态: open/processing/resolved/closed")

    # 处理人
    assigned_to = Column(Integer, comment="处理人ID")
    
    # 处理记录
    replies = Column(Text, comment="处理记录(JSON数组)")

    # 时间
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime, comment="解决时间")
