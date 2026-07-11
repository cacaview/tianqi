"""
ConstructionSafetyService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.construction_safety_service import ConstructionSafetyService


@pytest.fixture
def safety_service() -> ConstructionSafetyService:
    """创建 ConstructionSafetyService 实例"""
    return ConstructionSafetyService()


@pytest.mark.asyncio
async def test_assess_safe_conditions(safety_service: ConstructionSafetyService) -> None:
    """测试施工安全评估 — 安全条件"""
    mock_current = {
        "current": {
            "temperature": 25.0,
            "feels_like": 26.0,
            "wind_speed": 15.0,
            "weather_code": 0,
        },
        "timezone": "Asia/Shanghai",
    }
    mock_forecast = {
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [0],
            "temperature_2m_max": [28.0],
            "temperature_2m_min": [20.0],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [10],
            "wind_speed_10m_max": [15.0],
        },
        "hourly": {
            "temperature_2m": [25.0],
            "precipitation_probability": [10],
            "weather_code": [0],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json={**mock_current, **mock_forecast})
        )
        result = await safety_service.assess(22.82, 108.32, "zh")

    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["overall_decision"] == "go"
    assert result["overall_decision_zh"] == "可以施工"
    assert len(result["factors"]) == 4
    assert result["language"] == "zh"


@pytest.mark.asyncio
async def test_assess_high_wind(safety_service: ConstructionSafetyService) -> None:
    """测试施工安全评估 — 高风速"""
    from unittest.mock import AsyncMock, patch

    mock_forecast = {
        "latitude": 22.82,
        "longitude": 108.32,
        "timezone": "Asia/Shanghai",
        "forecast": [
            {
                "date": "2024-01-01",
                "weather_code": 0,
                "temp_max": 28.0,
                "temp_min": 20.0,
                "precipitation": 0.0,
                "precipitation_probability": 10,
                "wind_speed_max": 50.0,
            }
        ],
    }
    mock_current = {
        "temperature": 25.0,
        "feels_like": 26.0,
        "humidity": 60,
        "wind_speed": 50.0,
        "weather_code": 0,
        "latitude": 22.82,
        "longitude": 108.32,
    }

    with patch.object(safety_service._weather_service, "get_forecast", new_callable=AsyncMock, return_value=mock_forecast):
        with patch.object(safety_service._weather_service, "get_current_weather", new_callable=AsyncMock, return_value=mock_current):
            result = await safety_service.assess(22.82, 108.32, "zh")

    assert result["overall_decision"] == "no_go"
    assert result["overall_decision_zh"] == "建议停工"


@pytest.mark.asyncio
async def test_assess_high_heat(safety_service: ConstructionSafetyService) -> None:
    """测试施工安全评估 — 高温"""
    from unittest.mock import AsyncMock, patch

    mock_forecast = {
        "latitude": 22.82,
        "longitude": 108.32,
        "timezone": "Asia/Shanghai",
        "forecast": [
            {
                "date": "2024-01-01",
                "weather_code": 0,
                "temp_max": 42.0,
                "temp_min": 30.0,
                "precipitation": 0.0,
                "precipitation_probability": 0,
                "wind_speed_max": 10.0,
            }
        ],
    }
    mock_current = {
        "temperature": 42.0,
        "feels_like": 45.0,
        "humidity": 80,
        "wind_speed": 10.0,
        "weather_code": 0,
        "latitude": 22.82,
        "longitude": 108.32,
    }

    with patch.object(safety_service._weather_service, "get_forecast", new_callable=AsyncMock, return_value=mock_forecast):
        with patch.object(safety_service._weather_service, "get_current_weather", new_callable=AsyncMock, return_value=mock_current):
            result = await safety_service.assess(22.82, 108.32, "zh")

    assert result["overall_decision"] == "no_go"


@pytest.mark.asyncio
async def test_assess_lightning(safety_service: ConstructionSafetyService) -> None:
    """测试施工安全评估 — 雷暴"""
    mock_data = {
        "current": {
            "temperature": 25.0,
            "feels_like": 26.0,
            "wind_speed": 10.0,
            "weather_code": 95,  # 雷暴
        },
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [95],
            "temperature_2m_max": [28.0],
            "temperature_2m_min": [20.0],
            "precipitation_sum": [5.0],
            "precipitation_probability_max": [80],
            "wind_speed_10m_max": [15.0],
        },
        "hourly": {
            "temperature_2m": [25.0],
            "precipitation_probability": [80],
            "weather_code": [95],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        result = await safety_service.assess(22.82, 108.32, "zh")

    assert result["overall_decision"] == "no_go"


@pytest.mark.asyncio
async def test_assess_heavy_rain(safety_service: ConstructionSafetyService) -> None:
    """测试施工安全评估 — 强降雨"""
    mock_data = {
        "current": {
            "temperature": 25.0,
            "feels_like": 26.0,
            "wind_speed": 10.0,
            "weather_code": 61,
        },
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [61],
            "temperature_2m_max": [28.0],
            "temperature_2m_min": [20.0],
            "precipitation_sum": [20.0],  # 超过限制
            "precipitation_probability_max": [90],
            "wind_speed_10m_max": [15.0],
        },
        "hourly": {
            "temperature_2m": [25.0],
            "precipitation_probability": [90],
            "weather_code": [61],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        result = await safety_service.assess(22.82, 108.32, "zh")

    assert result["overall_decision"] == "no_go"


@pytest.mark.asyncio
async def test_assess_caution_conditions(safety_service: ConstructionSafetyService) -> None:
    """测试施工安全评估 — 注意条件"""
    from unittest.mock import AsyncMock, patch

    mock_forecast = {
        "latitude": 22.82,
        "longitude": 108.32,
        "timezone": "Asia/Shanghai",
        "forecast": [
            {
                "date": "2024-01-01",
                "weather_code": 0,
                "temp_max": 32.0,
                "temp_min": 25.0,
                "precipitation": 0.0,
                "precipitation_probability": 20,
                "wind_speed_max": 30.0,
            }
        ],
    }
    mock_current = {
        "temperature": 30.0,
        "feels_like": 36.0,
        "humidity": 65,
        "wind_speed": 30.0,
        "weather_code": 0,
        "latitude": 22.82,
        "longitude": 108.32,
    }

    with patch.object(safety_service._weather_service, "get_forecast", new_callable=AsyncMock, return_value=mock_forecast):
        with patch.object(safety_service._weather_service, "get_current_weather", new_callable=AsyncMock, return_value=mock_current):
            result = await safety_service.assess(22.82, 108.32, "en")

    assert result["overall_decision"] == "caution"
    assert result["overall_decision_zh"] == "注意施工"
    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_assess_different_languages(safety_service: ConstructionSafetyService) -> None:
    """测试施工安全评估 — 多语言"""
    mock_data = {
        "current": {
            "temperature": 25.0,
            "feels_like": 26.0,
            "wind_speed": 15.0,
            "weather_code": 0,
        },
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [0],
            "temperature_2m_max": [28.0],
            "temperature_2m_min": [20.0],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [10],
            "wind_speed_10m_max": [15.0],
        },
        "hourly": {
            "temperature_2m": [25.0],
            "precipitation_probability": [10],
            "weather_code": [0],
        },
        "timezone": "Asia/Shanghai",
    }

    languages = ["zh", "en", "vi", "th", "id"]
    for lang in languages:
        with respx.mock:
            respx.get("https://api.open-meteo.com/v1/forecast").mock(
                return_value=httpx.Response(200, json=mock_data)
            )
            result = await safety_service.assess(22.82, 108.32, lang)

        assert result["language"] == lang
        assert "description" in result
        assert len(result["description"]) > 0


@pytest.mark.asyncio
async def test_assess_factors(safety_service: ConstructionSafetyService) -> None:
    """测试施工安全评估 — 因子详情"""
    mock_data = {
        "current": {
            "temperature": 25.0,
            "feels_like": 26.0,
            "wind_speed": 15.0,
            "weather_code": 0,
        },
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [0],
            "temperature_2m_max": [28.0],
            "temperature_2m_min": [20.0],
            "precipitation_sum": [2.0],
            "precipitation_probability_max": [30],
            "wind_speed_10m_max": [15.0],
        },
        "hourly": {
            "temperature_2m": [25.0],
            "precipitation_probability": [30],
            "weather_code": [0],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_data)
        )
        result = await safety_service.assess(22.82, 108.32, "zh")

    assert len(result["factors"]) == 4
    factor_names = [f["name"] for f in result["factors"]]
    assert "wind" in factor_names
    assert "lightning" in factor_names
    assert "heat_stress" in factor_names
    assert "rainfall" in factor_names

    for factor in result["factors"]:
        assert "name" in factor
        assert "name_zh" in factor
        assert "status" in factor
        assert "value" in factor
        assert "detail" in factor


@pytest.mark.asyncio
async def test_assess_http_error(safety_service: ConstructionSafetyService) -> None:
    """测试施工安全评估 — HTTP错误"""
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await safety_service.assess(22.82, 108.32, "zh")
