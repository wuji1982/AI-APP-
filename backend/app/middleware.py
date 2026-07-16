"""
全局异常处理与中间件
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """全局异常处理中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except RequestValidationError as e:
            logger.warning(f"请求参数验证失败: {e}")
            return JSONResponse(
                status_code=422,
                content={
                    "code": 422,
                    "message": "请求参数错误",
                    "detail": e.errors()
                }
            )
            
        except SQLAlchemyError as e:
            logger.error(f"数据库错误: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "code": 500,
                    "message": "数据库操作失败",
                    "detail": str(e)
                }
            )
            
        except ValueError as e:
            logger.warning(f"业务逻辑错误: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "code": 400,
                    "message": str(e)
                }
            )
            
        except PermissionError as e:
            logger.warning(f"权限错误: {e}")
            return JSONResponse(
                status_code=403,
                content={
                    "code": 403,
                    "message": "权限不足"
                }
            )
            
        except Exception as e:
            logger.exception(f"未处理的异常: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "code": 500,
                    "message": "服务器内部错误",
                    "detail": str(e)
                }
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        
        logger.info(f"请求开始: {method} {url} - IP: {client_ip}")
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录请求完成
        logger.info(
            f"请求完成: {method} {url} - "
            f"状态码: {response.status_code} - "
            f"耗时: {process_time:.3f}s"
        )
        
        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS中间件（简化版，生产环境建议使用FastAPI内置的CORSMiddleware）"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
