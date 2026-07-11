"""
HistoricalService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

from datetime import date, timedelta

import httpx
import pytest
import respx

from app.services.historical_service import HistoricalService


@pytest.fixture
def historical_service() -> HistoricalService:
    """创建 HistoricalService 实例"""
    return HistoricalService()


@pytest.mark.asyncio
async def test_get_historical_weather_success(historical_service: HistoricalService) -> None:
    """测试获取历史天气 — 正常返回"""
    mock_response = {
        "daily": {
            "time": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "temperature_2m_max": [15.0, 16.5, 14.0],
            "temperature_2m_min": [5.0, 6.5, 4.0],
            "temperature_2m_mean": [10.0, 11.5, 9.0],
            "precipitation_sum": [0.0, 2.5, 5.0],
            "wind_speed_10m_max": [10.0, 12.0, 8.0],
            "weather_code": [1, 3, 61],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await historical_service.get_historical_weather(
            22.82, 108.32, "2023-01-01", "2023-01-03"
        )

    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["timezone"] == "Asia/Shanghai"
    assert result["start_date"] == "2023-01-01"
    assert result["end_date"] == "2023-01-03"
    assert len(result["daily"]) == 3
    assert result["daily"][0]["date"] == "2023-01-01"
    assert result["daily"][0]["temperature_max"] == 15.0
    assert result["daily"][0]["temperature_min"] == 5.0
    assert result["daily"][0]["temperature_mean"] == 10.0
    assert result["daily"][0]["precipitation"] == 0.0
    assert result["daily"][0]["wind_speed_max"] == 10.0
    assert result["daily"][0]["weather_code"] == 1


@pytest.mark.asyncio
async def test_get_historical_weather_http_error(historical_service: HistoricalService) -> None:
    """测试获取历史天气 — HTTP 错误"""
    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await historical_service.get_historical_weather(
                22.82, 108.32, "2023-01-01", "2023-01-03"
            )


@pytest.mark.asyncio
async def test_get_historical_weather_timeout(historical_service: HistoricalService) -> None:
    """测试获取历史天气 — 超时"""
    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            side_effect=httpx.TimeoutException("Connection timeout")
        )
        with pytest.raises(httpx.TimeoutException):
            await historical_service.get_historical_weather(
                22.82, 108.32, "2023-01-01", "2023-01-03"
            )


@pytest.mark.asyncio
async def test_get_historical_weather_network_error(historical_service: HistoricalService) -> None:
    """测试获取历史天气 — 网络错误"""
    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            side_effect=httpx.NetworkError("Network unreachable")
        )
        with pytest.raises(httpx.NetworkError):
            await historical_service.get_historical_weather(
                22.82, 108.32, "2023-01-01", "2023-01-03"
            )


@pytest.mark.asyncio
async def test_get_historical_weather_empty_data(historical_service: HistoricalService) -> None:
    """测试获取历史天气 — 空数据"""
    mock_response = {
        "daily": {
            "time": [],
            "temperature_2m_max": [],
            "temperature_2m_min": [],
            "temperature_2m_mean": [],
            "precipitation_sum": [],
            "wind_speed_10m_max": [],
            "weather_code": [],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await historical_service.get_historical_weather(
            22.82, 108.32, "2023-01-01", "2023-01-01"
        )

    assert len(result["daily"]) == 0


@pytest.mark.asyncio
async def test_get_climate_baseline_success(historical_service: HistoricalService) -> None:
    """测试获取气候基准 — 正常返回"""
    mock_response = {
        "daily": {
            "time": ["2023-01-01", "2023-01-02", "2022-01-01", "2022-01-02"],
            "temperature_2m_max": [15.0, 16.0, 14.0, 15.5],
            "temperature_2m_min": [5.0, 6.0, 4.0, 5.5],
            "temperature_2m_mean": [10.0, 11.0, 9.0, 10.5],
            "precipitation_sum": [0.0, 10.0, 5.0, 2.0],
            "wind_speed_10m_max": [10.0, 15.0, 12.0, 8.0],
            "weather_code": [1, 3, 61, 2],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await historical_service.get_climate_baseline(22.82, 108.32, reference_years=1)

    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["reference_years"] == 1
    assert result["data_points"] == 4
    assert result["baseline"] is not None
    assert "temperature_max" in result["baseline"]
    assert "temperature_min" in result["baseline"]
    assert "precipitation" in result["baseline"]
    assert "wind_speed_max" in result["baseline"]
    assert result["baseline"]["temperature_max"]["mean"] == 15.12
    assert result["baseline"]["temperature_max"]["min"] == 14.0
    assert result["baseline"]["temperature_max"]["max"] == 16.0


@pytest.mark.asyncio
async def test_get_climate_baseline_empty_data(historical_service: HistoricalService) -> None:
    """测试获取气候基准 — 空数据"""
    mock_response = {
        "daily": {
            "time": [],
            "temperature_2m_max": [],
            "temperature_2m_min": [],
            "temperature_2m_mean": [],
            "precipitation_sum": [],
            "wind_speed_10m_max": [],
            "weather_code": [],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await historical_service.get_climate_baseline(22.82, 108.32, reference_years=1)

    assert result["baseline"] is None


@pytest.mark.asyncio
async def test_close_client(historical_service: HistoricalService) -> None:
    """测试关闭HTTP客户端"""
    client = await historical_service._get_client()
    assert not client.is_closed

    await historical_service.close()
    assert client.is_closed


@pytest.mark.asyncio
async def test_close_client_when_not_initialized(historical_service: HistoricalService) -> None:
    """测试关闭未初始化的客户端"""
    await historical_service.close()
    assert historical_service._client is None


@pytest.mark.asyncio
async def test_client_reuse(historical_service: HistoricalService) -> None:
    """测试HTTP客户端复用"""
    client1 = await historical_service._get_client()
    client2 = await historical_service._get_client()

    assert client1 is client2
    assert not client1.is_closed
