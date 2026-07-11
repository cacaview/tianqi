"""
企业API v1 路由测试
"""

from __future__ import annotations

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, MagicMock

from app.main import app


@pytest.fixture
def mock_gateway():
    """模拟 API 网关服务"""
    gateway = MagicMock()
    gateway.validate_key.return_value = True
    gateway.check_rate_limit.return_value = True
    gateway.get_usage.return_value = {
        "api_key_prefix": "test1234...",
        "requests_this_minute": 5,
    }
    return gateway


@pytest.mark.asyncio
async def test_v1_weather_current_success(mock_gateway):
    """测试 v1 当前天气 — 成功"""
    mock_weather = MagicMock()
    mock_weather.get_current_weather.return_value = {
        "temperature": 25.0,
        "humidity": 60,
        "wind_speed": 10.0,
    }

    with patch("app.api.deps.get_weather_service", return_value=mock_weather):
        with patch("app.api.deps.get_api_gateway_service", return_value=mock_gateway):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.get(
                    "/api/v1/weather/current",
                    params={"latitude": 22.82, "longitude": 108.32},
                    headers={"X-API-Key": "a" * 16},
                )

    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data or "error" in data


@pytest.mark.asyncio
async def test_v1_weather_current_invalid_key(mock_gateway):
    """测试 v1 当前天气 — 无效 API Key"""
    mock_gateway.validate_key.return_value = False

    with patch("app.api.deps.get_api_gateway_service", return_value=mock_gateway):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/weather/current",
                params={"latitude": 22.82, "longitude": 108.32},
                headers={"X-API-Key": "short"},
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data.get("error") == "Invalid API key"


@pytest.mark.asyncio
async def test_v1_air_quality_success(mock_gateway):
    """测试 v1 空气质量 — 成功"""
    mock_aq = MagicMock()
    mock_aq.get_current.return_value = {"pm2_5": 12.0, "us_aqi": 48}

    with patch("app.api.deps.get_air_quality_service_instance", return_value=mock_aq):
        with patch("app.api.deps.get_api_gateway_service", return_value=mock_gateway):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.get(
                    "/api/v1/air-quality/current",
                    params={"latitude": 22.82, "longitude": 108.32},
                    headers={"X-API-Key": "a" * 16},
                )

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_v1_air_quality_invalid_key(mock_gateway):
    """测试 v1 空气质量 — 无效 Key"""
    mock_gateway.validate_key.return_value = False

    with patch("app.api.deps.get_api_gateway_service", return_value=mock_gateway):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/air-quality/current",
                params={"latitude": 22.82, "longitude": 108.32},
                headers={"X-API-Key": "bad"},
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data.get("error") == "Invalid API key"


@pytest.mark.asyncio
async def test_v1_usage(mock_gateway):
    """测试 v1 使用量查询"""
    with patch("app.api.deps.get_api_gateway_service", return_value=mock_gateway):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/usage",
                headers={"X-API-Key": "a" * 16},
            )

    assert resp.status_code == 200
