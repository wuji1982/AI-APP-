---
kind: error_handling
name: 基于 FastAPI HTTPException 的轻量级错误处理体系
category: error_handling
scope:
    - '**'
source_files:
    - backend/app/main.py
    - backend/app/database.py
    - backend/app/utils/auth.py
    - backend/app/api/v1/admin.py
    - backend/app/api/v1/auth.py
    - backend/app/agents/base_agent.py
---

## 1. 采用的错误处理方案

本项目采用 **FastAPI 原生 `HTTPException` + Python 内置异常** 的轻量级错误处理模式，未引入自定义异常类、全局异常处理器或统一错误码枚举。错误在 API 层直接抛出，由 FastAPI 自动序列化为 JSON 响应。

## 2. 关键文件与位置

- **应用入口**: `backend/app/main.py` — 仅注册路由与 CORS，**未注册任何全局异常处理器**
- **数据库会话**: `backend/app/database.py` — `get_db()` 依赖中通过 try/except 捕获异常并执行 rollback，然后重新抛出
- **认证工具**: `backend/app/utils/auth.py` — JWT 校验失败时返回 `None`，由调用方判断后抛 `HTTPException(401)`
- **各业务 API**: `backend/app/api/v1/*.py` — 直接在路由函数内 raise `HTTPException`
- **业务服务层**: `backend/app/services/*.py` — 使用 `ValueError` 表达业务校验失败（如余额不足、场次不存在等）
- **Agent 基类**: `backend/app/agents/base_agent.py` — 将异常捕获后包装为 `{status: "error", error: str(e)}` 结构化返回

## 3. 架构与约定

### 3.1 分层错误传播策略

| 层级 | 错误类型 | 处理方式 |
|------|----------|----------|
| Service 层 | `ValueError` / 业务异常 | 抛出异常，不捕获，向上传播 |
| API 层 | 捕获 `ValueError` → `HTTPException(400)`；直接抛 `HTTPException(401/404)` | 转换为 HTTP 响应 |
| DB 层 | `Exception` | 在 `get_db()` 中统一 rollback 后 re-raise |
| Agent 层 | `Exception` | 捕获后返回结构化 `{status, error}`，不向上抛出 |

### 3.2 认证错误集中化
JWT 解码失败返回 `None`，由 `get_current_user_id` 依赖统一抛 `HTTPException(401)`，所有需要鉴权的接口通过 `Depends(get_current_user_id)` 复用。

### 3.3 无全局异常处理器
项目未在 `main.py` 中注册 `@app.exception_handler`，因此：
- 未处理的 `ValueError` 会由 FastAPI 默认处理器转为 `500 Internal Server Error`
- 未设置统一的错误响应格式（如 `{code, message, data}`），不同异常返回结构不一致

## 4. 开发者应遵循的规则

1. **Service 层只抛业务异常**：使用 `ValueError("具体原因")` 描述业务校验失败，不要吞掉异常
2. **API 层负责映射**：捕获 Service 层的 `ValueError` 并转为 `HTTPException(status_code=400, detail=str(e))`；资源不存在用 404，认证失败用 401
3. **不要在中间层随意 try/except**：除 `database.get_db()` 和 Agent 基类外，避免在无关层捕获异常导致错误信息丢失
4. **认证逻辑复用**：通过 `Depends(get_current_user_id)` 获取用户 ID，该依赖已封装 JWT 解析与 401 转换
5. **未来改进建议**：
   - 定义统一错误码枚举与自定义异常基类
   - 在 `main.py` 注册全局异常处理器，统一响应格式为 `{code, message, data}`
   - 对第三方库异常（如 SQLAlchemy IntegrityError）做专门处理