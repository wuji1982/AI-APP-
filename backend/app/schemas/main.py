"""
Pydantic 请求/响应模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ========== 认证相关 ==========
class RegisterRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, description="密码")
    nickname: Optional[str] = None
    referrer_id: Optional[int] = None

class LoginRequest(BaseModel):
    phone: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    im_token: Optional[str] = None

# ========== 用户相关 ==========
class UserInfo(BaseModel):
    id: int
    phone: str
    nickname: Optional[str]
    role: str
    balance: float
    contribution_value: float
    points: float
    coupon_balance: float
    store_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class WalletInfo(BaseModel):
    balance: float
    contribution_value: float
    points: float
    coupon_balance: float

# ========== 商品相关 ==========
class ProductCreate(BaseModel):
    name: str
    category: str  # food/drink/use/wear
    original_price: float
    selling_price: float
    description: Optional[str] = None
    cover_image: Optional[str] = None
    stock: int = 0

class ProductInfo(BaseModel):
    id: int
    name: str
    category: str
    original_price: float
    selling_price: float
    discount_amount: Optional[float]
    stock: int
    sales_count: int
    cover_image: Optional[str]
    status: str

    class Config:
        from_attributes = True

# ========== 拼团相关 ==========
class JoinGroupBuyRequest(BaseModel):
    session_id: int = Field(..., description="拼团场次ID")

class GroupBuySessionInfo(BaseModel):
    id: int
    session_no: str
    level: str
    total_price: float
    total_players: int
    current_players: int
    status: str
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True

class GroupBuyOrderInfo(BaseModel):
    id: int
    order_no: str
    session_id: int
    amount: float
    status: str
    result: Optional[str]
    product_benefit: float
    contrib_benefit: float
    points_benefit: float
    ad_subsidy: float
    referral_subsidy: float
    created_at: datetime

    class Config:
        from_attributes = True

# ========== 贡献值相关 ==========
class ContributionInfo(BaseModel):
    id: int
    source: str
    role: str
    base_amount: float
    discount_amount: float
    ratio: float
    contrib_value: float
    remaining_value: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

# ========== 积分相关 ==========
class PointsConvertRequest(BaseModel):
    points_amount: float = Field(..., description="兑换积分数量")

class PointsPoolInfo(BaseModel):
    total_supply: float
    total_issued: float
    total_deflated: float
    total_converted: float
    current_unit_price: float
    remaining: float

# ========== 消费券相关 ==========
class CouponInfo(BaseModel):
    id: int
    source_type: str
    amount: float
    remaining: float
    created_at: datetime

    class Config:
        from_attributes = True

# ========== 门店相关 ==========
class StoreCreate(BaseModel):
    store_no: str
    name: str
    province: str
    city: str
    district: str
    address: str
    contact_name: str
    contact_phone: str

class StoreInfo(BaseModel):
    id: int
    store_no: str
    name: str
    province: str
    city: str
    district: str
    status: str
    total_performance: float
    monthly_performance: float
    member_count: int

    class Config:
        from_attributes = True

# ========== 通用响应 ==========
class ResponseModel(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None


# ========== 通知相关 ==========
class NotificationInfo(BaseModel):
    id: int
    type: str
    title: str
    content: str
    action_text: Optional[str] = None
    action_url: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[NotificationInfo]


class UnreadCountResponse(BaseModel):
    total: int
    order: int
    group: int
    system: int
    activity: int


# ========== 用户搜索 ==========
class UserSearchResult(BaseModel):
    id: int
    nickname: Optional[str] = None
    phone_masked: str  # 脱敏手机号
    avatar_url: Optional[str] = None
