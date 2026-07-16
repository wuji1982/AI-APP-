"""
订单管理服务
处理: 下单、取消、确认收货、订单查询
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product, ProductSKU, Order, OrderItem
from app.models.ecommerce import CartItem, UserAddress
from app.models.payment import PaymentRecord, PayStatus
from app.utils.security import generate_order_no

logger = logging.getLogger(__name__)


class OrderService:

    @staticmethod
    async def create_order(
        db: AsyncSession,
        user_id: int,
        address_id: int,
        cart_item_ids: Optional[List[int]] = None,
        remark: str = "",
        coupon_id: Optional[int] = None
    ) -> Dict:
        """
        从购物车创建订单
        1. 获取选中的购物车商品
        2. 校验库存和价格
        3. 计算金额(消费券抵扣)
        4. 创建订单+明细
        5. 扣减库存
        6. 清空购物车已下单商品
        """
        # 1. 获取收货地址
        addr_result = await db.execute(
            select(UserAddress).where(UserAddress.id == address_id, UserAddress.user_id == user_id)
        )
        address = addr_result.scalar_one_or_none()
        if not address:
            raise ValueError("收货地址不存在")

        address_str = f"{address.receiver_name} {address.receiver_phone} {address.province}{address.city}{address.district}{address.detail}"

        # 2. 获取购物车选中商品
        if cart_item_ids:
            cart_query = select(CartItem).where(
                CartItem.id.in_(cart_item_ids),
                CartItem.user_id == user_id,
                CartItem.selected == True
            )
        else:
            cart_query = select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.selected == True
            )
        cart_result = await db.execute(cart_query)
        cart_items = cart_result.scalars().all()

        if not cart_items:
            raise ValueError("购物车为空或没有选中商品")

        # 3. 校验商品并构建订单明细
        order_items = []
        total_amount = 0.0

        for cart_item in cart_items:
            # 查询商品信息
            prod_result = await db.execute(
                select(Product).where(Product.id == cart_item.product_id)
            )
            product = prod_result.scalar_one_or_none()
            if not product:
                raise ValueError(f"商品ID {cart_item.product_id} 不存在")

            if product.stock < cart_item.quantity:
                raise ValueError(f"商品 {product.name} 库存不足")

            unit_price = product.selling_price
            subtotal = unit_price * cart_item.quantity
            total_amount += subtotal

            order_items.append({
                "product_id": product.id,
                "sku_id": cart_item.sku_id,
                "product_name": product.name,
                "quantity": cart_item.quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })

        # 4. 消费券抵扣
        coupon_deduct = 0.0
        # TODO: 查询并核销消费券

        actual_amount = total_amount - coupon_deduct

        # 5. 创建订单
        order_no = generate_order_no("ORD")
        order = Order(
            order_no=order_no,
            user_id=user_id,
            total_amount=total_amount,
            coupon_deduct=coupon_deduct,
            actual_amount=actual_amount,
            address=address_str,
            remark=remark,
            status="pending",
        )
        db.add(order)
        await db.flush()

        # 6. 创建订单明细
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                **item_data
            )
            db.add(order_item)

        # 7. 扣减库存
        for item_data in order_items:
            prod_result = await db.execute(
                select(Product).where(Product.id == item_data["product_id"])
            )
            product = prod_result.scalar_one()
            product.stock -= item_data["quantity"]

        # 8. 清空已下单的购物车
        for cart_item in cart_items:
            await db.delete(cart_item)

        await db.commit()

        logger.info(f"订单创建成功: {order_no}, 用户: {user_id}, 金额: {actual_amount}")

        return {
            "order_id": order.id,
            "order_no": order_no,
            "total_amount": total_amount,
            "coupon_deduct": coupon_deduct,
            "actual_amount": actual_amount,
            "status": "pending",
        }

    @staticmethod
    async def get_user_orders(
        db: AsyncSession,
        user_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """获取用户订单列表"""
        query = select(Order).where(Order.user_id == user_id)
        if status:
            query = query.where(Order.status == status)
        query = query.order_by(Order.created_at.desc())

        # 总数
        count_q = select(func.count()).select_from(Order).where(Order.user_id == user_id)
        if status:
            count_q = count_q.where(Order.status == status)
        total = (await db.execute(count_q)).scalar()

        # 分页
        result = await db.execute(
            query.options(selectinload(Order.items)).offset((page - 1) * page_size).limit(page_size)
        )
        orders = result.scalars().all()

        return {
            "orders": [
                {
                    "id": o.id,
                    "order_no": o.order_no,
                    "total_amount": o.total_amount,
                    "actual_amount": o.actual_amount,
                    "status": o.status,
                    "address": o.address,
                    "created_at": o.created_at,
                    "paid_at": o.paid_at,
                    "items": [
                        {
                            "product_name": item.product_name,
                            "quantity": item.quantity,
                            "unit_price": item.unit_price,
                            "subtotal": item.subtotal,
                        }
                        for item in o.items
                    ]
                }
                for o in orders
            ],
            "total": total,
            "page": page,
        }

    @staticmethod
    async def get_order_detail(
        db: AsyncSession,
        order_id: int,
        user_id: int
    ) -> Optional[Dict]:
        """获取订单详情"""
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
            .options(selectinload(Order.items))
        )
        order = result.scalar_one_or_none()
        if not order:
            return None

        # 查询支付记录
        pay_result = await db.execute(
            select(PaymentRecord).where(PaymentRecord.order_id == order.id)
        )
        payment = pay_result.scalar_one_or_none()

        return {
            "id": order.id,
            "order_no": order.order_no,
            "total_amount": order.total_amount,
            "coupon_deduct": order.coupon_deduct,
            "actual_amount": order.actual_amount,
            "status": order.status,
            "address": order.address,
            "remark": order.remark,
            "created_at": order.created_at,
            "paid_at": order.paid_at,
            "completed_at": order.completed_at,
            "payment": {
                "out_trade_no": payment.out_trade_no,
                "pay_method": payment.pay_method.value if payment else None,
                "pay_status": payment.pay_status.value if payment else None,
            } if payment else None,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal,
                }
                for item in order.items
            ]
        }

    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        order_id: int,
        user_id: int
    ) -> Dict:
        """
        取消订单
        - 仅待支付/待发货状态可取消
        - 恢复库存
        """
        result = await db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
            .options(selectinload(Order.items))
        )
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("订单不存在")

        if order.status not in ("pending", "paid"):
            raise ValueError(f"订单状态 {order.status} 不可取消")

        # 恢复库存
        for item in order.items:
            prod_result = await db.execute(select(Product).where(Product.id == item.product_id))
            product = prod_result.scalar_one()
            product.stock += item.quantity

        order.status = "cancelled"
        await db.commit()

        logger.info(f"订单取消: {order.order_no}, 用户: {user_id}")
        return {"success": True, "message": "订单已取消"}

    @staticmethod
    async def confirm_receive(
        db: AsyncSession,
        order_id: int,
        user_id: int
    ) -> Dict:
        """确认收货"""
        result = await db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("订单不存在")

        if order.status != "shipped":
            raise ValueError("订单未发货，无法确认收货")

        order.status = "completed"
        order.completed_at = datetime.utcnow()
        await db.commit()

        # TODO: 触发贡献值/积分/消费券发放
        logger.info(f"确认收货: {order.order_no}")
        return {"success": True, "message": "已确认收货"}

    @staticmethod
    async def auto_cancel_expired(db: AsyncSession, minutes: int = 30):
        """自动取消超时未支付订单"""
        expire_time = datetime.utcnow() - timedelta(minutes=minutes)
        result = await db.execute(
            select(Order).where(
                Order.status == "pending",
                Order.created_at < expire_time
            ).options(selectinload(Order.items))
        )
        expired_orders = result.scalars().all()

        for order in expired_orders:
            # 恢复库存
            for item in order.items:
                prod_result = await db.execute(select(Product).where(Product.id == item.product_id))
                product = prod_result.scalar_one()
                product.stock += item.quantity
            order.status = "cancelled"

        await db.commit()
        return {"cancelled_count": len(expired_orders)}

    @staticmethod
    async def ship_order(
        db: AsyncSession,
        order_id: int,
        company_code: str,
        tracking_number: str
    ) -> Dict:
        """商家发货"""
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("订单不存在")

        if order.status != "paid":
            raise ValueError("订单未支付，无法发货")

        order.status = "shipped"
        await db.commit()

        # TODO: 创建物流记录、发送通知
        return {"success": True, "message": "发货成功"}
