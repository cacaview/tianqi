"""
MarineDecisionService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.marine_decision_service import MarineDecisionService


@pytest.fixture
def marine_decision_service() -> MarineDecisionService:
    """创建 MarineDecisionService 实例"""
    return MarineDecisionService()


@pytest.mark.asyncio
async def test_assess_route_safe(marine_decision_service: MarineDecisionService) -> None:
    """测试航线评估 — 安全"""
    mock_marine = {
        "latitude": 22.82,
        "longitude": 108.32,
        "timezone": "Asia/Shanghai",
        "wave_height": 0.5,
        "wave_direction": 180,
        "wave_period": 8,
        "wind_wave_height": 0.3,
        "wind_wave_direction": 180,
        "wind_wave_period": 6,
    }

    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(200, json={"current": mock_marine, "timezone": "Asia/Shanghai"})
        )
        result = await marine_decision_service.assess_route(22.82, 108.32, 10.82, 106.63, "zh")

    assert result["overall_decision"] == "go"
    assert result["language"] == "zh"
    assert len(result["checkpoints"]) == 3
    assert result["origin"]["latitude"] == 22.82
    assert result["destination"]["latitude"] == 10.82


@pytest.mark.asyncio
async def test_assess_route_no_go(marine_decision_service: MarineDecisionService) -> None:
    """测试航线评估 — 不可航行"""
    mock_marine = {
        "latitude": 22.82,
        "longitude": 108.32,
        "timezone": "Asia/Shanghai",
        "wave_height": 3.0,  # 超过限制
        "wave_direction": 180,
        "wave_period": 6,
        "wind_wave_height": 2.0,
        "wind_wave_direction": 180,
        "wind_wave_period": 4,
    }

    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(200, json={"current": mock_marine, "timezone": "Asia/Shanghai"})
        )
        result = await marine_decision_service.assess_route(22.82, 108.32, 10.82, 106.63, "zh")

    assert result["overall_decision"] == "no_go"


@pytest.mark.asyncio
async def test_assess_route_caution(marine_decision_service: MarineDecisionService) -> None:
    """测试航线评估 — 注意"""
    mock_marine = {
        "latitude": 22.82,
        "longitude": 108.32,
        "timezone": "Asia/Shanghai",
        "wave_height": 2.0,  # 超过注意阈值
        "wave_direction": 180,
        "wave_period": 7,
        "wind_wave_height": 1.0,
        "wind_wave_direction": 180,
        "wind_wave_period": 5,
    }

    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(200, json={"current": mock_marine, "timezone": "Asia/Shanghai"})
        )
        result = await marine_decision_service.assess_route(22.82, 108.32, 10.82, 106.63, "zh")

    assert result["overall_decision"] == "caution"


@pytest.mark.asyncio
async def test_assess_route_english(marine_decision_service: MarineDecisionService) -> None:
    """测试航线评估 — 英文"""
    mock_marine = {
        "latitude": 22.82,
        "longitude": 108.32,
        "timezone": "Asia/Shanghai",
        "wave_height": 0.5,
        "wave_direction": 180,
        "wave_period": 8,
        "wind_wave_height": 0.3,
    }

    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(200, json={"current": mock_marine, "timezone": "Asia/Shanghai"})
        )
        result = await marine_decision_service.assess_route(22.82, 108.32, 10.82, 106.63, "en")

    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_assess_route_checkpoints(marine_decision_service: MarineDecisionService) -> None:
    """测试航线评估 — 检查点详情"""
    mock_marine = {
        "latitude": 22.82,
        "longitude": 108.32,
        "timezone": "Asia/Shanghai",
        "wave_height": 0.5,
        "wave_direction": 180,
        "wave_period": 8,
        "wind_wave_height": 0.3,
    }

    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(200, json={"current": mock_marine, "timezone": "Asia/Shanghai"})
        )
        result = await marine_decision_service.assess_route(22.82, 108.32, 10.82, 106.63, "zh")

    checkpoints = result["checkpoints"]
    assert len(checkpoints) == 3
    checkpoint_names = [c["name"] for c in checkpoints]
    assert "origin" in checkpoint_names
    assert "midpoint" in checkpoint_names
    assert "destination" in checkpoint_names

    for checkpoint in checkpoints:
        assert "name" in checkpoint
        assert "latitude" in checkpoint
        assert "longitude" in checkpoint
        assert "wave_height" in checkpoint
        assert "decision" in checkpoint
        assert checkpoint["decision"] in ["go", "caution", "no_go"]


@pytest.mark.asyncio
async def test_get_current_condition(marine_decision_service: MarineDecisionService) -> None:
    """测试获取当前位置海况"""
    mock_marine = {
        "latitude": 22.82,
        "longitude": 108.32,
        "timezone": "Asia/Shanghai",
        "wave_height": 1.0,
        "wave_direction": 180,
        "wave_period": 8,
        "wind_wave_height": 0.5,
    }

    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(200, json={"current": mock_marine, "timezone": "Asia/Shanghai"})
        )
        result = await marine_decision_service.get_current_condition(22.82, 108.32)

    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["wave_height"] == 1.0


@pytest.mark.asyncio
async def test_assess_route_http_error(marine_decision_service: MarineDecisionService) -> None:
    """测试航线评估 — HTTP错误"""
    with respx.mock:
        respx.get("https://marine-api.open-meteo.com/v1/marine").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await marine_decision_service.assess_route(22.82, 108.32, 10.82, 106.63, "zh")
