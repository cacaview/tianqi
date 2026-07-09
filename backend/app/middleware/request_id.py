"""
请求 ID 中间件
为每个请求生成唯一的 X-Request-ID，支持跨服务传递
"""

from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger("middleware.request_id")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求分配并传播 request_id"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 优先使用客户端传入的 X-Request-ID，否则生成新的
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # 绑定到 structlog 上下文
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)

        # 将 request_id 添加到响应头
        response.headers["X-Request-ID"] = request_id
        return response
