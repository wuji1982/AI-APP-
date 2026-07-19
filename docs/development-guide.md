# AI Agent 共享商城 - 开发指南

> 本文档是项目开发的核心参考，用于保持开发方向一致，避免跑偏。

---

## 一、架构设计原则

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                    前端层 (Frontend)                  │
│  mobile-app(H5)  │  web-admin(Vue3)  │  merchant    │
├─────────────────────────────────────────────────────┤
│                  Nginx 反向代理 (:80)                │
├─────────────────────────────────────────────────────┤
│               FastAPI 后端 (:8000)                   │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ API路由  │→│ Service  │→│  Model   │→│  DB    │ │
│  │ (v1/*)  │ │ (业务层)  │ │ (数据层) │ │(SQLite)│ │
│  └─────────┘ └──────────┘ └──────────┘ └────────┘ │
├─────────────────────────────────────────────────────┤
│  Celery Worker │ Celery Beat │ WebSocket │ OpenIM   │
├─────────────────────────────────────────────────────┤
│  Dify RAG (AI) │ MinIO (存储) │ Redis (缓存)        │
└─────────────────────────────────────────────────────┘
```

### 1.2 分层职责

| 层级 | 目录 | 职责 | 禁止 |
|------|------|------|------|
| **API 路由层** | `app/api/v1/` | 接收请求、参数校验、调用 Service、返回响应 | 禁止写业务逻辑 |
| **Service 层** | `app/services/` | 核心业务逻辑、数据操作、跨模块协调 | 禁止处理 HTTP 请求/响应 |
| **Model 层** | `app/models/` | 数据库表定义、枚举、关系映射 | 禁止包含业务逻辑 |
| **Schema 层** | `app/schemas/` | Pydantic 请求/响应模型定义 | 禁止包含业务逻辑 |

### 1.3 新增模块标准流程

以通知模块为参考模板：

```
1. 定义 Model   → app/models/xxx.py         (数据表)
2. 注册 Model   → app/models/__init__.py     (导出)
3. 定义 Schema  → app/schemas/main.py        (请求/响应模型)
4. 编写 Service → app/services/xxx_service.py (业务逻辑)
5. 编写 API     → app/api/v1/xxx.py          (路由端点)
6. 注册路由     → app/main.py                (include_router)
7. 前端 API     → frontend/mobile-app/src/api/index.js
8. 前端页面     → frontend/mobile-app/src/pages/xxx/index.vue
9. 种子数据     → backend/scripts/seed_data.py
```

---

## 二、后端开发规范

### 2.1 API 路由规范

```python
# 路由前缀统一: /api/v1
# RESTful 风格

GET    /api/v1/{module}          # 列表查询（分页）
GET    /api/v1/{module}/{id}     # 详情查询
POST   /api/v1/{module}          # 创建
PUT    /api/v1/{module}/{id}     # 更新
DELETE /api/v1/{module}/{id}     # 删除

# 特殊端点
GET    /api/v1/{module}/summary      # 汇总信息
GET    /api/v1/{module}/unread-count # 计数类
PUT    /api/v1/{module}/read-all     # 批量操作
```

### 2.2 认证方式

```python
# JWT Bearer Token
# 请求头: Authorization: Bearer <token>
# 依赖注入: user_id: int = Depends(get_current_user_id)

# Token 获取: POST /api/v1/auth/login
# 响应: { "access_token": "xxx", "token_type": "bearer" }
# 注意: token 在响应根级别，不在 data 内
```

### 2.3 错误处理

```python
# 使用 FastAPI HTTPException
# 400: 业务逻辑错误 (ValueError)
# 401: 未认证/Token过期
# 403: 权限不足
# 404: 资源不存在
# 500: 服务器内部错误

# 全局异常中间件自动捕获，返回格式:
# { "detail": "错误信息" }
```

### 2.4 数据库操作

```python
# SQLAlchemy Async + SQLite(开发) / PostgreSQL(生产)
# 数据库会话通过 Depends(get_db) 注入

# 查询示例:
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()

# 分页模式:
count_query = select(func.count()).select_from(query.subquery())
total = (await db.execute(count_query)).scalar() or 0
query = query.offset((page - 1) * size).limit(size)

# 提交:
db.add(obj)
await db.commit()
await db.refresh(obj)
```

### 2.5 配置管理

```python
# 所有配置集中在 app/config.py (pydantic-settings)
# 环境变量通过 .env 文件加载
# 敏感信息不提交到 Git (.gitignore 已排除 .env)

# 引用方式:
from app.config import settings
settings.SECRET_KEY
settings.POINTS_TOTAL_SUPPLY
```

---

## 三、前端开发规范

### 3.1 移动端页面结构 (uni-app)

```vue
<template>
  <view class="page">
    <!-- 页面内容 -->
  </view>
</template>

<script>
import { apiFunc1, apiFunc2 } from '../../api/index'

export default {
  data() { return { /* 状态 */ } },
  onShow() { /* 页面显示时加载数据 */ },
  onReachBottom() { /* 触底加载更多 */ },
  methods: {
    async loadData() { /* 调用API加载数据 */ },
    goTo(url) { uni.navigateTo({ url }) },
    formatNum(val) { return (parseFloat(val) || 0).toFixed(2) },
  }
}
</script>

<style scoped>
/* 样式 */
</style>
```

### 3.2 API 调用规范

```javascript
// 所有 API 函数定义在 src/api/index.js
// 基础路径: /api/v1
// 自动附加 Bearer Token
// 401 自动跳转登录页

// 调用模式:
const res = await apiFunction(params)
// 成功: 直接返回 response.data
// 失败: throw Error

// 错误处理:
try {
  const res = await someApi()
  // 处理 res
} catch (e) {
  uni.showToast({ title: e.message || '操作失败', icon: 'none' })
}
```

### 3.3 底部导航栏 (tabBar)

当前 5 个 Tab:

| Tab | 页面路径 | 说明 |
|-----|----------|------|
| 首页 | pages/index/index | 推荐/轮播/入口 |
| 商城 | pages/mall/index | 左侧分类+右侧子分类+商品网格 |
| 拼团 | pages/group-buy/index | 拼团场次/参与 |
| 消息 | pages/message/index | IM消息/通知/搜索 |
| 我的 | pages/mine/index | 个人中心/钱包入口/设置 |

**注意**: 钱包已从 tabBar 移至 "我的" → "我的钱包"

### 3.4 页面清单

| 页面 | 路径 | 状态 |
|------|------|------|
| 首页 | pages/index | ✅ |
| 商城 | pages/mall | ✅ 电商风格双栏布局 |
| 拼团 | pages/group-buy | ✅ |
| 消息 | pages/message | ✅ 搜索+好友 |
| 我的 | pages/mine | ✅ |
| 钱包 | pages/wallet | ✅ 余额卡片+流水+充值提现 |
| 通知 | pages/notification | ✅ 对接真实API |
| 好友 | pages/friends | ✅ 后端搜索 |
| 聊天 | pages/chat | ✅ |
| 订单 | pages/order | ✅ |
| 商品详情 | pages/product | ✅ |
| 购物车 | pages/cart | ✅ |
| 结算 | pages/checkout | ✅ |
| 支付 | pages/pay | ✅ |
| 贡献值 | pages/contribution | ✅ |
| 消费券 | pages/coupon | ✅ |
| 门店 | pages/store | ✅ |
| 团队 | pages/team | ✅ |
| 地址 | pages/address | ✅ |
| 登录 | pages/login | ✅ |
| 设置 | pages/settings | ✅ |
| AI Agent | pages/agent | ✅ |
| 关于 | pages/about | ✅ |

---

## 四、数据模型概览

### 4.1 核心表

| 模型 | 表名 | 说明 |
|------|------|------|
| User | users | 用户(含角色/余额/代理信息) |
| UserWalletLog | user_wallet_logs | 钱包流水(四大资产变动) |
| Product | products | 商品 |
| ProductSKU | product_skus | 商品SKU |
| GroupBuySession | group_buy_sessions | 拼团场次 |
| GroupBuyOrder | group_buy_orders | 拼团订单 |
| ContributionRecord | contribution_records | 贡献值记录 |
| PointsPool | points_pool | 积分池(单例) |
| PointsRecord | points_records | 积分记录 |
| CouponRecord | coupon_records | 消费券记录 |
| Store | stores | 门店 |
| SettlementRecord | settlement_records | 结算记录 |
| PaymentRecord | payment_records | 支付记录 |
| Notification | notifications | 通知 |

### 4.2 四大资产

| 资产 | 字段 | 来源 | 用途 |
|------|------|------|------|
| 余额 | User.balance | 充值/拼团退款 | 购买商品/提现 |
| 消费券 | User.coupon_balance | 积分兑换 | 消费抵扣 |
| 贡献值 | User.contribution_value | 拼团产生 | 每周结算收益 |
| 增值积分 | User.points | 拼团产生 | 兑换消费券 |

---

## 五、开发环境操作手册

### 5.1 后端常用命令

```powershell
# 启动后端 (开发模式，自动重载)
cd d:\AIxingmu\backend
$env:PYTHONPATH="d:\AIxingmu\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 运行种子数据脚本
$env:PYTHONPATH="d:\AIxingmu\backend"
python scripts/seed_data.py

# 测试 API (PowerShell)
$token = (Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"phone":"13800138000","password":"123456"}').access_token
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/wallet/summary" -Headers @{"Authorization"="Bearer $token"}
```

### 5.2 前端常用命令

```powershell
# 启动 mobile-app H5
cd d:\AIxingmu\frontend\mobile-app
npm run dev:h5

# 启动 web-admin
cd d:\AIxingmu\frontend\web-admin
npm run dev

# 启动 merchant-admin
cd d:\AIxingmu\frontend\merchant-admin
npm run dev
```

### 5.3 Git 操作

```powershell
# 开发前先拉取最新代码
git pull

# 开发完成后提交推送
git add .
git commit -m "feat: 功能描述"
git push origin master

# 提交规范
# feat: 新功能
# fix: 修复bug
# refactor: 重构
# docs: 文档更新
# chore: 配置/依赖变更
```

---

## 六、模块开发进度追踪

### 6.1 后端 API 模块状态

| 模块 | 路由文件 | Service | 状态 |
|------|----------|---------|------|
| 认证 | auth.py | — | ✅ 完成 |
| 用户 | user.py | — | ✅ 完成(含搜索) |
| 商品 | product.py | — | ✅ 完成 |
| 拼团 | group_buy.py | group_buy_service.py | ✅ 完成 |
| 贡献值 | contribution.py | contribution_service.py | ✅ 完成 |
| 积分 | points.py | points_service.py | ✅ 完成 |
| 消费券 | coupon.py | coupon_service.py | ✅ 完成 |
| 门店 | store.py | store_service.py | ✅ 完成 |
| 管理后台 | admin.py | — | ✅ 完成 |
| 订单 | order.py | order_service.py | ✅ 完成 |
| 通知 | notification.py | notification_service.py | ✅ 完成 |
| 钱包 | wallet.py | wallet_service.py | ✅ 完成 |
| IM | im.py | im_service.py | ✅ 基础完成 |
| 支付 | payment.py | payment_service.py | 🚧 框架 |
| 物流 | — | logistics_service.py | 🚧 框架 |
| 地图 | map_service.py | — | ✅ 完成 |
| 电商通用 | ecommerce.py | — | ✅ 完成 |
| 用户智能体 | user_agent.py | user_agent_service.py | 🚧 基础 |

### 6.2 待开发功能清单

| 优先级 | 功能 | 说明 |
|--------|------|------|
| P0 | 支付对接 | 支付宝/微信支付实际接入 |
| P0 | 拼团流程完善 | 真实31人匹配/倒计时/开奖 |
| P1 | 物流追踪 | 快递100实际对接 |
| P1 | AI 智能客服 | Dify Agent 实际对话能力 |
| P1 | 结算系统 | 贡献值每周结算实际发放 |
| P2 | 风控系统 | 异常行为检测/限制 |
| P2 | 门店阶梯分红 | 月度业绩统计/分红计算 |
| P2 | 代理体系 | 省/市/区县代理分润 |
| P3 | 数据大屏 | 运营数据可视化 |
| P3 | 小程序发布 | uni-app 编译到微信小程序 |

---

## 七、注意事项

### 7.1 常见坑

1. **Write 工具追加问题**: 使用 Write 工具修改 Vue 文件时可能追加而非覆盖，导致重复 template 块。发现后立即用 SearchReplace 删除旧内容。
2. **Vite 缓存**: 前端修改不生效时，清除 `.vite` 缓存并重启 dev server。
3. **后端 --reload**: 后端修改后如果没自动重载，需手动 kill 进程重启。
4. **Token 格式**: 登录返回的 token 在 `res.access_token`，不在 `res.data.token`。
5. **PYTHONPATH**: Windows 下运行后端脚本必须设置 `$env:PYTHONPATH="d:\AIxingmu\backend"`。

### 7.2 开发检查清单

新增一个业务模块前，确认：

- [ ] Model 定义完成并注册到 `__init__.py`
- [ ] Service 层实现核心逻辑
- [ ] API 路由编写并注册到 `main.py`
- [ ] 前端 API 函数添加到 `api/index.js`
- [ ] 前端页面编写完成
- [ ] 浏览器实际验证通过
- [ ] Git 提交推送到 GitHub

### 7.3 性能基线

- API 响应时间: < 100ms (本地开发)
- 目标承载: 日活5万 / 峰值并发500
- 架构: 单机 All-in-One (12个服务内网通信)
