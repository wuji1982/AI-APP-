"""
数据库种子脚本 - 填充测试数据
运行: py -m backend.scripts.seed_data
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import select, delete
from app.database import async_session_factory, engine, Base
from app.models.product import Product, ProductCategory, ProductStatus, ProductSKU
from app.models.store import Store, StoreStatus
from app.models.group_buy import GroupBuySession, GroupBuyLevel, SessionStatus
from app.models.ecommerce import Banner, Announcement
from app.models.notification import Notification, NotificationType


async def seed_products(session):
    """填充商品数据"""
    products_data = [
        # 吃
        {"name": "法库精酿啤酒 经典款 6瓶/箱", "category": ProductCategory.DRINK, "original_price": 328, "selling_price": 288, "stock": 500, "sales_count": 1230, "is_recommended": True, "description": "法库原产地精酿啤酒，麦香浓郁，口感醇厚"},
        {"name": "东北黑木耳 500g装", "category": ProductCategory.FOOD, "original_price": 89, "selling_price": 59.9, "stock": 300, "sales_count": 856, "is_recommended": True, "description": "长白山优质黑木耳，肉厚鲜嫩"},
        {"name": "五常大米 10kg", "category": ProductCategory.FOOD, "original_price": 128, "selling_price": 99, "stock": 200, "sales_count": 2100, "is_recommended": True, "description": "正宗五常稻花香大米"},
        {"name": "法库酱牛肉 500g", "category": ProductCategory.FOOD, "original_price": 78, "selling_price": 58, "stock": 150, "sales_count": 430, "is_recommended": False, "description": "传统工艺酱制，肉质鲜嫩"},
        # 喝
        {"name": "法库纯粮白酒 500ml", "category": ProductCategory.DRINK, "original_price": 168, "selling_price": 128, "stock": 400, "sales_count": 670, "is_recommended": True, "description": "纯粮酿造，清香型白酒"},
        {"name": "长白山蓝莓汁 12瓶/箱", "category": ProductCategory.DRINK, "original_price": 198, "selling_price": 158, "stock": 250, "sales_count": 340, "is_recommended": False, "description": "野生蓝莓鲜榨，无添加"},
        {"name": "东北红松籽 250g", "category": ProductCategory.DRINK, "original_price": 68, "selling_price": 49.9, "stock": 180, "sales_count": 520, "is_recommended": False, "description": "手剥红松籽，颗粒饱满"},
        # 用
        {"name": "法库手工粉条 1kg*5袋", "category": ProductCategory.USE, "original_price": 99, "selling_price": 69, "stock": 350, "sales_count": 1560, "is_recommended": True, "description": "红薯粉条，久煮不烂"},
        {"name": "东北蜂蜜 500g*2瓶", "category": ProductCategory.USE, "original_price": 138, "selling_price": 98, "stock": 200, "sales_count": 780, "is_recommended": True, "description": "椴树蜜，天然纯正"},
        {"name": "法库豆油 5L", "category": ProductCategory.USE, "original_price": 89, "selling_price": 69.9, "stock": 300, "sales_count": 920, "is_recommended": False, "description": "非转基因大豆压榨"},
        {"name": "有机杂粮礼盒 8袋装", "category": ProductCategory.USE, "original_price": 268, "selling_price": 198, "stock": 100, "sales_count": 230, "is_recommended": True, "description": "小米/黑米/红豆/绿豆等8种"},
        # 穿
        {"name": "东北棉拖鞋 加厚保暖", "category": ProductCategory.WEAR, "original_price": 59, "selling_price": 39.9, "stock": 500, "sales_count": 3200, "is_recommended": True, "description": "加绒加厚，防滑底"},
        {"name": "法库羊绒围巾", "category": ProductCategory.WEAR, "original_price": 298, "selling_price": 198, "stock": 80, "sales_count": 156, "is_recommended": False, "description": "100%山羊绒，轻柔保暖"},
        {"name": "东北大花棉袄 女款", "category": ProductCategory.WEAR, "original_price": 398, "selling_price": 268, "stock": 60, "sales_count": 89, "is_recommended": False, "description": "传统东北大花，喜庆保暖"},
        {"name": "法库真皮皮带", "category": ProductCategory.WEAR, "original_price": 198, "selling_price": 128, "stock": 120, "sales_count": 340, "is_recommended": True, "description": "头层牛皮，商务休闲"},
        {"name": "东北貉子毛帽", "category": ProductCategory.WEAR, "original_price": 168, "selling_price": 118, "stock": 90, "sales_count": 210, "is_recommended": False, "description": "真貉子毛，防寒保暖"},
    ]

    for i, p in enumerate(products_data):
        # 检查是否已存在
        result = await session.execute(select(Product).where(Product.name == p["name"]))
        if result.scalar_one_or_none():
            continue

        product = Product(
            name=p["name"],
            category=p["category"],
            status=ProductStatus.ACTIVE,
            description=p["description"],
            cover_image=f"https://picsum.photos/400/400?random={i+1}",
            images=f'["https://picsum.photos/400/400?random={i+1}","https://picsum.photos/400/400?random={i+100}"]',
            original_price=p["original_price"],
            selling_price=p["selling_price"],
            cost_price=p["selling_price"] * 0.6,
            discount_amount=p["selling_price"] * 0.2,
            stock=p["stock"],
            sales_count=p["sales_count"],
            sort_order=100 - i,
            is_recommended=p["is_recommended"],
        )
        session.add(product)
        await session.flush()

        # 添加SKU
        sku = ProductSKU(
            product_id=product.id,
            sku_name="默认规格",
            sku_code=f"SKU-{product.id:04d}",
            price=p["selling_price"],
            stock=p["stock"],
            attributes='{"spec": "默认"}'
        )
        session.add(sku)

    print(f"  [OK] 商品数据: {len(products_data)} 条")


async def seed_stores(session):
    """填充门店数据"""
    stores_data = [
        {"store_no": "ST001", "name": "AI星木·法库旗舰店", "province": "辽宁", "city": "沈阳", "district": "法库县", "address": "法库镇中央大街28号", "contact_name": "张经理", "contact_phone": "13800001111", "total_performance": 156000, "monthly_performance": 32000, "member_count": 230},
        {"store_no": "ST002", "name": "AI星木·沈阳旗舰店", "province": "辽宁", "city": "沈阳", "district": "沈河区", "address": "沈河区中街路168号", "contact_name": "李经理", "contact_phone": "13800002222", "total_performance": 230000, "monthly_performance": 45000, "member_count": 380},
        {"store_no": "ST003", "name": "AI星木·大连体验店", "province": "辽宁", "city": "大连", "district": "中山区", "address": "中山区人民路128号", "contact_name": "王经理", "contact_phone": "13800003333", "total_performance": 189000, "monthly_performance": 38000, "member_count": 290},
        {"store_no": "ST004", "name": "AI星木·长春旗舰店", "province": "吉林", "city": "长春", "district": "朝阳区", "address": "朝阳区重庆路58号", "contact_name": "赵经理", "contact_phone": "13800004444", "total_performance": 120000, "monthly_performance": 25000, "member_count": 180},
        {"store_no": "ST005", "name": "AI星木·哈尔滨旗舰店", "province": "黑龙江", "city": "哈尔滨", "district": "南岗区", "address": "南岗区果戈里大街88号", "contact_name": "刘经理", "contact_phone": "13800005555", "total_performance": 98000, "monthly_performance": 18000, "member_count": 150},
    ]

    for s in stores_data:
        result = await session.execute(select(Store).where(Store.store_no == s["store_no"]))
        if result.scalar_one_or_none():
            continue

        store = Store(
            store_no=s["store_no"],
            name=s["name"],
            status=StoreStatus.ACTIVE,
            province=s["province"],
            city=s["city"],
            district=s["district"],
            address=s["address"],
            contact_name=s["contact_name"],
            contact_phone=s["contact_phone"],
            total_performance=s["total_performance"],
            monthly_performance=s["monthly_performance"],
            member_count=s["member_count"],
        )
        session.add(store)

    print(f"  [OK] 门店数据: {len(stores_data)} 条")


async def seed_group_buy_sessions(session):
    """填充拼团场次"""
    now = datetime.utcnow()
    sessions_data = [
        {"session_no": f"GB{now.strftime('%Y%m%d')}J01", "level": GroupBuyLevel.JUNIOR, "box_multiplier": 1, "total_price": 288, "status": SessionStatus.ACTIVE, "current_players": 18, "start_time": now.replace(hour=10, minute=0, second=0), "end_time": now.replace(hour=11, minute=0, second=0)},
        {"session_no": f"GB{now.strftime('%Y%m%d')}J02", "level": GroupBuyLevel.JUNIOR, "box_multiplier": 1, "total_price": 288, "status": SessionStatus.ACTIVE, "current_players": 25, "start_time": now.replace(hour=11, minute=0, second=0), "end_time": now.replace(hour=12, minute=0, second=0)},
        {"session_no": f"GB{now.strftime('%Y%m%d')}S01", "level": GroupBuyLevel.SENIOR, "box_multiplier": 5, "total_price": 1440, "status": SessionStatus.ACTIVE, "current_players": 12, "start_time": now.replace(hour=10, minute=0, second=0), "end_time": now.replace(hour=11, minute=0, second=0)},
        {"session_no": f"GB{now.strftime('%Y%m%d')}J03", "level": GroupBuyLevel.JUNIOR, "box_multiplier": 1, "total_price": 288, "status": SessionStatus.PENDING, "current_players": 0, "start_time": now.replace(hour=14, minute=0, second=0), "end_time": now.replace(hour=15, minute=0, second=0)},
        {"session_no": f"GB{now.strftime('%Y%m%d')}S02", "level": GroupBuyLevel.SENIOR, "box_multiplier": 5, "total_price": 1440, "status": SessionStatus.PENDING, "current_players": 0, "start_time": now.replace(hour=15, minute=0, second=0), "end_time": now.replace(hour=16, minute=0, second=0)},
        {"session_no": f"GB{(now - timedelta(days=1)).strftime('%Y%m%d')}J01", "level": GroupBuyLevel.JUNIOR, "box_multiplier": 1, "total_price": 288, "status": SessionStatus.COMPLETED, "current_players": 31, "start_time": (now - timedelta(days=1)).replace(hour=10, minute=0, second=0), "end_time": (now - timedelta(days=1)).replace(hour=11, minute=0, second=0)},
    ]

    for s in sessions_data:
        result = await session.execute(select(GroupBuySession).where(GroupBuySession.session_no == s["session_no"]))
        if result.scalar_one_or_none():
            continue

        session_obj = GroupBuySession(
            session_no=s["session_no"],
            level=s["level"],
            price_per_box=288.0,
            box_multiplier=s["box_multiplier"],
            total_price=s["total_price"],
            total_players=31,
            winner_count=1,
            loser_count=30,
            current_players=s["current_players"],
            status=s["status"],
            start_time=s["start_time"],
            end_time=s["end_time"],
        )
        session.add(session_obj)

    print(f"  [OK] 拼团场次: {len(sessions_data)} 条")


async def seed_banners(session):
    """填充Banner"""
    banners_data = [
        {"title": "AI共享商城盛大开业", "image_url": "https://picsum.photos/750/360?random=201", "link_url": "/pages/mall/index", "position": "home", "sort_order": 1},
        {"title": "法库啤酒拼团火热进行中", "image_url": "https://picsum.photos/750/360?random=202", "link_url": "/pages/group-buy/index", "position": "home", "sort_order": 2},
        {"title": "新人专享 首单立减20", "image_url": "https://picsum.photos/750/360?random=203", "link_url": "/pages/mall/index", "position": "home", "sort_order": 3},
        {"title": "东北特产专区上线", "image_url": "https://picsum.photos/750/360?random=204", "link_url": "/pages/mall/index", "position": "home", "sort_order": 4},
    ]

    for b in banners_data:
        result = await session.execute(select(Banner).where(Banner.title == b["title"]))
        if result.scalar_one_or_none():
            continue

        banner = Banner(
            title=b["title"],
            image_url=b["image_url"],
            link_url=b["link_url"],
            position=b["position"],
            sort_order=b["sort_order"],
            is_active=True,
        )
        session.add(banner)

    print(f"  [OK] Banner: {len(banners_data)} 条")


async def seed_announcements(session):
    """填充公告"""
    announcements_data = [
        {"title": "平台上线公告", "content": "AI星木共享商城正式上线运营，欢迎体验！", "announce_type": "notice"},
        {"title": "拼团规则说明", "content": "每日10:00-22:00开放拼团，31人参与仅1人拼中，欢迎了解规则后参与。", "announce_type": "notice"},
        {"title": "新人福利活动", "content": "新用户注册即送20元消费券，首单满99可用！", "announce_type": "activity"},
        {"title": "系统维护通知", "content": "本周六凌晨2:00-4:00进行系统维护升级，届时部分功能暂不可用。", "announce_type": "update"},
        {"title": "法库啤酒节预告", "content": "第七届法库啤酒节将于下月举办，届时推出限定款精酿啤酒！", "announce_type": "activity"},
    ]

    for a in announcements_data:
        result = await session.execute(select(Announcement).where(Announcement.title == a["title"]))
        if result.scalar_one_or_none():
            continue

        ann = Announcement(
            title=a["title"],
            content=a["content"],
            announce_type=a["announce_type"],
            is_active=True,
        )
        session.add(ann)

    print(f"  [OK] 公告: {len(announcements_data)} 条")


async def seed_notifications(session):
    """填充通知数据（给用户ID=1和2）"""
    now = datetime.utcnow()
    notifications_data = [
        {"user_id": 1, "type": NotificationType.ORDER, "title": "订单已发货", "content": "您的订单 ORD20240001 已发货，快递单号 SF1234567890", "action_text": "查看物流", "is_read": False, "created_at": now - timedelta(hours=1)},
        {"user_id": 1, "type": NotificationType.GROUP, "title": "拼团成功", "content": "恭喜！您参与的精酿啤酒初级团已成功，31人全部参团", "action_text": "查看详情", "is_read": False, "created_at": now - timedelta(hours=2)},
        {"user_id": 1, "type": NotificationType.SYSTEM, "title": "系统升级通知", "content": "平台将于本周六凌晨2:00-4:00进行系统维护升级，届时部分功能可能暂时无法使用", "action_text": "", "is_read": True, "created_at": now - timedelta(days=1)},
        {"user_id": 1, "type": NotificationType.ORDER, "title": "订单已完成", "content": "您的订单 ORD20240002 已自动确认收货，贡献值已发放至您的账户", "action_text": "去评价", "is_read": True, "created_at": now - timedelta(days=2)},
        {"user_id": 1, "type": NotificationType.ACTIVITY, "title": "新品上架", "content": "法库精酿啤酒新口味上架，限时9折优惠，先到先得", "action_text": "去看看", "is_read": True, "created_at": now - timedelta(days=3)},
        {"user_id": 1, "type": NotificationType.GROUP, "title": "拼团即将成团", "content": "您参与的五常大米拼团还差2人即可成团，快邀请好友加入", "action_text": "邀请好友", "is_read": False, "created_at": now - timedelta(hours=5)},
        {"user_id": 1, "type": NotificationType.ORDER, "title": "退款到账通知", "content": "您的退款 RFD20240001 已处理完成，金额 ¥29.90 已原路返回", "action_text": "查看详情", "is_read": True, "created_at": now - timedelta(days=3)},
        {"user_id": 2, "type": NotificationType.ORDER, "title": "订单已发货", "content": "您的订单 ORD20240003 已发货，请注意查收", "action_text": "查看物流", "is_read": False, "created_at": now - timedelta(hours=3)},
        {"user_id": 2, "type": NotificationType.SYSTEM, "title": "欢迎加入AI星木", "content": "恭喜您注册成功！新用户即送20元消费券，快去商城看看吧", "action_text": "去商城", "is_read": False, "created_at": now - timedelta(days=1)},
        {"user_id": 2, "type": NotificationType.ACTIVITY, "title": "新人福利活动", "content": "新用户首单满99减20，快来体验拼团购物吧！", "action_text": "立即参与", "is_read": False, "created_at": now - timedelta(hours=8)},
    ]

    for n in notifications_data:
        notif = Notification(**n)
        session.add(notif)

    print(f"  [OK] 通知数据: {len(notifications_data)} 条")


async def main():
    print("=" * 50)
    print("AI星木商城 - 数据库种子数据填充")
    print("=" * 50)

    # 确保表已创建
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] 数据库表已就绪")

    async with async_session_factory() as session:
        await seed_stores(session)
        await seed_products(session)
        await seed_group_buy_sessions(session)
        await seed_banners(session)
        await seed_announcements(session)
        await seed_notifications(session)
        await session.commit()

    print("=" * 50)
    print("[OK] 所有测试数据填充完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
