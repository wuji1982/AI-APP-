"""
数据库初始化脚本
创建所有表并插入种子数据
"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy import text

from app.database import engine, Base, async_session
from app.models import *
from app.models.user import User
from app.models.product import Product
from app.models.store import Store
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables():
    """创建所有数据库表"""
    logger.info("开始创建数据库表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表创建完成")


async def init_seed_data():
    """初始化种子数据"""
    logger.info("开始初始化种子数据...")
    
    async with async_session() as session:
        # 检查是否已有数据
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        if count > 0:
            logger.info("数据库已有数据，跳过种子数据初始化")
            return
        
        # 创建管理员用户
        admin = User(
            phone="13800000000",
            nickname="系统管理员",
            password_hash="admin123",  # 生产环境需要加密
            role="admin",
            status="active",
            balance=100000.00,
            contribution_value=0,
            points=0,
            coupon_balance=0,
            created_at=datetime.now()
        )
        session.add(admin)
        
        # 创建测试用户
        test_user = User(
            phone="13800000001",
            nickname="测试用户",
            password_hash="test123",
            role="user",
            status="active",
            balance=10000.00,
            contribution_value=0,
            points=0,
            coupon_balance=0,
            invite_code="TEST001",
            created_at=datetime.now()
        )
        session.add(test_user)
        
        # 创建示例商品
        products = [
            Product(
                name="法库啤酒6瓶装",
                category="drink",
                description="法库精酿啤酒，6瓶装",
                cover_image="/static/products/beer6.jpg",
                original_price=388.00,
                selling_price=288.00,
                discount_amount=57.60,  # 288 * 20%
                stock=1000,
                sales_count=0,
                is_recommended=True,
                status="on_sale",
                created_at=datetime.now()
            ),
            Product(
                name="法库啤酒12瓶装",
                category="drink",
                description="法库精酿啤酒，12瓶装（高级团）",
                cover_image="/static/products/beer12.jpg",
                original_price=1940.00,
                selling_price=1440.00,
                discount_amount=288.00,  # 1440 * 20%
                stock=500,
                sales_count=0,
                is_recommended=True,
                status="on_sale",
                created_at=datetime.now()
            ),
            Product(
                name="法库啤酒24瓶装",
                category="drink",
                description="法库精酿啤酒，24瓶装（SVIP团）",
                cover_image="/static/products/beer24.jpg",
                original_price=15400.00,
                selling_price=11520.00,
                discount_amount=2304.00,  # 11520 * 20%
                stock=200,
                sales_count=0,
                is_recommended=True,
                status="on_sale",
                created_at=datetime.now()
            )
        ]
        session.add_all(products)
        
        # 创建示例门店
        store = Store(
            name="法库旗舰店",
            province="辽宁省",
            city="沈阳市",
            district="法库县",
            address="法库县中央大街1号",
            phone="024-12345678",
            owner_id=2,  # 测试用户
            status="active",
            created_at=datetime.now()
        )
        session.add(store)
        
        await session.commit()
        logger.info("种子数据初始化完成")
        logger.info(f"管理员账号: 13800000000 / admin123")
        logger.info(f"测试用户: 13800000001 / test123")


async def main():
    """主函数"""
    try:
        await create_tables()
        await init_seed_data()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
