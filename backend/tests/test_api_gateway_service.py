"""
ApiGatewayService 单元测试
"""

from __future__ import annotations

import pytest

from app.services.api_gateway_service import ApiGatewayService


@pytest.fixture
def gateway_service() -> ApiGatewayService:
    return ApiGatewayService()


def test_validate_key_valid(gateway_service: ApiGatewayService) -> None:
    """测试API Key验证 — 有效"""
    assert gateway_service.validate_key("a" * 16) is True
    assert gateway_service.validate_key("abcdefghijklmnop") is True


def test_validate_key_too_short(gateway_service: ApiGatewayService) -> None:
    """测试API Key验证 — 太短"""
    assert gateway_service.validate_key("short") is False
    assert gateway_service.validate_key("a" * 15) is False


def test_validate_key_empty(gateway_service: ApiGatewayService) -> None:
    """测试API Key验证 — 空"""
    assert gateway_service.validate_key("") is False
    assert gateway_service.validate_key(None) is False


def test_check_rate_limit_under(gateway_service: ApiGatewayService) -> None:
    """测试限流 — 未超限"""
    api_key = "a" * 20
    assert gateway_service.check_rate_limit(api_key, limit=100) is True


def test_check_rate_limit_exceeded(gateway_service: ApiGatewayService) -> None:
    """测试限流 — 超限"""
    api_key = "a" * 20
    for _ in range(100):
        gateway_service.check_rate_limit(api_key, limit=100)
    assert gateway_service.check_rate_limit(api_key, limit=100) is False


def test_reset_counts(gateway_service: ApiGatewayService) -> None:
    """测试重置计数器"""
    api_key = "a" * 20
    gateway_service.check_rate_limit(api_key)
    gateway_service.reset_counts()
    assert gateway_service._request_counts == {}


def test_get_usage(gateway_service: ApiGatewayService) -> None:
    """测试获取使用量"""
    api_key = "abcdefgh12345678"
    usage = gateway_service.get_usage(api_key)
    assert usage["api_key_prefix"] == "abcdefgh..."
    assert usage["requests_this_minute"] == 0


def test_get_usage_short_key(gateway_service: ApiGatewayService) -> None:
    """测试获取使用量 — 短Key"""
    api_key = "short"
    usage = gateway_service.get_usage(api_key)
    assert usage["api_key_prefix"] == "short"
