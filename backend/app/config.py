"""
全局配置模块
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "AI共享商城平台"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aixingmu"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery 配置
    CELERY_BROKER_URL: str = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # JWT 认证配置
    SECRET_KEY: str = "aixingmu-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]

    # MinIO 对象存储配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "aixingmu"

    # ========== 拼团业务固定参数 ==========
    # 法库啤酒标准定价
    BEER_PRICE_PER_BOX: float = 288.0  # 单箱定价288元
    BEER_PER_BOX: int = 6  # 6瓶/箱

    # 三大板块拼团倍数
    GROUP_BUY_JUNIOR_MULTIPLIER: int = 1    # 初级团: 288x1=288元(1箱)
    GROUP_BUY_SENIOR_MULTIPLIER: int = 5    # 高级团: 288x5=1440元(5箱)
    GROUP_BUY_SVIP_MULTIPLIER: int = 40     # SVIP团: 288x40=11520元(40箱)

    # 拼团核心规则
    GROUP_BUY_TOTAL_PLAYERS: int = 31   # 每场31人
    GROUP_BUY_WINNERS: int = 1          # 1人拼中
    GROUP_BUY_LOSERS: int = 30          # 30人拼失败
    GROUP_BUY_START_HOUR: int = 10      # 每日10:00开始
    GROUP_BUY_END_HOUR: int = 22        # 每日22:00结束
    GROUP_BUY_MAX_ORDERS_PER_USER: int = 5  # 单ID单组最多5单

    # ========== 贡献值分配比例（全网统一） ==========
    CONTRIB_CONSUMER_RATIO: float = 0.50        # 消费者 50%
    CONTRIB_MERCHANT_RATIO: float = 0.20        # 合作商家/门店 20%
    CONTRIB_REFERRAL_MERCHANT_RATIO: float = 0.08  # 推荐商家 8%
    CONTRIB_REFERRAL_CONSUMER_RATIO: float = 0.05  # 推荐消费者 5%
    CONTRIB_AGENT_RATIO: float = 0.07           # 省/市/区县代理合计 7%
    CONTRIB_PLATFORM_RATIO: float = 0.10        # 平台利润留存 10%
    CONTRIB_MULTIPLIER: float = 10.0            # 贡献值乘数

    # 整体让利比例
    GLOBAL_DISCOUNT_RATIO: float = 0.20  # 整体让利20%

    # ========== 线下四级分润比例 ==========
    PROFIT_PROVINCE_RATIO: float = 0.01   # 省级代理 1%
    PROFIT_CITY_RATIO: float = 0.02       # 市级代理 2%
    PROFIT_DISTRICT_RATIO: float = 0.04   # 区县代理 4%
    PROFIT_STORE_RATIO: float = 0.08      # 线下门店 8%
    PROFIT_REFERRAL_STORE_RATIO: float = 0.01  # 推荐门店 1%

    # ========== 拼团用户权益比例 ==========
    # 拼中用户权益
    WIN_PRODUCT_RATIO: float = 0.10       # 商品权益 10%
    WIN_CONTRIB_RATIO: float = 0.20       # 贡献值权益 20%
    WIN_POINTS_RATIO: float = 0.20        # 增值积分权益 20%

    # 拼失败用户保障
    LOSE_AD_SUBSIDY_RATIO: float = 0.007  # 广告补贴 0.7%
    LOSE_REFERRAL_SUBSIDY_RATIO: float = 0.001  # 推荐人补贴 0.1%
    # 30人合计: 广告补贴21%, 推荐人补贴3%

    # ========== 平台收支分配（100%） ==========
    DIST_AGENT: float = 0.07              # 代理支出 7%
    DIST_STORE: float = 0.08              # 门店分账 8%
    DIST_REFERRAL_STORE: float = 0.01     # 推荐门店 1%
    DIST_WIN_PRODUCT: float = 0.10        # 拼中商品权益 10%
    DIST_WIN_CONTRIB: float = 0.20        # 拼中贡献值 20%
    DIST_WIN_POINTS: float = 0.20         # 拼中积分 20%
    DIST_LOSE_AD: float = 0.21            # 拼失败广告补贴 21%
    DIST_LOSE_REFERRAL: float = 0.03      # 拼失败推荐人补贴 3%
    DIST_PLATFORM_PROFIT: float = 0.10    # 平台利润 10%

    # ========== 贡献值递减兑换规则 ==========
    CONTRIB_DAILY_RATE_DEFAULT: float = 0.0005  # 默认日利率 万分之五
    CONTRIB_DAILY_RATE_MIN: float = 0.00001     # 最低日利率 万分之0.1
    CONTRIB_DAILY_RATE_MAX: float = 0.001       # 最高日利率 万分之10
    CONTRIB_SETTLE_DAY: str = "monday"          # 每周一结算

    # ========== 积分增值系统 ==========
    POINTS_TOTAL_SUPPLY: int = 12_000_000  # 总发行量1200万
    POINTS_PROFIT_RATIO: float = 0.20      # 20%利润值
    POINTS_DEFLATION_RATIO: float = 0.20   # 20%通缩

    # ========== 门店阶梯分红 ==========
    STORE_TIER1_MIN: float = 30000   # 3万
    STORE_TIER1_MAX: float = 50000   # 5万
    STORE_TIER2_MIN: float = 50000   # 5万
    STORE_TIER2_MAX: float = 100000  # 10万
    STORE_TIER3_MIN: float = 100000  # 10万
    STORE_TIER3_MAX: float = 500000  # 50万
    STORE_TIER4_MIN: float = 500000  # 50万以上
    STORE_TIER1_DIVIDEND: float = 0.005  # 0.5%
    STORE_TIER2_DIVIDEND: float = 0.005
    STORE_TIER3_DIVIDEND: float = 0.005
    STORE_TIER4_DIVIDEND: float = 0.01   # 1%

    # AI Agent 配置
    LLM_API_KEY: str = ""
    LLM_API_BASE: str = ""
    LLM_MODEL: str = "gpt-4"

    # Dify RAG平台配置
    DIFY_API_URL: str = "http://localhost:3800/v1"
    DIFY_API_KEY: str = ""  # Dify平台管理员API Key
    DIFY_DEFAULT_MODEL: str = "gpt-4"  # 用户智能体默认模型

    # 向量数据库配置 (pgvector)
    VECTOR_DIMENSION: int = 1536  # OpenAI embedding维度
    VECTOR_INDEX_TYPE: str = "ivfflat"  # 索引类型: ivfflat/hnsw

    # OpenIM 即时通讯配置
    OPENIM_API_URL: str = "http://localhost:10002"  # OpenIM API地址
    OPENIM_ADMIN_URL: str = "http://localhost:10008"  # OpenIM管理后台API
    OPENIM_SECRET: str = "openim-secret-key-change-in-production"
    OPENIM_ADMIN_TOKEN: str = ""  # OpenIM管理员Token

    # ========== 支付宝支付配置 ==========
    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""
    ALIPAY_PUBLIC_KEY: str = ""
    ALIPAY_NOTIFY_URL: str = "https://yourdomain.com/api/v1/payment/notify/alipay"
    ALIPAY_GATEWAY: str = "https://openapi.alipay.com/gateway.do"

    # ========== 微信支付配置 ==========
    WECHAT_APP_ID: str = ""
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_NOTIFY_URL: str = "https://yourdomain.com/api/v1/payment/notify/wechat"
    WECHAT_CERT_PATH: str = ""
    WECHAT_KEY_PATH: str = ""

    # ========== 快递100物流配置 ==========
    KUAIDI100_KEY: str = ""
    KUAIDI100_CUSTOMER: str = ""
    KUAIDI100_CALLBACK: str = "https://yourdomain.com/api/v1/logistics/callback"

    # ========== 短信服务配置 ==========
    SMS_PROVIDER: str = "mock"  # mock / aliyun / tencent
    SMS_ALIYUN_ACCESS_KEY: str = ""
    SMS_ALIYUN_SECRET: str = ""
    SMS_ALIYUN_SIGN_NAME: str = ""
    SMS_ALIYUN_TEMPLATE_CODE: str = ""
    SMS_TENCENT_SECRET_ID: str = ""
    SMS_TENCENT_SECRET_KEY: str = ""
    SMS_TENCENT_APP_ID: str = ""
    SMS_TENCENT_SIGN_NAME: str = ""
    SMS_TENCENT_TEMPLATE_ID: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
