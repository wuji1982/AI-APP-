"""
电商通用API - 购物车/地址/收藏/评价/Banner/足迹
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, and_
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import json

from app.database import get_db
from app.models.ecommerce import (
    CartItem, UserAddress, UserFavorite, ProductReview,
    Banner, Announcement, UserBrowseHistory
)
from app.models.product import Product, ProductStatus, ProductCategory
from app.services.sms_service import sms_service
from app.utils.auth import get_current_user_id

router = APIRouter()


# ========== 请求模型 ==========

class AddCartRequest(BaseModel):
    product_id: int
    sku_id: Optional[int] = None
    quantity: int = 1

class UpdateCartRequest(BaseModel):
    quantity: int

class AddressCreateRequest(BaseModel):
    receiver_name: str
    receiver_phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool = False

class ReviewCreateRequest(BaseModel):
    order_item_id: int
    rating: int
    content: str = ""
    images: List[str] = []
    is_anonymous: bool = False

class SendSMSRequest(BaseModel):
    phone: str
    scene: str = "login"  # login / register / pay_verify / reset_pwd

class VerifySMSRequest(BaseModel):
    phone: str
    code: str
    scene: str = "login"


# ========== 购物车 ==========

@router.get("/cart/list")
async def get_cart(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取购物车列表"""
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id).order_by(CartItem.created_at.desc())
    )
    items = result.scalars().all()

    cart_items = []
    for item in items:
        prod_result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = prod_result.scalar_one_or_none()
        cart_items.append({
            "id": item.id,
            "product_id": item.product_id,
            "sku_id": item.sku_id,
            "quantity": item.quantity,
            "selected": item.selected,
            "product_name": product.name if product else "已下架",
            "price": product.selling_price if product else 0,
            "cover_image": product.cover_image if product else "",
            "stock": product.stock if product else 0,
            "valid": product is not None and product.status == ProductStatus.ACTIVE,
        })

    return {"items": cart_items, "total": len(cart_items)}


@router.post("/cart/add")
async def add_to_cart(
    req: AddCartRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """添加商品到购物车"""
    # 检查商品是否存在
    prod_result = await db.execute(select(Product).where(Product.id == req.product_id))
    product = prod_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 检查是否已在购物车
    exist_result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == req.product_id)
    )
    existing = exist_result.scalar_one_or_none()

    if existing:
        existing.quantity += req.quantity
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_id=req.product_id,
            sku_id=req.sku_id,
            quantity=req.quantity
        )
        db.add(cart_item)

    await db.commit()
    return {"success": True, "message": "已加入购物车"}


@router.put("/cart/{item_id}")
async def update_cart_item(
    item_id: int,
    req: UpdateCartRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新购物车商品数量"""
    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="购物车项不存在")

    item.quantity = req.quantity
    await db.commit()
    return {"success": True}


@router.delete("/cart/{item_id}")
async def remove_cart_item(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除购物车商品"""
    await db.execute(
        delete(CartItem).where(CartItem.id == item_id, CartItem.user_id == user_id)
    )
    await db.commit()
    return {"success": True}


@router.post("/cart/select")
async def select_cart_items(
    item_ids: List[int],
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """选中/取消选中购物车商品"""
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id)
    )
    items = result.scalars().all()
    for item in items:
        item.selected = item.id in item_ids
    await db.commit()
    return {"success": True}


@router.post("/cart/select-all")
async def select_all_cart(
    selected: bool = True,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """全选/取消全选"""
    result = await db.execute(select(CartItem).where(CartItem.user_id == user_id))
    items = result.scalars().all()
    for item in items:
        item.selected = selected
    await db.commit()
    return {"success": True}


# ========== 收货地址 ==========

@router.get("/address/list")
async def get_addresses(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取收货地址列表"""
    result = await db.execute(
        select(UserAddress).where(UserAddress.user_id == user_id).order_by(UserAddress.is_default.desc())
    )
    addresses = result.scalars().all()
    return {"items": addresses, "total": len(addresses)}


@router.post("/address")
async def create_address(
    req: AddressCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """新增收货地址"""
    # 如果设为默认，取消其他默认
    if req.is_default:
        result = await db.execute(
            select(UserAddress).where(UserAddress.user_id == user_id, UserAddress.is_default == True)
        )
        for addr in result.scalars().all():
            addr.is_default = False

    address = UserAddress(
        user_id=user_id,
        **req.dict()
    )
    db.add(address)
    await db.commit()
    return {"success": True, "address_id": address.id}


@router.put("/address/{address_id}")
async def update_address(
    address_id: int,
    req: AddressCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """修改收货地址"""
    result = await db.execute(
        select(UserAddress).where(UserAddress.id == address_id, UserAddress.user_id == user_id)
    )
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    if req.is_default:
        existing = await db.execute(
            select(UserAddress).where(UserAddress.user_id == user_id, UserAddress.is_default == True)
        )
        for addr in existing.scalars().all():
            addr.is_default = False

    for field, value in req.dict().items():
        setattr(address, field, value)
    await db.commit()
    return {"success": True}


@router.delete("/address/{address_id}")
async def delete_address(
    address_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除收货地址"""
    await db.execute(
        delete(UserAddress).where(UserAddress.id == address_id, UserAddress.user_id == user_id)
    )
    await db.commit()
    return {"success": True}


@router.post("/address/{address_id}/default")
async def set_default_address(
    address_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """设为默认地址"""
    result = await db.execute(
        select(UserAddress).where(UserAddress.user_id == user_id, UserAddress.is_default == True)
    )
    for addr in result.scalars().all():
        addr.is_default = False

    target = await db.execute(
        select(UserAddress).where(UserAddress.id == address_id, UserAddress.user_id == user_id)
    )
    address = target.scalar_one_or_none()
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    address.is_default = True
    await db.commit()
    return {"success": True}


# ========== 商品搜索 ==========

@router.get("/product/search")
async def search_products(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = Query("default", regex="^(default|price_asc|price_desc|sales|newest)$"),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """商品搜索"""
    query = select(Product).where(Product.status == ProductStatus.ACTIVE)

    if keyword:
        query = query.where(Product.name.ilike(f"%{keyword}%"))
    if category:
        query = query.where(Product.category == ProductCategory(category))
    if min_price is not None:
        query = query.where(Product.selling_price >= min_price)
    if max_price is not None:
        query = query.where(Product.selling_price <= max_price)

    # 排序
    if sort_by == "price_asc":
        query = query.order_by(Product.selling_price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.selling_price.desc())
    elif sort_by == "sales":
        query = query.order_by(Product.sales_count.desc())
    elif sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.sort_order.desc(), Product.is_recommended.desc())

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    result = await db.execute(query.offset((page - 1) * size).limit(size))
    products = result.scalars().all()

    return {
        "items": [
            {
                "id": p.id, "name": p.name, "category": p.category.value,
                "cover_image": p.cover_image, "selling_price": p.selling_price,
                "original_price": p.original_price, "sales_count": p.sales_count,
                "is_recommended": p.is_recommended,
            }
            for p in products
        ],
        "total": total, "page": page, "size": size
    }


@router.get("/product/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """获取商品分类及数量"""
    categories = []
    for cat in ProductCategory:
        count_q = select(func.count()).select_from(Product).where(
            Product.status == ProductStatus.ACTIVE, Product.category == cat
        )
        count = (await db.execute(count_q)).scalar()
        categories.append({"code": cat.value, "name": {"food": "吃", "drink": "喝", "use": "用", "wear": "穿"}[cat.value], "count": count})
    return {"categories": categories}


@router.get("/product/recommended")
async def get_recommended_products(
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """推荐商品"""
    result = await db.execute(
        select(Product).where(
            Product.status == ProductStatus.ACTIVE, Product.is_recommended == True
        ).order_by(Product.sort_order.desc()).limit(size)
    )
    products = result.scalars().all()
    return {"items": products}


# ========== 收藏 ==========

@router.post("/favorite/{product_id}")
async def add_favorite(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """收藏商品"""
    existing = await db.execute(
        select(UserFavorite).where(UserFavorite.user_id == user_id, UserFavorite.product_id == product_id)
    )
    if existing.scalar_one_or_none():
        return {"success": True, "message": "已收藏"}

    fav = UserFavorite(user_id=user_id, product_id=product_id)
    db.add(fav)
    await db.commit()
    return {"success": True, "message": "收藏成功"}


@router.delete("/favorite/{product_id}")
async def remove_favorite(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """取消收藏"""
    await db.execute(
        delete(UserFavorite).where(UserFavorite.user_id == user_id, UserFavorite.product_id == product_id)
    )
    await db.commit()
    return {"success": True}


@router.get("/favorite/list")
async def get_favorites(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """我的收藏列表"""
    result = await db.execute(
        select(UserFavorite).where(UserFavorite.user_id == user_id).order_by(UserFavorite.created_at.desc()).offset((page-1)*size).limit(size)
    )
    favorites = result.scalars().all()

    items = []
    for fav in favorites:
        prod_result = await db.execute(select(Product).where(Product.id == fav.product_id))
        product = prod_result.scalar_one_or_none()
        if product:
            items.append({
                "id": fav.id, "product_id": product.id, "name": product.name,
                "price": product.selling_price, "cover_image": product.cover_image,
                "created_at": fav.created_at,
            })

    return {"items": items, "total": len(items)}


@router.get("/favorite/check/{product_id}")
async def check_favorite(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """检查是否已收藏"""
    result = await db.execute(
        select(UserFavorite).where(UserFavorite.user_id == user_id, UserFavorite.product_id == product_id)
    )
    return {"is_favorited": result.scalar_one_or_none() is not None}


# ========== 评价 ==========

@router.post("/review")
async def create_review(
    req: ReviewCreateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """提交商品评价"""
    from app.models.product import OrderItem
    result = await db.execute(
        select(OrderItem).where(OrderItem.id == req.order_item_id)
    )
    order_item = result.scalar_one_or_none()
    if not order_item:
        raise HTTPException(status_code=404, detail="订单商品不存在")

    # 检查是否已评价
    exist_review = await db.execute(
        select(ProductReview).where(ProductReview.order_item_id == req.order_item_id)
    )
    if exist_review.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该商品已评价")

    review = ProductReview(
        user_id=user_id,
        product_id=order_item.product_id,
        order_id=order_item.order_id,
        order_item_id=req.order_item_id,
        rating=req.rating,
        content=req.content,
        images=json.dumps(req.images) if req.images else None,
        is_anonymous=req.is_anonymous,
    )
    db.add(review)
    await db.commit()
    return {"success": True, "message": "评价成功"}


@router.get("/review/product/{product_id}")
async def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取商品评价列表"""
    from app.models.user import User
    result = await db.execute(
        select(ProductReview).where(ProductReview.product_id == product_id).order_by(ProductReview.created_at.desc()).offset((page-1)*size).limit(size)
    )
    reviews = result.scalars().all()

    items = []
    for review in reviews:
        user_result = await db.execute(select(User).where(User.id == review.user_id))
        user = user_result.scalar_one_or_none()
        items.append({
            "id": review.id,
            "rating": review.rating,
            "content": review.content,
            "images": json.loads(review.images) if review.images else [],
            "user_name": "匿名用户" if review.is_anonymous else (user.nickname if user else "用户"),
            "avatar": user.avatar_url if user and not review.is_anonymous else "",
            "created_at": review.created_at,
            "append_content": review.append_content,
            "merchant_reply": review.merchant_reply,
        })

    # 统计评分
    stats_q = select(func.avg(ProductReview.rating), func.count()).where(ProductReview.product_id == product_id)
    stats = (await db.execute(stats_q)).one()

    return {
        "items": items,
        "avg_rating": round(stats[0] or 0, 1),
        "total": stats[1],
    }


# ========== Banner/公告 ==========

@router.get("/banner/list")
async def get_banners(
    position: str = "home",
    db: AsyncSession = Depends(get_db)
):
    """获取Banner列表"""
    now = datetime.utcnow()
    result = await db.execute(
        select(Banner).where(
            Banner.position == position,
            Banner.is_active == True,
        ).order_by(Banner.sort_order.desc()).limit(10)
    )
    banners = result.scalars().all()
    return {"items": banners}


@router.get("/announcement/list")
async def get_announcements(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取系统公告"""
    result = await db.execute(
        select(Announcement).where(Announcement.is_active == True)
        .order_by(Announcement.is_top.desc(), Announcement.created_at.desc())
        .offset((page-1)*size).limit(size)
    )
    announcements = result.scalars().all()
    return {"items": announcements}


# ========== 浏览足迹 ==========

@router.post("/history/browse")
async def record_browse(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """记录浏览足迹"""
    history = UserBrowseHistory(user_id=user_id, product_id=product_id)
    db.add(history)
    await db.commit()
    return {"success": True}


@router.get("/history/browse")
async def get_browse_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取浏览足迹"""
    result = await db.execute(
        select(UserBrowseHistory).where(UserBrowseHistory.user_id == user_id)
        .order_by(UserBrowseHistory.created_at.desc()).offset((page-1)*size).limit(size)
    )
    histories = result.scalars().all()

    items = []
    for h in histories:
        prod_result = await db.execute(select(Product).where(Product.id == h.product_id))
        product = prod_result.scalar_one_or_none()
        if product:
            items.append({
                "product_id": product.id, "name": product.name,
                "price": product.selling_price, "cover_image": product.cover_image,
                "browsed_at": h.created_at,
            })

    return {"items": items}


@router.delete("/history/browse")
async def clear_browse_history(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """清空浏览足迹"""
    await db.execute(delete(UserBrowseHistory).where(UserBrowseHistory.user_id == user_id))
    await db.commit()
    return {"success": True}


# ========== 短信验证码 ==========

@router.post("/sms/send")
async def send_sms_code(req: SendSMSRequest):
    """发送短信验证码"""
    result = await sms_service.send_code(req.phone, req.scene)
    return result


@router.post("/sms/verify")
async def verify_sms_code(req: VerifySMSRequest):
    """验证短信验证码"""
    valid = await sms_service.verify_code(req.phone, req.code, req.scene)
    return {"valid": valid}
