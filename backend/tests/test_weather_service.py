"""
WeatherService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.weather_service import WeatherService


@pytest.fixture
def weather_service() -> WeatherService:
    """创建 WeatherService 实例"""
    return WeatherService()


@pytest.mark.asyncio
async def test_get_current_weather_success(weather_service: WeatherService) -> None:
    """测试获取当前天气 — 正常返回"""
    mock_response = {
        "current": {
            "temperature_2m": 28.5,
            "relative_humidity_2m": 75,
            "apparent_temperature": 30.2,
            "precipitation": 0.0,
            "weather_code": 1,
            "wind_speed_10m": 12.3,
            "wind_direction_10m": 180,
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_response))
        result = await weather_service.get_current_weather(22.82, 108.32)

    assert result["temperature"] == 28.5
    assert result["humidity"] == 75
    assert result["wind_speed"] == 12.3
    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["timezone"] == "Asia/Shanghai"


@pytest.mark.asyncio
async def test_get_current_weather_http_error(weather_service: WeatherService) -> None:
    """测试获取当前天气 — HTTP 错误"""
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await weather_service.get_current_weather(22.82, 108.32)


@pytest.mark.asyncio
async def test_get_forecast_success(weather_service: WeatherService) -> None:
    """测试获取天气预报 — 正常返回"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02"],
            "weather_code": [1, 3],
            "temperature_2m_max": [28.0, 26.5],
            "temperature_2m_min": [20.0, 18.5],
            "precipitation_sum": [0.0, 5.2],
            "precipitation_probability_max": [10, 80],
            "wind_speed_10m_max": [15.0, 20.0],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_response))
        result = await weather_service.get_forecast(22.82, 108.32, days=2)

    assert len(result["forecast"]) == 2
    assert result["forecast"][0]["date"] == "2024-01-01"
    assert result["forecast"][0]["temp_max"] == 28.0
    assert result["forecast"][1]["precipitation"] == 5.2


@pytest.mark.asyncio
async def test_get_minutely_precipitation_success(weather_service: WeatherService) -> None:
    """测试获取分钟级降水预报 — 正常返回"""
    mock_response = {
        "minutely_15": {
            "time": ["2024-01-01T00:00", "2024-01-01T00:15", "2024-01-01T00:30"],
            "precipitation": [0.0, 0.5, 1.2],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_response))
        result = await weather_service.get_minutely_precipitation(22.82, 108.32)

    assert len(result["minutely_15"]) == 3
    assert result["minutely_15"][0]["time"] == "2024-01-01T00:00"
    assert result["minutely_15"][0]["precipitation_mm"] == 0.0
    assert result["minutely_15"][1]["precipitation_mm"] == 0.5
    assert result["minutely_15"][2]["precipitation_mm"] == 1.2
    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["timezone"] == "Asia/Shanghai"


def test_get_asean_cities(weather_service: WeatherService) -> None:
    """测试获取东盟城市列表"""
    cities = weather_service.get_asean_cities()

    assert "nanning" in cities
    assert "bangkok" in cities
    assert cities["nanning"]["name"] == "南宁"
    assert cities["bangkok"]["lat"] == 13.76


@pytest.mark.asyncio
async def test_http_client_reuse(weather_service: WeatherService) -> None:
    """测试 httpx 客户端复用"""
    client1 = await weather_service._get_client()
    client2 = await weather_service._get_client()
    assert client1 is client2
    await weather_service.close()
