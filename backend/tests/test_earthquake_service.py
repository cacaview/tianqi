"""
EarthquakeService 单元测试
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.earthquake_service import EarthquakeService


@pytest.fixture
def earthquake_service() -> EarthquakeService:
    """创建 EarthquakeService 实例"""
    return EarthquakeService()


def test_is_cache_valid_no_cache(earthquake_service: EarthquakeService) -> None:
    """测试无缓存时返回 False"""
    assert earthquake_service._is_cache_valid(ttl_seconds=300) is False


def test_is_cache_valid_fresh(earthquake_service: EarthquakeService) -> None:
    """测试刚缓存时返回 True"""
    from datetime import datetime

    earthquake_service._cache = {"data": []}
    earthquake_service._cache_time = datetime.now()
    assert earthquake_service._is_cache_valid(ttl_seconds=300) is True


def test_is_cache_valid_expired(earthquake_service: EarthquakeService) -> None:
    """测试缓存过期时返回 False"""
    from datetime import datetime, timedelta

    earthquake_service._cache = {"data": []}
    earthquake_service._cache_time = datetime.now() - timedelta(seconds=600)
    assert earthquake_service._is_cache_valid(ttl_seconds=300) is False


@pytest.mark.asyncio
async def test_get_recent_earthquakes_empty(earthquake_service: EarthquakeService) -> None:
    """测试获取地震列表 — 空数据"""
    with respx.mock:
        respx.get("https://api.wolfx.jp/cenc_eqlist.json").mock(
            return_value=httpx.Response(200, json={"time": "2024-01-01T00:00:00"})
        )
        result = await earthquake_service.get_recent_earthquakes(source="cenc")

    assert result["earthquakes"] == []
    assert result["total"] == 0


@pytest.mark.asyncio
async def test_get_recent_earthquakes_with_data(earthquake_service: EarthquakeService) -> None:
    """测试获取地震列表 — 有数据（No1..No50 格式）"""
    mock_data = {
        "No1": {
            "ID": "202401010001",
            "type": "CENC",
            "Hypocenter": "四川",
            "Magnitude": 5.0,
            "MaxIntensity": "VI",
            "Latitude": 30.0,
            "Longitude": 103.0,
            "Depth": 10.0,
            "Time": "2024-01-01T00:00:00",
            "Detail": "https://example.com/eq1",
        },
        "No2": {
            "ID": "202401010002",
            "type": "JMA",
            "HypoCenter": "東京",
            "Magnitude": 3.5,
            "MaxIntensity": "III",
            "Latitude": 35.0,
            "Longitude": 139.0,
            "Depth": 30.0,
            "Time": "2024-01-01T01:00:00",
        },
        "time": "2024-01-01T02:00:00",
    }

    with respx.mock:
        respx.get("https://api.wolfx.jp/cenc_eqlist.json").mock(return_value=httpx.Response(200, json=mock_data))
        result = await earthquake_service.get_recent_earthquakes(source="cenc")

    assert result["total"] >= 1
    assert result["is_mock"] is False


@pytest.mark.asyncio
async def test_get_recent_earthquakes_api_error(earthquake_service: EarthquakeService) -> None:
    """测试获取地震列表 — API 报错时返回 mock 数据"""
    with respx.mock:
        respx.get("https://api.wolfx.jp/cenc_eqlist.json").mock(return_value=httpx.Response(500))
        result = await earthquake_service.get_recent_earthquakes(source="cenc")

    # API 失败应返回 mock 数据而非抛出异常
    assert result["earthquakes"] != []
    assert result.get("is_mock", True) is True


@pytest.mark.asyncio
async def test_get_eew_alerts_empty(earthquake_service: EarthquakeService) -> None:
    """测试获取 EEW 预警 — 空数据"""
    with respx.mock:
        respx.get("https://api.wolfx.jp/cenc_eew.json").mock(return_value=httpx.Response(200, json={}))
        alerts = await earthquake_service.get_eew_alerts()

    assert alerts == []


@pytest.mark.asyncio
async def test_get_eew_alerts_with_data(earthquake_service: EarthquakeService) -> None:
    """测试获取 EEW 预警 — 有数据"""
    mock_data = {
        "EventID": "EEW-20240101",
        "type": "JMA",
        "HypoCenter": "熊本",
        "Magnitude": 6.0,
        "MaxIntensity": "VI",
        "Latitude": 32.8,
        "Longitude": 130.7,
        "Depth": 12.0,
        "Time": "2024-01-01T03:00:00",
        "is_cancelled": False,
    }

    with respx.mock:
        respx.get("https://api.wolfx.jp/cenc_eew.json").mock(return_value=httpx.Response(200, json=mock_data))
        alerts = await earthquake_service.get_eew_alerts()

    assert len(alerts) == 1
    assert alerts[0]["magnitude"] == 6.0


@pytest.mark.asyncio
async def test_get_eew_alerts_api_error(earthquake_service: EarthquakeService) -> None:
    """测试获取 EEW 预警 — API 报错时返回空列表"""
    with respx.mock:
        respx.get("https://api.wolfx.jp/cenc_eew.json").mock(return_value=httpx.Response(500))
        alerts = await earthquake_service.get_eew_alerts()

    assert alerts == []


@pytest.mark.asyncio
async def test_close(earthquake_service: EarthquakeService) -> None:
    """测试关闭客户端"""
    # 未创建客户端时 close 不报错
    await earthquake_service.close()

    # 创建并关闭
    await earthquake_service._get_client()
    assert earthquake_service._client is not None
    await earthquake_service.close()
    assert earthquake_service._client is None or earthquake_service._client.is_closed
