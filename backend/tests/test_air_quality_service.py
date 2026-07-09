"""
AirQualityService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.air_quality_service import AirQualityService


@pytest.fixture
def air_quality_service() -> AirQualityService:
    """创建 AirQualityService 实例"""
    return AirQualityService()


@pytest.mark.asyncio
async def test_get_current_air_quality_success(air_quality_service: AirQualityService) -> None:
    """测试获取当前空气质量 — 正常返回"""
    mock_response = {
        "current": {
            "pm10": 25.3,
            "pm2_5": 12.1,
            "carbon_monoxide": 0.4,
            "nitrogen_dioxide": 18.5,
            "sulphur_dioxide": 3.2,
            "ozone": 55.0,
            "us_aqi": 48,
            "european_aqi": 42,
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await air_quality_service.get_current(22.82, 108.32)

    assert result["current"]["pm2_5"] == 12.1
    assert result["current"]["pm10"] == 25.3
    assert result["current"]["us_aqi"] == 48
    assert result["current"]["european_aqi"] == 42
    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["timezone"] == "Asia/Shanghai"


@pytest.mark.asyncio
async def test_get_current_air_quality_http_error(air_quality_service: AirQualityService) -> None:
    """测试获取当前空气质量 — HTTP 错误"""
    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await air_quality_service.get_current(22.82, 108.32)


@pytest.mark.asyncio
async def test_get_forecast_success(air_quality_service: AirQualityService) -> None:
    """测试获取空气质量预报 — 正常返回"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "pm10": [30.0, 28.5, 35.0],
            "pm2_5": [15.0, 12.0, 18.0],
            "carbon_monoxide": [0.5, 0.4, 0.6],
            "nitrogen_dioxide": [20.0, 18.0, 22.0],
            "sulphur_dioxide": [4.0, 3.5, 5.0],
            "ozone": [50.0, 55.0, 48.0],
            "us_aqi": [50, 45, 55],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await air_quality_service.get_forecast(22.82, 108.32, days=3)

    assert len(result["forecast"]) == 3
    assert result["forecast"][0]["date"] == "2024-01-01"
    assert result["forecast"][0]["pm2_5"] == 15.0
    assert result["forecast"][0]["us_aqi"] == 50
    assert result["forecast"][1]["o3"] == 55.0


@pytest.mark.asyncio
async def test_http_client_reuse(air_quality_service: AirQualityService) -> None:
    """测试 httpx 客户端复用"""
    client1 = await air_quality_service._get_client()
    client2 = await air_quality_service._get_client()
    assert client1 is client2
    await air_quality_service.close()
