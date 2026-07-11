"""
AgroDecisionService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.agro_decision_service import AgroDecisionService


@pytest.fixture
def agro_service() -> AgroDecisionService:
    return AgroDecisionService()


@pytest.mark.asyncio
async def test_irrigation_advice_dry(agro_service: AgroDecisionService) -> None:
    mock_forecast = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "weather_code": [0, 0, 0],
            "temperature_2m_max": [35.0, 36.0, 34.0],
            "temperature_2m_min": [25.0, 26.0, 24.0],
            "precipitation_sum": [0.0, 0.0, 0.0],
            "precipitation_probability_max": [10, 10, 10],
            "wind_speed_10m_max": [5.0, 5.0, 5.0],
        },
        "hourly": {"temperature_2m": [35.0], "precipitation_probability": [10], "weather_code": [0]},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_forecast))
        result = await agro_service.irrigation_advice(22.82, 108.32, "zh")
    assert result["irrigation_needed"] is True
    assert "灌溉" in result["advice"]
    assert result["language"] == "zh"


@pytest.mark.asyncio
async def test_irrigation_advice_rainy(agro_service: AgroDecisionService) -> None:
    mock_forecast = {
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [61],
            "temperature_2m_max": [25.0],
            "temperature_2m_min": [20.0],
            "precipitation_sum": [20.0],
            "precipitation_probability_max": [90],
            "wind_speed_10m_max": [10.0],
        },
        "hourly": {"temperature_2m": [25.0], "precipitation_probability": [90], "weather_code": [61]},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_forecast))
        result = await agro_service.irrigation_advice(22.82, 108.32, "zh")
    assert result["irrigation_needed"] is False


@pytest.mark.asyncio
async def test_irrigation_advice_english(agro_service: AgroDecisionService) -> None:
    mock_forecast = {
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [0],
            "temperature_2m_max": [30.0],
            "temperature_2m_min": [20.0],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [10],
            "wind_speed_10m_max": [5.0],
        },
        "hourly": {"temperature_2m": [30.0], "precipitation_probability": [10], "weather_code": [0]},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_forecast))
        result = await agro_service.irrigation_advice(22.82, 108.32, "en")
    assert result["language"] == "en"
    assert "irrigation" in result["advice"].lower()


@pytest.mark.asyncio
async def test_irrigation_advice_unknown_lang(agro_service: AgroDecisionService) -> None:
    mock_forecast = {
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [0],
            "temperature_2m_max": [30.0],
            "temperature_2m_min": [20.0],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [10],
            "wind_speed_10m_max": [5.0],
        },
        "hourly": {"temperature_2m": [30.0], "precipitation_probability": [10], "weather_code": [0]},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_forecast))
        result = await agro_service.irrigation_advice(22.82, 108.32, "fr")
    assert result["language"] == "fr"
    # Falls back to English
    assert "irrigation" in result["advice"].lower()


@pytest.mark.asyncio
async def test_irrigation_advice_empty_forecast(agro_service: AgroDecisionService) -> None:
    mock_forecast = {
        "daily": {"time": [], "weather_code": [], "temperature_2m_max": [], "temperature_2m_min": [],
                   "precipitation_sum": [], "precipitation_probability_max": [], "wind_speed_10m_max": []},
        "hourly": {"temperature_2m": [], "precipitation_probability": [], "weather_code": []},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_forecast))
        result = await agro_service.irrigation_advice(22.82, 108.32, "zh")
    assert result["irrigation_needed"] is None
    assert result["advice"] == "数据不足"


@pytest.mark.asyncio
async def test_irrigation_advice_http_error(agro_service: AgroDecisionService) -> None:
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(500))
        with pytest.raises(httpx.HTTPStatusError):
            await agro_service.irrigation_advice(22.82, 108.32)


@pytest.mark.asyncio
async def test_pest_risk_high(agro_service: AgroDecisionService) -> None:
    mock_weather = {
        "current": {"temperature_2m": 25.0, "relative_humidity_2m": 85, "apparent_temperature": 27.0,
                    "precipitation": 0.0, "weather_code": 0, "wind_speed_10m": 5.0, "wind_direction_10m": 180},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_weather))
        result = await agro_service.pest_risk(22.82, 108.32, "zh")
    assert result["risk_level"] == "high"


@pytest.mark.asyncio
async def test_pest_risk_moderate(agro_service: AgroDecisionService) -> None:
    mock_weather = {
        "current": {"temperature_2m": 25.0, "relative_humidity_2m": 65, "apparent_temperature": 27.0,
                    "precipitation": 0.0, "weather_code": 0, "wind_speed_10m": 5.0, "wind_direction_10m": 180},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_weather))
        result = await agro_service.pest_risk(22.82, 108.32, "zh")
    assert result["risk_level"] in ["high", "moderate"]


@pytest.mark.asyncio
async def test_pest_risk_low(agro_service: AgroDecisionService) -> None:
    mock_weather = {
        "current": {"temperature_2m": 15.0, "relative_humidity_2m": 40, "apparent_temperature": 14.0,
                    "precipitation": 0.0, "weather_code": 0, "wind_speed_10m": 10.0, "wind_direction_10m": 180},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_weather))
        result = await agro_service.pest_risk(22.82, 108.32, "zh")
    assert result["risk_level"] == "low"


@pytest.mark.asyncio
async def test_pest_risk_english(agro_service: AgroDecisionService) -> None:
    mock_weather = {
        "current": {"temperature_2m": 15.0, "relative_humidity_2m": 40, "apparent_temperature": 14.0,
                    "precipitation": 0.0, "weather_code": 0, "wind_speed_10m": 10.0, "wind_direction_10m": 180},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_weather))
        result = await agro_service.pest_risk(22.82, 108.32, "en")
    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_harvest_window_with_dry_days(agro_service: AgroDecisionService) -> None:
    mock_forecast = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "weather_code": [0, 1, 61, 0, 0],
            "temperature_2m_max": [28.0, 27.0, 25.0, 29.0, 30.0],
            "temperature_2m_min": [20.0, 19.0, 18.0, 21.0, 22.0],
            "precipitation_sum": [0.0, 0.0, 15.0, 0.0, 0.0],
            "precipitation_probability_max": [10, 20, 80, 10, 10],
            "wind_speed_10m_max": [10.0, 12.0, 15.0, 8.0, 6.0],
        },
        "hourly": {"temperature_2m": [28.0], "precipitation_probability": [10], "weather_code": [0]},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_forecast))
        result = await agro_service.harvest_window(22.82, 108.32, "zh")
    assert result["dry_days"] >= 2
    assert "适合收获" in result["advice"]
    assert result["language"] == "zh"


@pytest.mark.asyncio
async def test_harvest_window_no_dry_days(agro_service: AgroDecisionService) -> None:
    mock_forecast = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02"],
            "weather_code": [61, 63],
            "temperature_2m_max": [25.0, 24.0],
            "temperature_2m_min": [20.0, 19.0],
            "precipitation_sum": [15.0, 20.0],
            "precipitation_probability_max": [90, 95],
            "wind_speed_10m_max": [15.0, 20.0],
        },
        "hourly": {"temperature_2m": [25.0], "precipitation_probability": [90], "weather_code": [61]},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_forecast))
        result = await agro_service.harvest_window(22.82, 108.32, "zh")
    assert result["dry_days"] == 0
    assert result["best_window"] == []


@pytest.mark.asyncio
async def test_harvest_window_english(agro_service: AgroDecisionService) -> None:
    mock_forecast = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02"],
            "weather_code": [0, 1],
            "temperature_2m_max": [28.0, 27.0],
            "temperature_2m_min": [20.0, 19.0],
            "precipitation_sum": [0.0, 0.0],
            "precipitation_probability_max": [10, 20],
            "wind_speed_10m_max": [10.0, 12.0],
        },
        "hourly": {"temperature_2m": [28.0], "precipitation_probability": [10], "weather_code": [0]},
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=mock_forecast))
        result = await agro_service.harvest_window(22.82, 108.32, "en")
    assert result["language"] == "en"
    assert "dry days" in result["advice"]


@pytest.mark.asyncio
async def test_harvest_window_http_error(agro_service: AgroDecisionService) -> None:
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(500))
        with pytest.raises(httpx.HTTPStatusError):
            await agro_service.harvest_window(22.82, 108.32)
