"""
安全中间件 — 安全响应头 + API Key 脱敏
"""

from __future__ import annotations

import re

from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """为所有响应添加安全 HTTP 头"""

    SECURITY_HEADERS: dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        for header, value in self.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response


# ── 敏感信息脱敏工具 ──

# 匹配 API Key 模式
_SENSITIVE_PATTERNS: list[re.Pattern] = [
    re.compile(r"(sk-[a-zA-Z0-9]{20,})", re.IGNORECASE),  # OpenAI style
    re.compile(r"(key[=:]\s*[a-zA-Z0-9]{16,})", re.IGNORECASE),  # Generic API key
    re.compile(r"(Bearer\s+[a-zA-Z0-9\-._~+/]+=*)", re.IGNORECASE),  # Bearer token
]

_MASK = r"\1"[:4] + "***"  # 保留前4个字符


def mask_sensitive(text: str) -> str:
    """遮蔽字符串中的敏感信息"""
    result = text
    for pattern in _SENSITIVE_PATTERNS:
        result = pattern.sub(_MASK, result)
    return result


def register_security_middleware(app: FastAPI) -> None:
    """注册安全中间件"""
    # 安全响应头
    app.add_middleware(SecurityHeadersMiddleware)
