# AI Agent 共享商城 + 拼团生态平台

> AI Agent 全量赋能 · 共享商城 + 拼团生态平台

## 项目简介

基于 AI Agent 智能体的共享商城与拼团生态平台，融合拼团购物、贡献值分配、积分增值、消费券、线下门店代理等创新商业模式，通过 AI 智能体为用户提供个性化购物体验。

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.11+ / FastAPI / SQLAlchemy Async / SQLite(开发) / PostgreSQL(生产) |
| **前端** | Vue3 / uni-app (H5+小程序) / Element Plus (管理后台) |
| **异步任务** | Celery + RabbitMQ + Redis |
| **即时通讯** | OpenIM Server + WebSocket |
| **AI 引擎** | Dify RAG 平台 / 多 Agent 编排 |
| **对象存储** | MinIO |
| **部署** | Docker Compose / Nginx 反向代理 |

## 项目结构

```
AIxingmu/
├── backend/                    # 后端 FastAPI 服务
│   ├── app/
│   │   ├── api/v1/             # API 路由层 (18个模块)
│   │   ├── models/             # SQLAlchemy 数据模型 (13个文件)
│   │   ├── services/           # 业务逻辑层 (19个服务)
│   │   ├── schemas/            # Pydantic 数据校验
│   │   ├── agents/             # AI Agent 智能体
│   │   ├── tasks/              # Celery 异步任务
│   │   ├── ws/                 # WebSocket 连接管理
│   │   ├── utils/              # 工具函数 (auth/security)
│   │   ├── config.py           # 全局配置 (pydantic-settings)
│   │   ├── database.py         # 数据库连接
│   │   └── main.py             # 应用入口
│   └── scripts/                # 脚本 (种子数据/测试)
├── frontend/
│   ├── mobile-app/             # 移动端 uni-app (H5)
│   ├── web-admin/              # Web 管理后台 (Vue3)
│   └── merchant-admin/         # 商户管理后台
├── docker-compose.yml          # 容器编排 (12个服务)
├── nginx.conf                  # Nginx 反向代理配置
└── docs/                       # 开发文档
    └── development-guide.md    # 开发指南
```

## 核心业务模块

### 已开发完成 ✅

| 模块 | 后端 API | 前端页面 | 说明 |
|------|----------|----------|------|
| 用户认证 | `/api/v1/auth` | 登录/注册页 | 手机号+密码登录，JWT Token |
| 拼团系统 | `/api/v1/group-buy` | 拼团页/订单页 | 31人团，1人拼中，三级场次(初级/高级/SVIP) |
| 商品管理 | `/api/v1/product` | 商城页/商品详情 | 四大品类(食品/酒水/百货/服饰) |
| 贡献值 | `/api/v1/contribution` | 贡献值明细页 | 六方分配，每周结算，递减利率 |
| 积分增值 | `/api/v1/points` | 积分池状态 | 总量1200万，20%通缩，兑换消费券 |
| 消费券 | `/api/v1/coupon` | 消费券页 | 积分兑换获取，消费抵扣 |
| 门店代理 | `/api/v1/store` | 门店/团队页 | 省/市/区县三级代理，阶梯分红 |
| 订单管理 | `/api/v1/order` | 订单列表/详情 | 创建/取消/确认收货 |
| 即时通讯 | `/api/v1/im` + WebSocket | 消息页/聊天页 | OpenIM 集成，好友系统 |
| 通知中心 | `/api/v1/notifications` | 通知页 | 订单/拼团/系统/活动四类通知 |
| 钱包系统 | `/api/v1/wallet` | 钱包页 | 余额/充值/提现/流水/四大资产总览 |
| 地图服务 | `/api/v1/map` | — | 门店定位/附近搜索 |
| 管理后台 | `/api/v1/admin` | web-admin | 用户/商品/拼团/财务/系统监控 |

### 开发中 🚧

| 模块 | 状态 | 说明 |
|------|------|------|
| 支付系统 | 接口已建 | 支付宝/微信支付集成 |
| 物流追踪 | 接口已建 | 快递100对接 |
| AI 智能客服 | 基础框架 | Dify RAG + 用户智能体 |
| 风控系统 | 模型已建 | 用户风险评分/异常检测 |

## 商业模式核心参数

```
拼团规则: 31人团 → 1人拼中 / 30人拼失败
商品定价: 法库啤酒 288元/箱 (6瓶)
三级场次: 初级×1(288元) / 高级×5(1440元) / SVIP×40(11520元)

贡献值分配: 消费者50% / 商家20% / 推荐商家8% / 推荐消费者5% / 代理7% / 平台10%
积分总量: 1200万枚，20%利润值，20%通缩
```

## 快速开始

### 本地开发模式

```bash
# 1. 克隆项目
git clone https://github.com/wuji1982/AI-APP-.git
cd AIxingmu

# 2. 后端启动
cd backend
pip install -r requirements.txt
# 设置环境变量（或复制 .env.example 为 .env）
$env:PYTHONPATH="d:\AIxingmu\backend"   # Windows PowerShell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. 前端启动 (mobile-app H5)
cd frontend/mobile-app
npm install
npm run dev:h5    # http://localhost:8080

# 4. 管理后台
cd frontend/web-admin
npm install
npm run dev       # http://localhost:3000
```

### Docker 部署模式

```bash
# 启动全部服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 开发环境端口

| 服务 | 端口 | 地址 |
|------|------|------|
| 后端 API | 8000 | http://localhost:8000 |
| API 文档 (Swagger) | 8000 | http://localhost:8000/api/docs |
| mobile-app H5 | 8080 | http://localhost:8080 |
| web-admin 管理后台 | 3000 | http://localhost:3000 |
| merchant-admin | 3001 | http://localhost:3001 |

## 开发规范

详见 [开发指南](docs/development-guide.md)

## Git 工作流

- **主仓库**: GitHub (`origin/master`)
- **开发流程**: GitHub 为主，本地保持同步
- **提交规范**: `feat:` / `fix:` / `refactor:` / `docs:` / `chore:`
- **分支策略**: 单分支 master，直接推送

## 测试账号

| 角色 | 手机号 | 密码 |
|------|--------|------|
| 普通用户 | 13800138000 | 123456 |
| 门店用户 | 13800138001 | 123456 |
| 管理员 | 13800138002 | 123456 |

## License

Private - 内部项目
