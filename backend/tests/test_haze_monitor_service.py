"""
HazeMonitorService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.haze_monitor_service import HazeMonitorService


@pytest.fixture
def haze_service() -> HazeMonitorService:
    """创建 HazeMonitorService 实例"""
    return HazeMonitorService()


@pytest.mark.asyncio
async def test_get_fire_hotspots_no_api_key(haze_service: HazeMonitorService) -> None:
    """测试获取火点数据 — 无API Key（模拟）"""
    # 由于Settings对象没有NASA_FIRMS_API_KEY字段，直接测试异常处理
    result = await haze_service.get_fire_hotspots("sumatra", 7)

    # 当没有配置API Key时，应该返回mock数据
    assert result["region"] == "sumatra"
    assert result["mock"] is True


@pytest.mark.asyncio
async def test_get_fire_hotspots_sumatra(haze_service: HazeMonitorService) -> None:
    """测试获取火点数据 — 苏门答腊区域"""
    result = await haze_service.get_fire_hotspots("sumatra", 7)
    assert result["region"] == "sumatra"


@pytest.mark.asyncio
async def test_get_fire_hotspots_borneo(haze_service: HazeMonitorService) -> None:
    """测试获取火点数据 — 婆罗洲区域"""
    result = await haze_service.get_fire_hotspots("borneo", 7)
    assert result["region"] == "borneo"


@pytest.mark.asyncio
async def test_get_fire_hotspots_mainland(haze_service: HazeMonitorService) -> None:
    """测试获取火点数据 — 中南半岛区域"""
    result = await haze_service.get_fire_hotspots("mainland_sea", 7)
    assert result["region"] == "mainland_sea"


@pytest.mark.asyncio
async def test_get_aqi_stations_success(haze_service: HazeMonitorService) -> None:
    """测试获取AQI站点数据"""
    mock_response = {
        "current": {
            "pm10": 50,
            "pm2_5": 35,
            "carbon_monoxide": 0.5,
            "nitrogen_dioxide": 20,
            "sulphur_dioxide": 10,
            "ozone": 30,
            "us_aqi": 85,
            "european_aqi": 75,
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await haze_service.get_aqi_stations(22.82, 108.32)

    assert result["current"]["us_aqi"] == 85
    assert result["current"]["pm2_5"] == 35


@pytest.mark.asyncio
async def test_get_haze_level_good(haze_service: HazeMonitorService) -> None:
    """测试烟霾等级评估 — 优"""
    mock_response = {
        "current": {"us_aqi": 30},
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await haze_service.get_haze_level(22.82, 108.32, "zh")

    assert result["us_aqi"] == 30
    assert result["haze_level"] == "good"
    assert result["haze_level_zh"] == "优"
    assert result["language"] == "zh"


@pytest.mark.asyncio
async def test_get_haze_level_moderate(haze_service: HazeMonitorService) -> None:
    """测试烟霾等级评估 — 良"""
    mock_response = {
        "current": {"us_aqi": 80},
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await haze_service.get_haze_level(22.82, 108.32, "zh")

    assert result["haze_level"] == "moderate"
    assert result["haze_level_zh"] == "良"


@pytest.mark.asyncio
async def test_get_haze_level_unhealthy_sensitive(haze_service: HazeMonitorService) -> None:
    """测试烟霾等级评估 — 轻度污染"""
    mock_response = {
        "current": {"us_aqi": 120},
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await haze_service.get_haze_level(22.82, 108.32, "zh")

    assert result["haze_level"] == "unhealthy_sensitive"
    assert result["haze_level_zh"] == "轻度污染"


@pytest.mark.asyncio
async def test_get_haze_level_unhealthy(haze_service: HazeMonitorService) -> None:
    """测试烟霾等级评估 — 中度污染"""
    mock_response = {
        "current": {"us_aqi": 180},
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await haze_service.get_haze_level(22.82, 108.32, "zh")

    assert result["haze_level"] == "unhealthy"
    assert result["haze_level_zh"] == "中度污染"


@pytest.mark.asyncio
async def test_get_haze_level_very_unhealthy(haze_service: HazeMonitorService) -> None:
    """测试烟霾等级评估 — 重度污染"""
    mock_response = {
        "current": {"us_aqi": 250},
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await haze_service.get_haze_level(22.82, 108.32, "zh")

    assert result["haze_level"] == "very_unhealthy"
    assert result["haze_level_zh"] == "重度污染"


@pytest.mark.asyncio
async def test_get_haze_level_hazardous(haze_service: HazeMonitorService) -> None:
    """测试烟霾等级评估 — 严重污染"""
    mock_response = {
        "current": {"us_aqi": 350},
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await haze_service.get_haze_level(22.82, 108.32, "zh")

    assert result["haze_level"] == "hazardous"
    assert result["haze_level_zh"] == "严重污染"


@pytest.mark.asyncio
async def test_get_haze_level_with_null_aqi(haze_service: HazeMonitorService) -> None:
    """测试烟霾等级评估 — AQI为None"""
    mock_response = {
        "current": {"us_aqi": None},
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await haze_service.get_haze_level(22.82, 108.32, "en")

    assert result["us_aqi"] == 0
    assert result["haze_level"] == "good"
    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_close_client(haze_service: HazeMonitorService) -> None:
    """测试关闭HTTP客户端"""
    client = await haze_service._get_client()
    assert not client.is_closed

    await haze_service.close()
    assert client.is_closed


@pytest.mark.asyncio
async def test_close_client_when_not_initialized(haze_service: HazeMonitorService) -> None:
    """测试关闭未初始化的客户端"""
    await haze_service.close()
    assert haze_service._client is None


@pytest.mark.asyncio
async def test_client_reuse(haze_service: HazeMonitorService) -> None:
    """测试HTTP客户端复用"""
    client1 = await haze_service._get_client()
    client2 = await haze_service._get_client()

    assert client1 is client2
    assert not client1.is_closed
