"""
API 集成测试
使用 httpx AsyncClient 测试端点
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.asyncio
async def test_health_check() -> None:
    """测试健康检查端点"""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "version" in data
    assert "dependencies" in data


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    """测试根路径端点"""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "PolyWind 万语风"
    assert "supported_languages" in data


@pytest.mark.asyncio
async def test_weather_current_with_mock() -> None:
    """测试天气查询端点 — mock Open-Meteo"""
    mock_response = {
        "current": {
            "temperature_2m": 25.0,
            "relative_humidity_2m": 80,
            "apparent_temperature": 27.0,
            "precipitation": 0.0,
            "weather_code": 2,
            "wind_speed_10m": 10.0,
            "wind_direction_10m": 90,
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
                "/api/weather/current",
                params={"latitude": 22.82, "longitude": 108.32},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["temperature"] == 25.0
    assert data["humidity"] == 80


@pytest.mark.asyncio
async def test_weather_current_validation_error() -> None:
    """测试天气查询端点 — 参数校验失败"""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/weather/current",
            params={"latitude": 999, "longitude": 108.32},  # 无效纬度
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_weather_report_with_mock() -> None:
    """测试天气报告端点 — mock Open-Meteo"""
    current_mock = {
        "current": {
            "temperature_2m": 28.0,
            "relative_humidity_2m": 75,
            "apparent_temperature": 30.0,
            "precipitation": 0.0,
            "weather_code": 2,
            "wind_speed_10m": 12.0,
            "wind_direction_100m": 180,
        },
        "timezone": "Asia/Shanghai",
    }
    forecast_mock = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "weather_code": [2, 3, 1],
            "temperature_2m_max": [30, 28, 32],
            "temperature_2m_min": [22, 20, 24],
            "precipitation_sum": [0, 5, 0],
            "precipitation_probability_max": [10, 60, 5],
            "wind_speed_10m_max": [15, 20, 12],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=current_mock))
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/api/weather/report",
                params={"latitude": 22.82, "longitude": 108.32, "language": "zh"},
            )

    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert data["language"] == "zh"
    assert data["generated_by"] == "rules"


@pytest.mark.asyncio
async def test_minutely_precipitation_with_mock() -> None:
    """测试分钟级降水预报端点 — mock Open-Meteo"""
    mock_response = {
        "minutely_15": {
            "time": ["2024-01-01T00:00", "2024-01-01T00:15", "2024-01-01T00:30"],
            "precipitation": [0.0, 0.5, 1.2],
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
                "/api/weather/minutely-precipitation",
                params={"latitude": 22.82, "longitude": 108.32},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data["minutely_15"]) == 3
    assert data["minutely_15"][0]["time"] == "2024-01-01T00:00"
    assert data["minutely_15"][0]["precipitation_mm"] == 0.0
    assert data["minutely_15"][2]["precipitation_mm"] == 1.2
    assert data["latitude"] == 22.82
    assert data["longitude"] == 108.32


@pytest.mark.asyncio
async def test_disaster_typhoons_with_mock() -> None:
    """测试台风端点 — mock NHC"""
    with respx.mock:
        respx.get("https://www.nhc.noaa.gov/CurrentStorms.json").mock(return_value=httpx.Response(500))
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/disaster/typhoons")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # 应回退到模拟数据


@pytest.mark.asyncio
async def test_disaster_typhoon_not_found() -> None:
    """测试台风详情 — 不存在"""
    with respx.mock:
        respx.get("https://www.nhc.noaa.gov/CurrentStorms.json").mock(return_value=httpx.Response(500))
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/disaster/typhoons/NOTEXIST")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chat_send_validation_error() -> None:
    """测试对话端点 — 空消息校验"""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/chat/send",
            json={"message": ""},  # 空消息
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_weather_report_english_with_mock() -> None:
    """测试天气报告端点 — 英文模式"""
    current_mock = {
        "current": {
            "temperature_2m": 25.0,
            "relative_humidity_2m": 60,
            "apparent_temperature": 26.0,
            "precipitation": 0.0,
            "weather_code": 0,
            "wind_speed_10m": 8.0,
            "wind_direction_10m": 180,
        },
        "timezone": "Asia/Shanghai",
    }
    forecast_mock = {
        "daily": {
            "time": ["2024-01-01"],
            "weather_code": [0],
            "temperature_2m_max": [28],
            "temperature_2m_min": [20],
            "precipitation_sum": [0],
            "precipitation_probability_max": [5],
            "wind_speed_10m_max": [12],
        },
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=forecast_mock))
        respx.get("https://api.open-meteo.com/v1/forecast").mock(return_value=httpx.Response(200, json=current_mock))
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/api/weather/report",
                params={"latitude": 22.82, "longitude": 108.32, "language": "en"},
            )
    assert response.status_code == 200
    data = response.json()
    assert "[Weather Report]" in data["report"]


@pytest.mark.asyncio
async def test_air_quality_current_with_mock() -> None:
    """测试空气质量端点 — mock Open-Meteo AQ"""
    mock_response = {
        "current": {
            "pm2_5": 35.2,
            "pm10": 48.1,
            "nitrogen_dioxide": 22.5,
            "carbon_monoxide": 0.8,
            "sulphur_dioxide": 5.3,
            "ozone": 68.2,
            "us_aqi": 98,
            "european_aqi": 72,
        },
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(return_value=httpx.Response(200, json=mock_response))
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/api/air-quality/current",
                params={"latitude": 22.82, "longitude": 108.32},
            )
    assert response.status_code == 200
    data = response.json()
    assert data["current"]["us_aqi"] == 98
    assert data["current"]["pm2_5"] == 35.2


@pytest.mark.asyncio
async def test_lifestyle_indices_with_mock() -> None:
    """测试生活指数端点 — mock Open-Meteo"""
    mock_response = {
        "current": {
            "temperature_2m": 28.0,
            "relative_humidity_2m": 75,
            "apparent_temperature": 30.0,
            "precipitation": 0.0,
            "weather_code": 2,
            "wind_speed_10m": 12.0,
            "wind_direction_10m": 180,
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
                params={"latitude": 22.82, "longitude": 108.32, "language": "zh"},
            )
    assert response.status_code == 200
    data = response.json()
    assert len(data["indices"]) == 6
    assert data["generated_by"] == "rules"


@pytest.mark.asyncio
async def test_earthquake_endpoint_with_mock() -> None:
    """测试地震列表端点 — mock Wolfx"""
    with respx.mock:
        respx.get("https://api.wolfx.jp/cenc_eqlist.json").mock(
            return_value=httpx.Response(200, json={"time": "2024-01-01"})
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/api/disaster/earthquakes",
                params={"source": "cenc"},
            )
    assert response.status_code == 200
