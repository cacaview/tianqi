"""
FloodService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.flood_service import FloodService


@pytest.fixture
def flood_service() -> FloodService:
    """创建 FloodService 实例"""
    return FloodService()


@pytest.mark.asyncio
async def test_get_river_discharge_success(flood_service: FloodService) -> None:
    """测试获取河流流量 — 正常返回"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "river_discharge": [150.5, 200.3, 180.0],
            "river_discharge_mean": [120.0, 130.0, 125.0],
            "river_discharge_max": [180.0, 250.0, 200.0],
            "river_discharge_min": [100.0, 150.0, 130.0],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://flood-api.open-meteo.com/v1/flood").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await flood_service.get_river_discharge(22.82, 108.32)

    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["timezone"] == "Asia/Shanghai"
    assert len(result["daily"]) == 3
    assert result["daily"][0]["date"] == "2024-01-01"
    assert result["daily"][0]["river_discharge"] == 150.5
    assert result["daily"][0]["river_discharge_mean"] == 120.0


@pytest.mark.asyncio
async def test_get_river_discharge_http_error(flood_service: FloodService) -> None:
    """测试获取河流流量 — HTTP 错误"""
    with respx.mock:
        respx.get("https://flood-api.open-meteo.com/v1/flood").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await flood_service.get_river_discharge(22.82, 108.32)


@pytest.mark.asyncio
async def test_get_river_discharge_timeout(flood_service: FloodService) -> None:
    """测试获取河流流量 — 超时"""
    with respx.mock:
        respx.get("https://flood-api.open-meteo.com/v1/flood").mock(
            side_effect=httpx.TimeoutException("Connection timeout")
        )
        with pytest.raises(httpx.TimeoutException):
            await flood_service.get_river_discharge(22.82, 108.32)


@pytest.mark.asyncio
async def test_get_river_discharge_network_error(flood_service: FloodService) -> None:
    """测试获取河流流量 — 网络错误"""
    with respx.mock:
        respx.get("https://flood-api.open-meteo.com/v1/flood").mock(
            side_effect=httpx.NetworkError("Network unreachable")
        )
        with pytest.raises(httpx.NetworkError):
            await flood_service.get_river_discharge(22.82, 108.32)


@pytest.mark.asyncio
async def test_get_river_discharge_empty_data(flood_service: FloodService) -> None:
    """测试获取河流流量 — 空数据"""
    mock_response = {
        "daily": {
            "time": [],
            "river_discharge": [],
            "river_discharge_mean": [],
            "river_discharge_max": [],
            "river_discharge_min": [],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://flood-api.open-meteo.com/v1/flood").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await flood_service.get_river_discharge(22.82, 108.32)

    assert len(result["daily"]) == 0


@pytest.mark.asyncio
async def test_close_client(flood_service: FloodService) -> None:
    """测试关闭HTTP客户端"""
    # 先创建客户端
    client = await flood_service._get_client()
    assert not client.is_closed

    # 关闭客户端
    await flood_service.close()
    assert client.is_closed


@pytest.mark.asyncio
async def test_close_client_when_not_initialized(flood_service: FloodService) -> None:
    """测试关闭未初始化的客户端"""
    # 客户端未初始化时调用close应该不报错
    await flood_service.close()
    assert flood_service._client is None


@pytest.mark.asyncio
async def test_client_reuse(flood_service: FloodService) -> None:
    """测试HTTP客户端复用"""
    client1 = await flood_service._get_client()
    client2 = await flood_service._get_client()

    assert client1 is client2
    assert not client1.is_closed


@pytest.mark.asyncio
async def test_get_flood_risk_high(flood_service: FloodService) -> None:
    """测试洪水风险评估 — 高风险"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "river_discharge": [100.0, 120.0, 600.0],
            "river_discharge_mean": [120.0, 130.0, 125.0],
            "river_discharge_max": [180.0, 250.0, 600.0],
            "river_discharge_min": [100.0, 150.0, 200.0],
        },
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://flood-api.open-meteo.com/v1/flood").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await flood_service.get_flood_risk(22.82, 108.32)
    assert result["risk_level"] == "high"
    assert result["trend"] == "rising"
    assert result["latitude"] == 22.82


@pytest.mark.asyncio
async def test_get_flood_risk_moderate(flood_service: FloodService) -> None:
    """测试洪水风险评估 — 中等风险"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02"],
            "river_discharge": [100.0, 180.0],
            "river_discharge_mean": [120.0, 130.0],
            "river_discharge_max": [180.0, 250.0],
            "river_discharge_min": [100.0, 150.0],
        },
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://flood-api.open-meteo.com/v1/flood").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await flood_service.get_flood_risk(22.82, 108.32)
    assert result["risk_level"] in ["moderate", "low"]
    assert result["latitude"] == 22.82


@pytest.mark.asyncio
async def test_get_flood_risk_low(flood_service: FloodService) -> None:
    """测试洪水风险评估 — 低风险"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "river_discharge": [120.0, 122.0, 118.0],
            "river_discharge_mean": [120.0, 130.0, 125.0],
            "river_discharge_max": [180.0, 200.0, 190.0],
            "river_discharge_min": [100.0, 100.0, 100.0],
        },
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://flood-api.open-meteo.com/v1/flood").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await flood_service.get_flood_risk(22.82, 108.32)
    assert result["risk_level"] == "low"
    assert result["trend"] == "stable"


@pytest.mark.asyncio
async def test_get_flood_risk_empty_data(flood_service: FloodService) -> None:
    """测试洪水风险评估 — 空数据"""
    mock_response = {
        "daily": {
            "time": [],
            "river_discharge": [],
            "river_discharge_mean": [],
            "river_discharge_max": [],
            "river_discharge_min": [],
        },
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://flood-api.open-meteo.com/v1/flood").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await flood_service.get_flood_risk(22.82, 108.32)
    assert result["risk_level"] == "unknown"
    assert "message" in result


@pytest.mark.asyncio
async def test_get_flood_risk_null_discharge(flood_service: FloodService) -> None:
    """测试洪水风险评估 — 流量为None"""
    mock_response = {
        "daily": {
            "time": ["2024-01-01", "2024-01-02"],
            "river_discharge": [None, None],
            "river_discharge_mean": [120.0, 130.0],
            "river_discharge_max": [180.0, 250.0],
            "river_discharge_min": [100.0, 150.0],
        },
        "timezone": "Asia/Shanghai",
    }
    with respx.mock:
        respx.get("https://flood-api.open-meteo.com/v1/flood").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await flood_service.get_flood_risk(22.82, 108.32)
    assert result["risk_level"] == "unknown"
