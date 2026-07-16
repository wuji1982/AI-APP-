"""
电商通用数据模型
包含: 购物车、收货地址、收藏、评价、Banner、足迹
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base


# ========== 购物车 ==========

class CartItem(Base):
    """购物车"""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("product_skus.id"), nullable=True)
    quantity = Column(Integer, nullable=False, default=1, comment="数量")
    selected = Column(Boolean, default=True, comment="是否选中")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_cart_user_product", "user_id", "product_id", unique=True),
    )


# ========== 收货地址 ==========

class UserAddress(Base):
    """收货地址"""
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_name = Column(String(50), nullable=False, comment="收件人")
    receiver_phone = Column(String(20), nullable=False, comment="手机号")
    province = Column(String(50), nullable=False, comment="省")
    city = Column(String(50), nullable=False, comment="市")
    district = Column(String(50), nullable=False, comment="区")
    detail = Column(String(200), nullable=False, comment="详细地址")
    is_default = Column(Boolean, default=False, comment="是否默认")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ========== 商品收藏 ==========

class UserFavorite(Base):
    """商品收藏"""
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_fav_user_product", "user_id", "product_id", unique=True),
    )


# ========== 商品评价 ==========

class ProductReview(Base):
    """商品评价"""
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=False)

    rating = Column(Integer, nullable=False, comment="评分1-5")
    content = Column(Text, comment="评价内容")
    images = Column(Text, comment="评价图片JSON数组")
    is_anonymous = Column(Boolean, default=False, comment="是否匿名")

    # 追评
    append_content = Column(Text, comment="追评内容")
    append_images = Column(Text, comment="追评图片JSON数组")
    append_at = Column(DateTime, comment="追评时间")

    # 商家回复
    merchant_reply = Column(Text, comment="商家回复")
    merchant_reply_at = Column(DateTime, comment="回复时间")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ========== Banner/公告 ==========

class Banner(Base):
    """首页轮播Banner"""
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False, comment="标题")
    image_url = Column(String(500), nullable=False, comment="图片URL")
    link_url = Column(String(500), comment="跳转链接")
    link_type = Column(String(20), default="product", comment="类型: product/category/url/none")
    position = Column(String(20), default="home", comment="位置: home/category/detail")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    created_at = Column(DateTime, server_default=func.now())


class Announcement(Base):
    """系统公告"""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    announce_type = Column(String(20), default="notice", comment="类型: notice/activity/update")
    is_top = Column(Boolean, default=False, comment="是否置顶")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now())


# ========== 浏览足迹 ==========

class UserBrowseHistory(Base):
    """浏览足迹"""
    __tablename__ = "user_browse_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_browse_user_time", "user_id", "created_at"),
    )
