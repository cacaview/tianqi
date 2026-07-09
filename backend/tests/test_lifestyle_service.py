"""
生活指数服务测试
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.main import app
from app.services.lifestyle_service import LifestyleService


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def lifestyle_service() -> LifestyleService:
    return LifestyleService()


# ── 规则引擎单元测试 ──


def test_rule_based_indices_structure(lifestyle_service: LifestyleService) -> None:
    """测试规则引擎返回6个指数"""
    mock_weather = {
        "temperature": 25,
        "humidity": 60,
        "precipitation": 0,
        "wind_speed": 10,
        "weather_code": 2,
        "timezone": "Asia/Shanghai",
    }
    indices = lifestyle_service._get_rule_based_indices(mock_weather, "zh")
    assert len(indices) == 6
    names = [idx["name"] for idx in indices]
    assert names == ["clothing", "car_wash", "exercise", "uv", "umbrella", "tourism"]
    for idx in indices:
        assert "name" in idx
        assert "name_zh" in idx
        assert "level" in idx
        assert "level_zh" in idx
        assert "description" in idx
        assert "icon" in idx


def test_clothing_hot_weather(lifestyle_service: LifestyleService) -> None:
    """测试高温穿衣指数"""
    result = lifestyle_service._clothing_index(36, 5, 0)
    assert result["level"] == "very_hot"
    assert result["level_zh"] == "极热"
    assert result["name"] == "clothing"

    result = lifestyle_service._clothing_index(30, 5, 0)
    assert result["level"] == "light"
    assert result["level_zh"] == "轻薄"


def test_clothing_cold_weather(lifestyle_service: LifestyleService) -> None:
    """测试低温穿衣指数"""
    result = lifestyle_service._clothing_index(5, 20, 0)
    assert result["level"] == "cold"
    assert result["level_zh"] == "寒冷"

    result = lifestyle_service._clothing_index(15, 10, 0)
    assert result["level"] == "warm"
    assert result["level_zh"] == "保暖"


def test_car_wash_rainy(lifestyle_service: LifestyleService) -> None:
    """测试雨天洗车指数"""
    result = lifestyle_service._car_wash_index(2.0, 61)
    assert result["level"] == "not_recommended"
    assert result["level_zh"] == "不宜"

    # High weather_code (rain) even with low precipitation
    result = lifestyle_service._car_wash_index(0, 63)
    assert result["level"] == "not_recommended"


def test_car_wash_sunny(lifestyle_service: LifestyleService) -> None:
    """测试晴天洗车指数"""
    result = lifestyle_service._car_wash_index(0, 0)
    assert result["level"] == "suitable"
    assert result["level_zh"] == "适宜"


def test_umbrella_needed(lifestyle_service: LifestyleService) -> None:
    """测试需要带伞"""
    result = lifestyle_service._umbrella_index(1.0, 61)
    assert result["level"] == "needed"
    assert result["level_zh"] == "需要"

    # Drizzle (weather_code >= 51) even without precipitation
    result = lifestyle_service._umbrella_index(0, 51)
    assert result["level"] == "needed"


def test_umbrella_not_needed(lifestyle_service: LifestyleService) -> None:
    """测试不需要带伞"""
    result = lifestyle_service._umbrella_index(0, 0)
    assert result["level"] == "not_needed"
    assert result["level_zh"] == "不需要"


# ── API 集成测试 ──


@pytest.mark.asyncio
async def test_api_integration() -> None:
    """测试生活指数 API 端点（mock 天气服务）"""
    mock_weather = {
        "temperature": 25.0,
        "humidity": 60,
        "precipitation": 0.0,
        "wind_speed": 10.0,
        "weather_code": 2,
        "wind_direction": 180.0,
        "timezone": "Asia/Shanghai",
        "latitude": 22.82,
        "longitude": 108.32,
        "feels_like": 27.0,
    }

    mock_response = {
        "current": {
            "temperature_2m": 25.0,
            "relative_humidity_2m": 60,
            "apparent_temperature": 27.0,
            "precipitation": 0.0,
            "weather_code": 2,
            "wind_speed_10m": 10.0,
            "wind_direction_10m": 180.0,
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_response))
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/api/weather/lifestyle-indices",
                params={"latitude": 22.82, "longitude": 108.32},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 22.82
    assert data["longitude"] == 108.32
    assert data["generated_by"] == "rules"
    assert len(data["indices"]) == 6
    # Verify structure of first index
    first = data["indices"][0]
    assert first["name"] == "clothing"
    assert "level" in first
    assert "description" in first
