"""
拼团核心业务服务
实现拼团全流程: 开团→参团→满员判定→结果结算→权益发放
"""
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.group_buy import GroupBuySession, GroupBuyOrder, GroupBuyLevel, SessionStatus, OrderStatus
from app.models.user import User, UserWalletLog


class GroupBuyService:
    """拼团服务"""

    # ========== 板块价格配置 ==========
    LEVEL_CONFIG = {
        GroupBuyLevel.JUNIOR: {"multiplier": 1, "price": 288.0 * 1},
        GroupBuyLevel.SENIOR: {"multiplier": 5, "price": 288.0 * 5},
        GroupBuyLevel.SVIP:   {"multiplier": 40, "price": 288.0 * 40},
    }

    @staticmethod
    async def create_daily_sessions(db: AsyncSession, date: datetime) -> List[GroupBuySession]:
        """创建每日固定场次
        每日10:00-22:00, 每小时1场, 三大板块并行
        """
        sessions = []
        for hour in range(settings.GROUP_BUY_START_HOUR, settings.GROUP_BUY_END_HOUR + 1):
            start_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)

            # 每个小时创建3个场次(初级/高级/SVIP)
            for level in [GroupBuyLevel.JUNIOR, GroupBuyLevel.SENIOR, GroupBuyLevel.SVIP]:
                config = GroupBuyService.LEVEL_CONFIG[level]
                session = GroupBuySession(
                    session_no=f"GB{date.strftime('%Y%m%d')}{hour:02d}{level.value[0].upper()}{uuid.uuid4().hex[:4]}",
                    level=level,
                    price_per_box=settings.BEER_PRICE_PER_BOX,
                    box_multiplier=config["multiplier"],
                    total_price=config["price"],
                    total_players=settings.GROUP_BUY_TOTAL_PLAYERS,
                    winner_count=settings.GROUP_BUY_WINNERS,
                    loser_count=settings.GROUP_BUY_LOSERS,
                    current_players=0,
                    status=SessionStatus.PENDING,
                    start_time=start_time,
                    end_time=end_time,
                    is_custom=False,
                )
                db.add(session)
                sessions.append(session)

        await db.flush()
        return sessions

    @staticmethod
    async def create_custom_session(
        db: AsyncSession,
        store_id: int,
        level: GroupBuyLevel,
        start_time: datetime,
    ) -> GroupBuySession:
        """门店自定义开团
        线下门店可跟随平台固定场次或自主发起自定义开团
        """
        config = GroupBuyService.LEVEL_CONFIG[level]
        session = GroupBuySession(
            session_no=f"GB{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}",
            level=level,
            price_per_box=settings.BEER_PRICE_PER_BOX,
            box_multiplier=config["multiplier"],
            total_price=config["price"],
            total_players=settings.GROUP_BUY_TOTAL_PLAYERS,
            winner_count=settings.GROUP_BUY_WINNERS,
            loser_count=settings.GROUP_BUY_LOSERS,
            current_players=0,
            status=SessionStatus.PENDING,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            is_custom=True,
            store_id=store_id,
        )
        db.add(session)
        await db.flush()
        return session

    @staticmethod
    async def join_group_buy(
        db: AsyncSession,
        user_id: int,
        session_id: int,
    ) -> dict:
        """用户参与拼团
        规则:
        - 单ID单组最多参与5单
        - 余额充足(扣除参团本金)
        - 场次未满(当前人数<31)
        """
        # 1. 获取场次信息
        result = await db.execute(
            select(GroupBuySession).where(GroupBuySession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError("拼团场次不存在")
        if session.status not in [SessionStatus.PENDING, SessionStatus.ACTIVE]:
            raise ValueError("该场次已截止参与")
        if session.current_players >= session.total_players:
            raise ValueError("该场次已满员")

        # 2. 检查用户单组参与次数(最多5单)
        result = await db.execute(
            select(func.count()).select_from(GroupBuyOrder).where(
                and_(
                    GroupBuyOrder.user_id == user_id,
                    GroupBuyOrder.session_id == session_id,
                    GroupBuyOrder.status.in_([OrderStatus.PENDING, OrderStatus.LOCKED]),
                )
            )
        )
        user_order_count = result.scalar()
        if user_order_count >= settings.GROUP_BUY_MAX_ORDERS_PER_USER:
            raise ValueError(f"单ID单组最多参与{settings.GROUP_BUY_MAX_ORDERS_PER_USER}单")

        # 3. 检查用户余额
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("用户不存在")
        if user.balance < session.total_price:
            raise ValueError("余额不足, 请先充值")

        # 4. 扣除本金(锁定)
        old_balance = user.balance
        user.balance -= session.total_price
        wallet_log = UserWalletLog(
            user_id=user_id,
            asset_type="balance",
            change_type="lock",
            amount=session.total_price,
            balance_before=old_balance,
            balance_after=user.balance,
            related_session_id=session_id,
            description=f"拼团参团锁定本金-{session.level.value}",
        )
        db.add(wallet_log)

        # 5. 创建拼团订单
        order = GroupBuyOrder(
            order_no=f"GO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}",
            user_id=user_id,
            session_id=session_id,
            amount=session.total_price,
            status=OrderStatus.LOCKED,
            referrer_id=user.referrer_id,
        )
        db.add(order)

        # 6. 更新场次人数
        session.current_players += 1
        if session.status == SessionStatus.PENDING:
            session.status = SessionStatus.ACTIVE

        # 7. 检查是否满员
        if session.current_players >= session.total_players:
            session.status = SessionStatus.FULL

        await db.flush()
        return {
            "order_id": order.id,
            "order_no": order.order_no,
            "session_id": session_id,
            "amount": session.total_price,
            "remaining_balance": user.balance,
            "session_full": session.status == SessionStatus.FULL,
        }

    @staticmethod
    async def settle_session(db: AsyncSession, session_id: int) -> dict:
        """拼团场次结算
        满31人后自动判定: 1人拼中, 30人拼失败
        拼中: 商品权益10% + 贡献值20% + 积分20%
        拼失败: 本金退回 + 广告补贴0.7% + 推荐人补贴0.1%
        """
        # 获取场次
        result = await db.execute(
            select(GroupBuySession).where(GroupBuySession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session or session.status != SessionStatus.FULL:
            raise ValueError("场次状态异常, 无法结算")

        # 获取所有订单
        result = await db.execute(
            select(GroupBuyOrder).where(
                GroupBuyOrder.session_id == session_id,
                GroupBuyOrder.status == OrderStatus.LOCKED,
            )
        )
        orders = result.scalars().all()
        if len(orders) != session.total_players:
            raise ValueError(f"订单数量不匹配: 期望{session.total_players}, 实际{len(orders)}")

        # 随机抽取1人拼中
        winner_order = random.choice(orders)
        loser_orders = [o for o in orders if o.id != winner_order.id]

        # ========== 处理拼中用户 ==========
        winner_amount = session.total_price
        winner_user_result = await db.execute(select(User).where(User.id == winner_order.user_id))
        winner_user = winner_user_result.scalar_one()

        # 本金不退回(用于购买啤酒)
        # 商品权益: 金额 * 10%
        product_benefit = winner_amount * settings.WIN_PRODUCT_RATIO
        # 贡献值权益: 金额 * 20%
        contrib_benefit = winner_amount * settings.WIN_CONTRIB_RATIO
        # 积分权益: 金额 * 20%
        points_benefit = winner_amount * settings.WIN_POINTS_RATIO

        winner_order.status = OrderStatus.WON
        winner_order.result = "won"
        winner_order.product_benefit = product_benefit
        winner_order.contrib_benefit = contrib_benefit
        winner_order.points_benefit = points_benefit

        # 发放商品权益(消费券形式)
        winner_user.coupon_balance += product_benefit
        db.add(UserWalletLog(
            user_id=winner_user.id, asset_type="coupon", change_type="income",
            amount=product_benefit, balance_before=winner_user.coupon_balance - product_benefit,
            balance_after=winner_user.coupon_balance,
            related_session_id=session_id,
            description=f"拼中商品权益-{session.level.value}",
        ))

        # 发放贡献值
        winner_user.contribution_value += contrib_benefit
        db.add(UserWalletLog(
            user_id=winner_user.id, asset_type="contribution", change_type="income",
            amount=contrib_benefit, balance_before=winner_user.contribution_value - contrib_benefit,
            balance_after=winner_user.contribution_value,
            related_session_id=session_id,
            description=f"拼中贡献值权益-{session.level.value}",
        ))

        # 发放积分(通过积分服务处理通缩逻辑)
        winner_user.points += points_benefit
        db.add(UserWalletLog(
            user_id=winner_user.id, asset_type="points", change_type="income",
            amount=points_benefit, balance_before=winner_user.points - points_benefit,
            balance_after=winner_user.points,
            related_session_id=session_id,
            description=f"拼中积分权益-{session.level.value}",
        ))

        session.winner_id = winner_user.id

        # ========== 处理拼失败用户(30人) ==========
        for loser_order in loser_orders:
            loser_amount = loser_order.amount
            loser_user_result = await db.execute(select(User).where(User.id == loser_order.user_id))
            loser_user = loser_user_result.scalar_one()

            # 本金全额退回
            old_balance = loser_user.balance
            loser_user.balance += loser_amount
            db.add(UserWalletLog(
                user_id=loser_user.id, asset_type="balance", change_type="unlock",
                amount=loser_amount, balance_before=old_balance,
                balance_after=loser_user.balance,
                related_session_id=session_id,
                description=f"拼失败本金退回-{session.level.value}",
            ))

            # 广告补贴: 金额 * 0.7% (30人合计21%)
            ad_subsidy = loser_amount * settings.LOSE_AD_SUBSIDY_RATIO
            loser_user.coupon_balance += ad_subsidy
            db.add(UserWalletLog(
                user_id=loser_user.id, asset_type="coupon", change_type="income",
                amount=ad_subsidy, balance_before=loser_user.coupon_balance - ad_subsidy,
                balance_after=loser_user.coupon_balance,
                related_session_id=session_id,
                description=f"拼失败广告补贴-{session.level.value}",
            ))

            # 推荐人补贴: 金额 * 0.1% (30人合计3%)
            referral_subsidy = loser_amount * settings.LOSE_REFERRAL_SUBSIDY_RATIO
            loser_user.coupon_balance += referral_subsidy
            db.add(UserWalletLog(
                user_id=loser_user.id, asset_type="coupon", change_type="income",
                amount=referral_subsidy, balance_before=loser_user.coupon_balance - referral_subsidy,
                balance_after=loser_user.coupon_balance,
                related_session_id=session_id,
                description=f"拼失败推荐人补贴-{session.level.value}",
            ))

            loser_order.status = OrderStatus.REFUNDED
            loser_order.result = "lost"
            loser_order.ad_subsidy = ad_subsidy
            loser_order.referral_subsidy = referral_subsidy

        # 更新场次状态
        session.status = SessionStatus.COMPLETED
        session.settled_at = datetime.utcnow()

        await db.flush()
        return {
            "session_id": session_id,
            "winner_id": winner_user.id,
            "winner_order_no": winner_order.order_no,
            "loser_count": len(loser_orders),
            "product_benefit": product_benefit,
            "contrib_benefit": contrib_benefit,
            "points_benefit": points_benefit,
        }

    @staticmethod
    async def get_active_sessions(db: AsyncSession, level: Optional[GroupBuyLevel] = None) -> list:
        """获取当前可参与的场次"""
        query = select(GroupBuySession).where(
            GroupBuySession.status.in_([SessionStatus.PENDING, SessionStatus.ACTIVE])
        )
        if level:
            query = query.where(GroupBuySession.level == level)
        query = query.order_by(GroupBuySession.start_time)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_user_orders(db: AsyncSession, user_id: int, page: int = 1, size: int = 20) -> dict:
        """获取用户拼团订单记录"""
        query = select(GroupBuyOrder).where(GroupBuyOrder.user_id == user_id).order_by(GroupBuyOrder.created_at.desc())
        count_query = select(func.count()).select_from(GroupBuyOrder).where(GroupBuyOrder.user_id == user_id)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        result = await db.execute(query.offset((page - 1) * size).limit(size))
        orders = result.scalars().all()

        return {"total": total, "page": page, "size": size, "items": orders}
