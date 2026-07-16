---
kind: configuration_system
name: 基于 pydantic-settings 的环境变量配置体系
category: configuration_system
scope:
    - '**'
source_files:
    - backend/app/config.py
    - backend/.env.example
    - docker-compose.yml
    - nginx.conf
---

## 配置系统概述

本项目采用 pydantic-settings 作为统一配置加载框架，通过 BaseSettings 模型集中管理所有运行时配置项，支持从 .env 文件和 Docker 环境变量中自动注入。

## 核心架构

### 1. 配置定义层 (backend/app/config.py)
- 使用 pydantic_settings.BaseSettings 定义单一 Settings 类，包含全部配置字段
- 每个配置项都有明确的类型注解和默认值，实现配置即文档
- 通过嵌套的 Config 类指定 .env 文件路径和大小写敏感
- 全局单例 settings = Settings() 供全应用共享

### 2. 配置分类组织
配置按功能域分组，主要包含：
- 基础设施: DATABASE_URL、REDIS_URL、CELERY_*、CORS_ORIGINS
- 安全认证: SECRET_KEY、ALGORITHM、ACCESS_TOKEN_EXPIRE_MINUTES
- 对象存储: MINIO_ENDPOINT、MINIO_ACCESS_KEY、MINIO_SECRET_KEY、MINIO_BUCKET
- 业务规则: 拼团参数、贡献值分配比例、分润比例、积分系统等大量业务常量
- AI Agent: LLM_API_KEY、LLM_API_BASE、LLM_MODEL

### 3. 环境隔离策略
- 开发环境: 使用 .env.example 模板 + 本地默认值
- Docker 环境: 通过 docker-compose.yml 的 environment 字段覆盖关键配置（数据库、Redis、RabbitMQ 地址）
- 生产环境: 需复制 .env.example 为 .env 并修改敏感信息

### 4. 反向代理配置 (nginx.conf)
Nginx 作为统一入口，将 /api/ 请求转发到后端服务，预留了 WebSocket 和静态资源代理位置。

## 关键文件
- backend/app/config.py - 主配置类定义
- backend/.env.example - 环境变量模板
- docker-compose.yml - 容器化环境变量注入
- nginx.conf - 反向代理路由配置

## 开发者规范
1. 新增配置项: 在 Settings 类中添加带类型注解的字段，提供合理的默认值
2. 敏感信息: 密钥类配置必须通过环境变量注入，禁止硬编码
3. 业务常量: 业务规则相关配置集中在对应注释区块下，保持可读性
4. 环境差异: 仅保留必要的环境特定配置，其他使用默认值