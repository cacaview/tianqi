"""
企业气象APIaaS网关服务 MVP
API Key认证 + 简单计数限流
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger("services.api_gateway")


class ApiGatewayService:
    """企业气象APIaaS网关服务"""

    def __init__(self) -> None:
        self._request_counts: dict[str, int] = {}

    def validate_key(self, api_key: str) -> bool:
        """验证API Key（简化MVP版本）"""
        return bool(api_key and len(api_key) >= 16)

    def check_rate_limit(self, api_key: str, limit: int = 100) -> bool:
        """检查是否超限流"""
        count = self._request_counts.get(api_key, 0)
        if count >= limit:
            return False
        self._request_counts[api_key] = count + 1
        return True

    def reset_counts(self) -> None:
        """重置计数器（每分钟调用）"""
        self._request_counts.clear()

    def get_usage(self, api_key: str) -> dict:
        """获取使用量"""
        return {
            "api_key_prefix": api_key[:8] + "..." if len(api_key) > 8 else api_key,
            "requests_this_minute": self._request_counts.get(api_key, 0),
        }
