"""
EnergyForecastService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.energy_forecast_service import EnergyForecastService


@pytest.fixture
def energy_service() -> EnergyForecastService:
    """创建 EnergyForecastService 实例"""
    return EnergyForecastService()


@pytest.mark.asyncio
async def test_solar_forecast_success(energy_service: EnergyForecastService) -> None:
    """测试太阳能发电预测 — 正常返回"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "weather_code": [0, 1, 3],
            "temperature_2m_max": [28.0, 25.0, 22.0],
            "temperature_2m_min": [20.0, 18.0, 15.0],
            "precipitation_sum": [0.0, 0.0, 5.0],
            "precipitation_probability_max": [10, 20, 50],
            "wind_speed_10m_max": [10.0, 12.0, 15.0],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await energy_service.solar_forecast(22.82, 108.32, capacity_kw=10.0, days=3)

    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["capacity_kw"] == 10.0
    assert result["efficiency"] == 0.17
    assert len(result["forecast"]) == 3

    # 验证第一天（晴天，28°C）
    day1 = result["forecast"][0]
    assert day1["date"] == "2024-01-01"
    assert day1["weather_code"] == 0
    assert day1["estimated_radiation_wm2"] == 800.0
    assert day1["temperature_factor"] == 0.988  # 1.0 + (-0.004) * (28-25) = 0.988
    assert day1["daily_output_kwh"] > 0

    # 验证第二天（大部晴朗）
    day2 = result["forecast"][1]
    assert day2["estimated_radiation_wm2"] == 600.0

    # 验证第三天（多云）
    day3 = result["forecast"][2]
    assert day3["estimated_radiation_wm2"] == 400.0


@pytest.mark.asyncio
async def test_solar_forecast_high_temperature(energy_service: EnergyForecastService) -> None:
    """测试太阳能发电预测 — 高温修正"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [0],
            "temperature_2m_max": [35.0],
            "temperature_2m_min": [25.0],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [0],
            "wind_speed_10m_max": [5.0],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await energy_service.solar_forecast(22.82, 108.32, capacity_kw=10.0, days=1)

    day = result["forecast"][0]
    assert day["temperature_factor"] < 1.0  # 高温应该降低效率
    assert day["temperature_factor"] == 0.96  # 1.0 + (-0.004) * (35-25) = 0.96


@pytest.mark.asyncio
async def test_solar_forecast_http_error(energy_service: EnergyForecastService) -> None:
    """测试太阳能发电预测 — HTTP错误"""
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await energy_service.solar_forecast(22.82, 108.32)


@pytest.mark.asyncio
async def test_wind_power_forecast_success(energy_service: EnergyForecastService) -> None:
    """测试风力发电预测 — 正常返回"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "weather_code": [0, 1, 3],
            "temperature_2m_max": [28.0, 25.0, 22.0],
            "temperature_2m_min": [20.0, 18.0, 15.0],
            "precipitation_sum": [0.0, 0.0, 5.0],
            "precipitation_probability_max": [10, 20, 50],
            "wind_speed_10m_max": [10.0, 15.0, 20.0],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await energy_service.wind_power_forecast(22.82, 108.32, rated_power_kw=100.0, days=3)

    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["rated_power_kw"] == 100.0
    assert len(result["forecast"]) == 3

    # 验证第一天（风速10 km/h = 2.78 m/s，低于切入风速3 m/s）
    day1 = result["forecast"][0]
    assert day1["date"] == "2024-01-01"
    assert day1["wind_speed_kmh"] == 10.0
    assert day1["power_ratio"] == 0.0  # 低于切入风速
    assert day1["daily_output_kwh"] == 0.0

    # 验证第二天（风速15 km/h = 4.17 m/s，在工作范围内）
    day2 = result["forecast"][1]
    assert day2["wind_speed_kmh"] == 15.0
    assert day2["power_ratio"] > 0
    assert day2["power_ratio"] < 1.0
    assert day2["daily_output_kwh"] > 0

    # 验证第三天（风速20 km/h = 5.56 m/s，更接近额定功率）
    day3 = result["forecast"][2]
    assert day3["wind_speed_kmh"] == 20.0
    assert day3["power_ratio"] > day2["power_ratio"]


@pytest.mark.asyncio
async def test_wind_power_forecast_high_wind(energy_service: EnergyForecastService) -> None:
    """测试风力发电预测 — 高风速（额定功率）"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [0],
            "temperature_2m_max": [25.0],
            "temperature_2m_min": [15.0],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [0],
            "wind_speed_10m_max": [50.0],  # 50 km/h = 13.89 m/s，超过额定风速
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await energy_service.wind_power_forecast(22.82, 108.32, rated_power_kw=100.0, days=1)

    day = result["forecast"][0]
    assert day["power_ratio"] == 1.0  # 达到额定功率
    assert day["daily_output_kwh"] == 2400.0  # 100kW * 1.0 * 24h


@pytest.mark.asyncio
async def test_wind_power_forecast_storm(energy_service: EnergyForecastService) -> None:
    """测试风力发电预测 — 暴风（切出）"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [95],
            "temperature_2m_max": [20.0],
            "temperature_2m_min": [15.0],
            "precipitation_sum": [20.0],
            "precipitation_probability_max": [90],
            "wind_speed_10m_max": [100.0],  # 100 km/h = 27.78 m/s，超过切出风速
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await energy_service.wind_power_forecast(22.82, 108.32, rated_power_kw=100.0, days=1)

    day = result["forecast"][0]
    assert day["power_ratio"] == 0.0  # 超过切出风速，停机保护
    assert day["daily_output_kwh"] == 0.0


@pytest.mark.asyncio
async def test_wind_power_forecast_http_error(energy_service: EnergyForecastService) -> None:
    """测试风力发电预测 — HTTP错误"""
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await energy_service.wind_power_forecast(22.82, 108.32)


@pytest.mark.asyncio
async def test_solar_forecast_empty_data(energy_service: EnergyForecastService) -> None:
    """测试太阳能发电预测 — 空数据"""
    mock_response = {
        "daily": {
            "time": [],
            "weather_code": [],
            "temperature_2m_max": [],
            "temperature_2m_min": [],
            "precipitation_sum": [],
            "precipitation_probability_max": [],
            "wind_speed_10m_max": [],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await energy_service.solar_forecast(22.82, 108.32, capacity_kw=10.0, days=0)

    assert len(result["forecast"]) == 0


@pytest.mark.asyncio
async def test_wind_power_forecast_empty_data(energy_service: EnergyForecastService) -> None:
    """测试风力发电预测 — 空数据"""
    mock_response = {
        "daily": {
            "time": [],
            "weather_code": [],
            "temperature_2m_max": [],
            "temperature_2m_min": [],
            "precipitation_sum": [],
            "precipitation_probability_max": [],
            "wind_speed_10m_max": [],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await energy_service.wind_power_forecast(22.82, 108.32, rated_power_kw=100.0, days=0)

    assert len(result["forecast"]) == 0
