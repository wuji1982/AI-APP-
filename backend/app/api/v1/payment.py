"""
支付/物流/退款 API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import json

from app.database import get_db
from app.services.payment_service import payment_service
from app.services.logistics_service import logistics_service, EXPRESS_COMPANIES
from app.models.payment import PaymentRecord, LogisticsOrder, RefundOrder, PayMethod, PayStatus, RefundStatus
from app.models.product import Order
from app.utils.auth import get_current_user_id
from app.utils.security import generate_order_no

router = APIRouter()


# ========== 请求模型 ==========

class CreatePaymentRequest(BaseModel):
    order_id: int
    pay_method: str = "alipay"  # alipay / wechat / wechat_app

class RefundRequest(BaseModel):
    order_id: int
    refund_type: str = "only_refund"  # only_refund / return_refund
    reason: str
    description: str = ""
    images: List[str] = []

class ShipOrderRequest(BaseModel):
    order_id: int
    company_code: str
    tracking_number: str
    receiver_name: str = ""
    receiver_phone: str = ""
    receiver_address: str = ""


# ========== 支付接口 ==========

@router.post("/payment/create")
async def create_payment(
    request: CreatePaymentRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """创建支付订单"""
    # 查询订单
    result = await db.execute(select(Order).where(Order.id == request.order_id, Order.user_id == user_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 生成支付单号
    out_trade_no = generate_order_no("PAY")
    
    # 创建支付记录
    payment = PaymentRecord(
        user_id=user_id,
        order_id=order.id,
        out_trade_no=out_trade_no,
        pay_method=PayMethod(request.pay_method),
        amount=order.actual_amount,
        expire_at=datetime.now().replace(minute=datetime.now().minute + 30)
    )
    db.add(payment)
    await db.commit()

    # 调用第三方支付
    pay_result = await payment_service.create_payment(
        out_trade_no=out_trade_no,
        amount=order.actual_amount,
        subject=f"AI星木商城-订单{order.order_no}",
        pay_method=request.pay_method
    )

    return {
        "payment_id": payment.id,
        "out_trade_no": out_trade_no,
        **pay_result
    }


@router.get("/payment/status/{out_trade_no}")
async def get_payment_status(
    out_trade_no: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """查询支付状态"""
    result = await db.execute(
        select(PaymentRecord).where(
            PaymentRecord.out_trade_no == out_trade_no,
            PaymentRecord.user_id == user_id
        )
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在")

    return {
        "out_trade_no": out_trade_no,
        "status": payment.pay_status.value,
        "amount": payment.amount,
        "paid_amount": payment.paid_amount,
        "paid_at": payment.paid_at,
    }


@router.post("/payment/notify/alipay")
async def alipay_notify(request: Request, db: AsyncSession = Depends(get_db)):
    """支付宝异步回调"""
    form = await request.form()
    params = dict(form)
    
    out_trade_no = params.get("out_trade_no")
    trade_status = params.get("trade_status")
    trade_no = params.get("trade_no")

    # 查询支付记录
    result = await db.execute(
        select(PaymentRecord).where(PaymentRecord.out_trade_no == out_trade_no)
    )
    payment = result.scalar_one_or_none()
    
    if payment and trade_status == "TRADE_SUCCESS":
        payment.pay_status = PayStatus.paid
        payment.trade_no = trade_no
        payment.paid_amount = float(params.get("total_amount", 0))
        payment.paid_at = datetime.now()
        payment.notify_data = json.dumps(params)
        await db.commit()

    return "success"


@router.post("/payment/notify/wechat")
async def wechat_notify(request: Request, db: AsyncSession = Depends(get_db)):
    """微信支付异步回调"""
    body = await request.body()
    # TODO: 验签和解密
    data = json.loads(body)
    
    out_trade_no = data.get("out_trade_no")
    result = await db.execute(
        select(PaymentRecord).where(PaymentRecord.out_trade_no == out_trade_no)
    )
    payment = result.scalar_one_or_none()
    
    if payment and data.get("trade_state") == "SUCCESS":
        payment.pay_status = PayStatus.paid
        payment.trade_no = data.get("transaction_id")
        payment.paid_amount = data.get("amount", {}).get("total", 0) / 100
        payment.paid_at = datetime.now()
        payment.notify_data = body.decode()
        await db.commit()

    return {"code": "SUCCESS", "message": "成功"}


# ========== 物流接口 ==========

@router.get("/logistics/companies")
async def get_express_companies():
    """获取快递公司列表"""
    return {"companies": EXPRESS_COMPANIES}


@router.get("/logistics/track")
async def track_logistics(
    company: str = Query(..., description="快递公司编码"),
    number: str = Query(..., description="快递单号")
):
    """查询物流轨迹"""
    result = await logistics_service.query_track(company, number)
    return result


@router.get("/logistics/detect/{number}")
async def detect_express_company(number: str):
    """智能识别快递公司"""
    result = await logistics_service.auto_detect(number)
    return {"companies": result}


@router.get("/logistics/order/{order_id}")
async def get_order_logistics(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """查询订单物流"""
    result = await db.execute(
        select(LogisticsOrder).where(
            LogisticsOrder.order_id == order_id,
            LogisticsOrder.user_id == user_id
        )
    )
    logistics = result.scalar_one_or_none()
    if not logistics:
        return {"has_logistics": False}

    # 实时查询物流轨迹
    track_result = {}
    if logistics.tracking_number:
        track_result = await logistics_service.query_track(
            logistics.company_code,
            logistics.tracking_number
        )

    return {
        "has_logistics": True,
        "company": logistics.company_name,
        "tracking_number": logistics.tracking_number,
        "status": logistics.status.value,
        "latest_trace": logistics.latest_trace,
        "traces": track_result.get("traces", []),
        "shipped_at": logistics.shipped_at,
        "delivered_at": logistics.delivered_at,
    }


@router.post("/logistics/ship")
async def ship_order(
    request: ShipOrderRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """订单发货(商家/管理员)"""
    logistics = LogisticsOrder(
        order_id=request.order_id,
        user_id=user_id,
        company_code=request.company_code,
        tracking_number=request.tracking_number,
        status="shipped",
        receiver_name=request.receiver_name,
        receiver_phone=request.receiver_phone,
        receiver_address=request.receiver_address,
        shipped_at=datetime.now()
    )
    db.add(logistics)
    await db.commit()

    # 订阅物流推送
    await logistics_service.subscribe(request.company_code, request.tracking_number)

    return {"success": True, "message": "发货成功"}


# ========== 退款/退货接口 ==========

@router.post("/refund/apply")
async def apply_refund(
    request: RefundRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """申请退款/退货"""
    # 查询订单
    result = await db.execute(select(Order).where(Order.id == request.order_id, Order.user_id == user_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 生成退款单号
    refund_no = generate_order_no("REF")

    # 创建退款单
    refund = RefundOrder(
        user_id=user_id,
        order_id=order.id,
        refund_no=refund_no,
        refund_type=request.refund_type,
        reason=request.reason,
        description=request.description,
        images=json.dumps(request.images) if request.images else None,
        refund_amount=order.actual_amount,
    )
    db.add(refund)
    await db.commit()

    return {
        "success": True,
        "refund_no": refund_no,
        "message": "退款申请已提交，等待审核"
    }


@router.get("/refund/list")
async def list_refunds(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """查询退款列表"""
    query = select(RefundOrder).where(RefundOrder.user_id == user_id)
    if status:
        query = query.where(RefundOrder.status == status)
    query = query.order_by(RefundOrder.created_at.desc())
    
    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    refunds = result.scalars().all()

    return {
        "refunds": [
            {
                "id": r.id,
                "refund_no": r.refund_no,
                "order_id": r.order_id,
                "refund_type": r.refund_type,
                "reason": r.reason,
                "refund_amount": r.refund_amount,
                "status": r.status.value,
                "created_at": r.created_at,
            }
            for r in refunds
        ],
        "total": len(refunds)
    }


@router.post("/refund/{refund_id}/upload-tracking")
async def upload_return_tracking(
    refund_id: int,
    tracking_number: str = Query(...),
    company_code: str = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """上传退货物流单号"""
    result = await db.execute(
        select(RefundOrder).where(
            RefundOrder.id == refund_id,
            RefundOrder.user_id == user_id
        )
    )
    refund = result.scalar_one_or_none()
    if not refund:
        raise HTTPException(status_code=404, detail="退款单不存在")

    refund.return_tracking_number = tracking_number
    refund.return_company = company_code
    await db.commit()

    return {"success": True, "message": "退货物流已上传"}
