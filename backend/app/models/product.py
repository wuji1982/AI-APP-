"""
商品数据模型
包含: 商品分类(吃/喝/用/穿)、商品SKU、库存
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Index, Text
)
from sqlalchemy.orm import relationship
from app.database import Base


class ProductCategory(str, enum.Enum):
    """商品四大品类"""
    FOOD = "food"       # 吃
    DRINK = "drink"     # 喝
    USE = "use"         # 用
    WEAR = "wear"       # 穿


class ProductStatus(str, enum.Enum):
    """商品状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SOLD_OUT = "sold_out"


class Product(Base):
    """商品表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="商品名称")
    category = Column(Enum(ProductCategory), nullable=False, comment="商品品类")
    status = Column(Enum(ProductStatus), default=ProductStatus.DRAFT, comment="商品状态")
    description = Column(Text, comment="商品描述")
    cover_image = Column(String(500), comment="封面图URL")
    images = Column(String(2000), comment="商品图片JSON数组")

    # 价格体系
    original_price = Column(Float, nullable=False, comment="原价")
    selling_price = Column(Float, nullable=False, comment="售价")
    cost_price = Column(Float, nullable=True, comment="成本价")

    # 让利计算: 让利金额 = selling_price * GLOBAL_DISCOUNT_RATIO(20%)
    discount_amount = Column(Float, nullable=True, comment="让利金额(售价*20%)")

    # 库存
    stock = Column(Integer, default=0, comment="库存数量")
    sales_count = Column(Integer, default=0, comment="已售数量")

    # 门店关联（线下门店商品可选）
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True, comment="所属门店ID")

    # 排序与推荐
    sort_order = Column(Integer, default=0, comment="排序权重")
    is_recommended = Column(Boolean, default=False, comment="是否推荐")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    skus = relationship("ProductSKU", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

    __table_args__ = (
        Index("idx_product_category", "category"),
        Index("idx_product_status", "status"),
        Index("idx_product_store", "store_id"),
    )


class ProductSKU(Base):
    """商品SKU表"""
    __tablename__ = "product_skus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sku_name = Column(String(100), nullable=False, comment="规格名称")
    sku_code = Column(String(50), unique=True, comment="SKU编码")
    price = Column(Float, nullable=False, comment="SKU价格")
    stock = Column(Integer, default=0, comment="SKU库存")
    attributes = Column(String(500), comment="规格属性JSON")

    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="skus")


class Order(Base):
    """商城订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False, index=True, comment="订单编号")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True, comment="下单门店")

    total_amount = Column(Float, nullable=False, comment="订单总金额")
    coupon_deduct = Column(Float, default=0.0, comment="消费券抵扣金额")
    actual_amount = Column(Float, nullable=False, comment="实际支付金额")

    # 贡献值计算相关
    discount_amount = Column(Float, default=0.0, comment="让利金额")
    contrib_generated = Column(Float, default=0.0, comment="产生的贡献值总量")

    status = Column(String(20), default="pending", comment="订单状态: pending/paid/shipped/completed/refunded")
    address = Column(String(500), comment="收货地址")
    remark = Column(String(200), comment="订单备注")

    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """订单商品明细"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("product_skus.id"), nullable=True)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
