"""
DisasterAlertService 单元测试
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.disaster_service import DisasterAlertService


@pytest.fixture
def disaster_service() -> DisasterAlertService:
    """创建 DisasterAlertService 实例"""
    return DisasterAlertService()


def test_is_cache_valid(disaster_service: DisasterAlertService) -> None:
    """测试缓存有效性检查"""
    from datetime import datetime, timedelta

    # 无缓存时间 → 无效
    assert disaster_service._is_cache_valid(None, timedelta(minutes=5)) is False

    # 刚缓存 → 有效
    disaster_service._cache_time = datetime.now()
    assert disaster_service._is_cache_valid(disaster_service._cache_time, timedelta(minutes=5)) is True


def test_nhc_category_to_abbrev(disaster_service: DisasterAlertService) -> None:
    """测试台风强度等级转换"""
    assert disaster_service._nhc_category_to_abbrev("Typhoon") == "TY"
    assert disaster_service._nhc_category_to_abbrev("Super Typhoon") == "STY"
    assert disaster_service._nhc_category_to_abbrev("Storm") == "TS"
    assert disaster_service._nhc_category_to_abbrev("Unknown") == "TS"  # 默认值


def test_estimate_impact_regions(disaster_service: DisasterAlertService) -> None:
    """测试影响区域估算"""
    # 南海区域
    regions = disaster_service._estimate_impact_regions(18.0, 110.0)
    assert "南海" in regions

    # 北部湾
    regions = disaster_service._estimate_impact_regions(20.0, 108.0)
    assert "北部湾" in regions

    # 远离中国的区域
    regions = disaster_service._estimate_impact_regions(0.0, 0.0)
    assert regions == ["西太平洋"]


def test_qweather_level_to_standard(disaster_service: DisasterAlertService) -> None:
    """测试预警等级转换"""
    assert disaster_service._qweather_level_to_standard("蓝色") == "blue"
    assert disaster_service._qweather_level_to_standard("红色") == "red"
    assert disaster_service._qweather_level_to_standard("Orange") == "orange"
    assert disaster_service._qweather_level_to_standard("未知") == "blue"  # 默认值


def test_get_mock_typhoon_data(disaster_service: DisasterAlertService) -> None:
    """测试模拟台风数据"""
    data = disaster_service._get_mock_typhoon_data()
    assert len(data) == 1
    assert data[0]["name"] == "帕布"
    assert data[0]["status"] == "active"
    assert data[0]["source"] == "模拟数据"


def test_get_mock_alerts(disaster_service: DisasterAlertService) -> None:
    """测试模拟预警数据"""
    alerts = disaster_service._get_mock_alerts("guangxi")
    assert len(alerts) > 0
    assert alerts[0]["type"] in ("rainstorm", "typhoon")

    # 未知区域返回空
    assert disaster_service._get_mock_alerts("unknown") == []


@pytest.mark.asyncio
async def test_typhoon_list_with_mock(disaster_service: DisasterAlertService) -> None:
    """测试台风列表 — 使用模拟数据（NHC不可用时）"""
    with respx.mock:
        # 模拟 NHC 请求失败
        respx.get("https://www.nhc.noaa.gov/CurrentStorms.json").mock(return_value=httpx.Response(500))
        typhoons = await disaster_service.get_typhoon_list()

    assert len(typhoons) > 0  # 应回退到模拟数据
    assert typhoons[0]["source"] == "模拟数据"


@pytest.mark.asyncio
async def test_typhoon_detail_not_found(disaster_service: DisasterAlertService) -> None:
    """测试台风详情 — 不存在的ID"""
    with respx.mock:
        respx.get("https://www.nhc.noaa.gov/CurrentStorms.json").mock(return_value=httpx.Response(500))
        result = await disaster_service.get_typhoon_detail("NOTEXIST")
    assert result is None


@pytest.mark.asyncio
async def test_count_by_type(disaster_service: DisasterAlertService) -> None:
    """测试按类型统计"""
    alerts = [
        {"type": "rainstorm"},
        {"type": "rainstorm"},
        {"type": "typhoon"},
    ]
    counts = disaster_service._count_by_type(alerts)
    assert counts["rainstorm"] == 2
    assert counts["typhoon"] == 1
