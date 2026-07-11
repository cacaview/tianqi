"""
CrossBorderService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.cross_border_service import CrossBorderService


@pytest.fixture
def cross_border_service() -> CrossBorderService:
    """创建 CrossBorderService 实例"""
    return CrossBorderService()


@pytest.mark.asyncio
async def test_correlate_events_success(cross_border_service: CrossBorderService) -> None:
    """测试关联分析 — 成功"""
    from unittest.mock import AsyncMock, patch

    mock_alerts = {
        "alerts": [
            {"type": "rain", "level": "orange", "title": "暴雨预警"},
        ],
        "total": 1,
        "by_level": {"red": 0, "orange": 1, "yellow": 0, "blue": 0},
    }
    mock_earthquakes = {
        "earthquakes": [
            {"magnitude": 5.0, "hypocenter": "云南", "occurred_at": "2024-01-01T00:00:00"},
        ],
        "total": 1,
    }

    with patch.object(cross_border_service._disaster_service, "get_alerts", new_callable=AsyncMock, return_value=mock_alerts):
        with patch.object(cross_border_service._earthquake_service, "get_earthquakes", new_callable=AsyncMock, return_value=mock_earthquakes):
            result = await cross_border_service.correlate_events(48, "zh")

    assert result["time_window_hours"] == 48
    assert result["language"] == "zh"
    assert "regions_with_alerts" in result
    assert "correlations" in result
    assert "earthquake_count" in result


@pytest.mark.asyncio
async def test_correlate_events_with_correlations(cross_border_service: CrossBorderService) -> None:
    """测试关联分析 — 有关联事件"""
    from unittest.mock import AsyncMock, patch

    # Mock alerts and earthquakes
    mock_alerts = {
        "alerts": [{"type": "rain", "level": "orange", "title": "暴雨预警"}],
        "total": 1,
        "by_level": {"red": 0, "orange": 1, "yellow": 0, "blue": 0},
    }
    mock_earthquakes = {
        "earthquakes": [
            {"magnitude": 6.5, "hypocenter": "菲律宾", "occurred_at": "2024-01-01T00:00:00"},
        ],
        "total": 1,
    }

    with patch.object(cross_border_service._disaster_service, "get_alerts", new_callable=AsyncMock, return_value=mock_alerts):
        with patch.object(cross_border_service._earthquake_service, "get_earthquakes", new_callable=AsyncMock, return_value=mock_earthquakes):
            result = await cross_border_service.correlate_events(48, "zh")

    assert len(result["correlations"]) > 0
    # 应该有地震关联
    earthquake_corr = [c for c in result["correlations"] if c["type"] == "earthquake"]
    assert len(earthquake_corr) > 0
    assert earthquake_corr[0]["magnitude"] == 6.5
    assert earthquake_corr[0]["severity"] == "high"


@pytest.mark.asyncio
async def test_correlate_events_no_alerts(cross_border_service: CrossBorderService) -> None:
    """测试关联分析 — 无预警"""
    from unittest.mock import AsyncMock, patch

    mock_alerts = {
        "alerts": [],
        "total": 0,
        "by_level": {"red": 0, "orange": 0, "yellow": 0, "blue": 0},
    }
    mock_earthquakes = {
        "earthquakes": [],
        "total": 0,
    }

    with patch.object(cross_border_service._disaster_service, "get_alerts", new_callable=AsyncMock, return_value=mock_alerts):
        with patch.object(cross_border_service._earthquake_service, "get_earthquakes", new_callable=AsyncMock, return_value=mock_earthquakes):
            result = await cross_border_service.correlate_events(48, "en")

    assert result["total_alerts"] == 0
    assert result["earthquake_count"] == 0
    assert len(result["correlations"]) == 0
    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_impact_chain_typhoon(cross_border_service: CrossBorderService) -> None:
    """测试灾害影响链 — 台风"""
    result = await cross_border_service.impact_chain("typhoon", "zh")

    assert result["disaster_type"] == "typhoon"
    assert result["language"] == "zh"
    assert "impact_chain" in result
    assert len(result["impact_chain"]) > 0
    assert result["impact_chain"][0]["stage"] == 1


@pytest.mark.asyncio
async def test_impact_chain_flood(cross_border_service: CrossBorderService) -> None:
    """测试灾害影响链 — 洪水"""
    result = await cross_border_service.impact_chain("flood", "zh")

    assert result["disaster_type"] == "flood"
    assert "impact_chain" in result


@pytest.mark.asyncio
async def test_impact_chain_earthquake(cross_border_service: CrossBorderService) -> None:
    """测试灾害影响链 — 地震"""
    result = await cross_border_service.impact_chain("earthquake", "zh")

    assert result["disaster_type"] == "earthquake"
    assert "impact_chain" in result


@pytest.mark.asyncio
async def test_impact_chain_unknown(cross_border_service: CrossBorderService) -> None:
    """测试灾害影响链 — 未知类型"""
    result = await cross_border_service.impact_chain("unknown", "zh")

    assert result["disaster_type"] == "unknown"
    assert "impact_chain" in result


@pytest.mark.asyncio
async def test_impact_chain_english(cross_border_service: CrossBorderService) -> None:
    """测试灾害影响链 — 英文"""
    result = await cross_border_service.impact_chain("typhoon", "en")

    assert result["language"] == "en"
