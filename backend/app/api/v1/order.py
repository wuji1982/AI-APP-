"""
订单管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel

from app.database import get_db
from app.services.order_service import OrderService
from app.utils.auth import get_current_user_id

router = APIRouter()


class CreateOrderRequest(BaseModel):
    address_id: int
    cart_item_ids: Optional[List[int]] = None
    remark: str = ""
    coupon_id: Optional[int] = None


class ShipRequest(BaseModel):
    company_code: str
    tracking_number: str


@router.post("/create")
async def create_order(
    req: CreateOrderRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建订单(从购物车下单)"""
    try:
        result = await OrderService.create_order(
            db=db,
            user_id=user_id,
            address_id=req.address_id,
            cart_item_ids=req.cart_item_ids,
            remark=req.remark,
            coupon_id=req.coupon_id
        )
        return {"code": 0, "message": "下单成功", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
async def get_orders(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取我的订单列表"""
    result = await OrderService.get_user_orders(db, user_id, status, page, size)
    return result


@router.get("/{order_id}")
async def get_order_detail(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取订单详情"""
    result = await OrderService.get_order_detail(db, order_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="订单不存在")
    return result


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """取消订单"""
    try:
        result = await OrderService.cancel_order(db, order_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/confirm")
async def confirm_receive(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """确认收货"""
    try:
        result = await OrderService.confirm_receive(db, order_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/ship")
async def ship_order(
    order_id: int,
    req: ShipRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """商家发货"""
    try:
        result = await OrderService.ship_order(db, order_id, req.company_code, req.tracking_number)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
