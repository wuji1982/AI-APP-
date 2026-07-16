"""
数据库初始化脚本 - 创建所有表
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def init_db():
    from app.database import engine, Base
    # 导入所有模型
    from app.models import (
        User, UserWalletLog, UserRole,
        Product, ProductSKU, ProductCategory, ProductStatus, Order, OrderItem,
        GroupBuySession, GroupBuyOrder,
        ContributionRecord, ContribWeeklySettlement,
        PointsPool, PointsRecord, PointsConvertRecord,
        CouponRecord, CouponUsageLog,
        SettlementRecord, StoreMonthlyDividend, PlatformDailyFinance,
        Store, TeamMember, StoreMonthlyPerformance,
        RiskControlLog, UserRiskScore,
        UserAgent, UserAgentMemory, AgentKnowledgeSource, UserAgentConfig,
        PaymentRecord, LogisticsOrder, RefundOrder, AfterSaleTicket,
        CartItem, UserAddress, UserFavorite, ProductReview,
        Banner, Announcement, UserBrowseHistory,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("[OK] Database tables created successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
