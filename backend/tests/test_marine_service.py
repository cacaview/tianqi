"""
MarineService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.marine_service import MarineService


@pytest.fixture
def marine_service() -> MarineService:
    """创建 MarineService 实例"""
    return MarineService()


@pytest.mark.asyncio
async def test_get_marine_forecast_success(marine_service: MarineService) -> None:
    """测试获取海洋气象预报 — 正常返回"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "wave_height_max": [1.5, 2.0, 1.8],
            "wave_direction_dominant": [180, 190, 175],
            "wave_period_max": [8, 10, 9],
            "wind_wave_height_max": [0.8, 1.2, 1.0],
            "swell_wave_height_max": [1.2, 1.8, 1.5],
        },
        "timezone": "Asia/Ho_Chi_Minh",
    }

    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await marine_service.get_marine_forecast(10.82, 106.63, days=3)

    assert result["latitude"] == 10.82
    assert result["longitude"] == 106.63
    assert result["timezone"] == "Asia/Ho_Chi_Minh"
    assert len(result["daily"]) == 3
    assert result["daily"][0]["date"] == "2024-01-01"
    assert result["daily"][0]["wave_height_max"] == 1.5
    assert result["daily"][0]["wave_direction_dominant"] == 180
    assert result["daily"][0]["wave_period_max"] == 8


@pytest.mark.asyncio
async def test_get_marine_forecast_http_error(marine_service: MarineService) -> None:
    """测试获取海洋气象预报 — HTTP 错误"""
    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await marine_service.get_marine_forecast(10.82, 106.63)


@pytest.mark.asyncio
async def test_get_marine_forecast_timeout(marine_service: MarineService) -> None:
    """测试获取海洋气象预报 — 超时"""
    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            side_effect=httpx.TimeoutException("Connection timeout")
        )
        with pytest.raises(httpx.TimeoutException):
            await marine_service.get_marine_forecast(10.82, 106.63)


@pytest.mark.asyncio
async def test_get_marine_forecast_empty_data(marine_service: MarineService) -> None:
    """测试获取海洋气象预报 — 空数据"""
    mock_response = {
        "daily": {
            "time": [],
            "wave_height_max": [],
            "wave_direction_dominant": [],
            "wave_period_max": [],
            "wind_wave_height_max": [],
            "swell_wave_height_max": [],
        },
        "timezone": "Asia/Ho_Chi_Minh",
    }

    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await marine_service.get_marine_forecast(10.82, 106.63, days=0)

    assert len(result["daily"]) == 0


@pytest.mark.asyncio
async def test_get_marine_forecast_with_default_days(marine_service: MarineService) -> None:
    """测试获取海洋气象预报 — 默认天数"""
    mock_response = {
        "daily": {
            "time": [f"2024-01-{i:02d}" for i in range(1, 8)],
            "wave_height_max": [1.5] * 7,
            "wave_direction_dominant": [180] * 7,
            "wave_period_max": [8] * 7,
            "wind_wave_height_max": [0.8] * 7,
            "swell_wave_height_max": [1.2] * 7,
        },
        "timezone": "Asia/Ho_Chi_Minh",
    }

    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await marine_service.get_marine_forecast(10.82, 106.63)

    assert len(result["daily"]) == 7


@pytest.mark.asyncio
async def test_close_client(marine_service: MarineService) -> None:
    """测试关闭HTTP客户端"""
    # 先创建客户端
    client = await marine_service._get_client()
    assert not client.is_closed

    # 关闭客户端
    await marine_service.close()
    assert client.is_closed


@pytest.mark.asyncio
async def test_close_client_when_not_initialized(marine_service: MarineService) -> None:
    """测试关闭未初始化的客户端"""
    # 客户端未初始化时调用close应该不报错
    await marine_service.close()
    assert marine_service._client is None


@pytest.mark.asyncio
async def test_client_reuse(marine_service: MarineService) -> None:
    """测试HTTP客户端复用"""
    client1 = await marine_service._get_client()
    client2 = await marine_service._get_client()

    assert client1 is client2
    assert not client1.is_closed
