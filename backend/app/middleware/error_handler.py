"""
全局异常处理器
将应用异常转换为结构化 JSON 响应
"""

from __future__ import annotations

import traceback

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.exceptions import AppError

logger = structlog.get_logger("middleware.error_handler")


def register_error_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """处理应用自定义异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "code": exc.code.value,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """处理请求参数校验失败"""
        errors = []
        for err in exc.errors():
            loc = " → ".join(str(part) for part in err.get("loc", []))
            msg = err.get("msg", "未知错误")
            errors.append(f"{loc}: {msg}")

        return JSONResponse(
            status_code=422,
            content={
                "error": "请求参数校验失败",
                "code": "VALIDATION_ERROR",
                "detail": "; ".join(errors),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """处理 HTTP 异常（404 等）"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": str(exc.detail),
                "code": "HTTP_ERROR",
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """处理未预期的异常"""
        settings = get_settings()
        error_detail = traceback.format_exc() if settings.is_development else None

        # 日志输出
        logger.error("unhandled_error", error_type=type(exc).__name__, error=str(exc))

        return JSONResponse(
            status_code=500,
            content={
                "error": "服务器内部错误",
                "code": "INTERNAL_ERROR",
                "detail": error_detail,
            },
        )
