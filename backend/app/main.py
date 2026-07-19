"""
AI Agent 共享商城 + 拼团生态平台
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import engine, Base
from app.api.v1 import auth, user, product, group_buy, contribution, points, coupon, store, admin, user_agent, im, payment, ecommerce, order, map_service, notification
from app.api.v1.websocket import router as ws_router
from app.api.v1.agent_ws import router as agent_ws_router
from app.middleware import GlobalExceptionMiddleware, RequestLoggingMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表（开发阶段，生产环境使用 alembic 迁移）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭时释放资源
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Agent全量赋能 · 共享商城+拼团生态平台 API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 中间件配置（注意：中间件执行顺序与添加顺序相反）
# 1. 请求日志中间件（最先执行）
app.add_middleware(RequestLoggingMiddleware)
# 2. 全局异常处理中间件
app.add_middleware(GlobalExceptionMiddleware)
# 3. CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
api_prefix = "/api/v1"
app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["认证"])
app.include_router(user.router, prefix=f"{api_prefix}/user", tags=["用户"])
app.include_router(product.router, prefix=f"{api_prefix}/product", tags=["商品/商城"])
app.include_router(group_buy.router, prefix=f"{api_prefix}/group-buy", tags=["拼团"])
app.include_router(contribution.router, prefix=f"{api_prefix}/contribution", tags=["贡献值"])
app.include_router(points.router, prefix=f"{api_prefix}/points", tags=["积分"])
app.include_router(coupon.router, prefix=f"{api_prefix}/coupon", tags=["消费券"])
app.include_router(store.router, prefix=f"{api_prefix}/store", tags=["门店/团队"])
app.include_router(admin.router, prefix=f"{api_prefix}/admin", tags=["管理后台"])
app.include_router(user_agent.router, prefix=f"{api_prefix}", tags=["用户智能体"])
app.include_router(im.router, prefix=f"{api_prefix}", tags=["即时通讯"])
app.include_router(payment.router, prefix=f"{api_prefix}", tags=["支付/物流/退款"])
app.include_router(ecommerce.router, prefix=f"{api_prefix}", tags=["电商通用"])
app.include_router(order.router, prefix=f"{api_prefix}/order", tags=["订单管理"])
app.include_router(map_service.router, prefix=f"{api_prefix}/map", tags=["地图服务"])
app.include_router(notification.router, prefix=f"{api_prefix}", tags=["通知"])
app.include_router(ws_router, tags=["WebSocket"])
app.include_router(agent_ws_router, tags=["智能体WebSocket"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
