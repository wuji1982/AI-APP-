"""商品/商城API"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product, ProductCategory, ProductStatus
from app.schemas.main import ProductCreate, ProductInfo
from app.utils.auth import get_current_user_id

router = APIRouter()


@router.get("/list")
async def list_products(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Product).where(Product.status == ProductStatus.ACTIVE)
    if category:
        query = query.where(Product.category == category)

    count_q = select(func.count()).select_from(Product).where(Product.status == ProductStatus.ACTIVE)
    total = (await db.execute(count_q)).scalar()

    result = await db.execute(query.order_by(Product.sort_order.desc()).offset((page-1)*size).limit(size))
    products = result.scalars().all()
    return {"total": total, "page": page, "size": size, "items": products}


@router.get("/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        return {"code": 404, "message": "商品不存在"}
    return product
