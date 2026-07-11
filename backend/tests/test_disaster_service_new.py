"""
DisasterAlertService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

from datetime import datetime, timedelta

import httpx
import pytest
import respx

from app.services.disaster_service import DisasterAlertService


@pytest.fixture
def disaster_service() -> DisasterAlertService:
    """创建 DisasterAlertService 实例"""
    return DisasterAlertService()


# === 缓存测试 ===


def test_is_cache_valid_no_cache(disaster_service: DisasterAlertService) -> None:
    """测试缓存有效性 — 无缓存"""
    assert disaster_service._is_cache_valid(None, timedelta(seconds=300)) is False


def test_is_cache_valid_fresh(disaster_service: DisasterAlertService) -> None:
    """测试缓存有效性 — 新鲜缓存"""
    cache_time = datetime.now()
    assert disaster_service._is_cache_valid(cache_time, timedelta(seconds=300)) is True


def test_is_cache_valid_expired(disaster_service: DisasterAlertService) -> None:
    """测试缓存有效性 — 过期缓存"""
    cache_time = datetime.now() - timedelta(seconds=400)
    assert disaster_service._is_cache_valid(cache_time, timedelta(seconds=300)) is False


# === 台风命名和常量测试 ===


def test_typhoon_names(disaster_service: DisasterAlertService) -> None:
    """测试台风命名表"""
    assert len(disaster_service.TYPHOON_NAMES) > 0
    assert "珍珠" in disaster_service.TYPHOON_NAMES
    assert "蝴蝶" in disaster_service.TYPHOON_NAMES


def test_alert_levels(disaster_service: DisasterAlertService) -> None:
    """测试预警等级"""
    assert "blue" in disaster_service.ALERT_LEVELS
    assert "yellow" in disaster_service.ALERT_LEVELS
    assert "orange" in disaster_service.ALERT_LEVELS
    assert "red" in disaster_service.ALERT_LEVELS
    assert disaster_service.ALERT_LEVELS["red"]["level"] == 4


# === 辅助方法测试 ===


def test_nhc_category_to_abbrev(disaster_service: DisasterAlertService) -> None:
    """测试NHC类别转换"""
    assert disaster_service._nhc_category_to_abbrev("Storm") == "TS"
    assert disaster_service._nhc_category_to_abbrev("Typhoon") == "TY"
    assert disaster_service._nhc_category_to_abbrev("Super Typhoon") == "STY"
    assert disaster_service._nhc_category_to_abbrev("unknown") == "TS"  # 默认


def test_parse_nhc_forecast(disaster_service: DisasterAlertService) -> None:
    """测试NHC预报路径解析"""
    lats = [15.0, 16.0, 17.0]
    lons = [110.0, 109.0, 108.0]
    forecast = disaster_service._parse_nhc_forecast(lats, lons)

    assert len(forecast) == 3
    assert forecast[0]["lat"] == 15.0
    assert forecast[0]["lon"] == 110.0
    assert forecast[0]["hour"] == 24


def test_parse_nhc_forecast_empty(disaster_service: DisasterAlertService) -> None:
    """测试NHC预报路径解析 — 空"""
    forecast = disaster_service._parse_nhc_forecast([], [])
    assert len(forecast) == 0


def test_estimate_impact_regions_south_china_sea(disaster_service: DisasterAlertService) -> None:
    """测试影响区域估算 — 南海"""
    regions = disaster_service._estimate_impact_regions(15.0, 112.0)
    assert "南海" in regions


def test_estimate_impact_regions_hainan(disaster_service: DisasterAlertService) -> None:
    """测试影响区域估算 — 海南"""
    regions = disaster_service._estimate_impact_regions(18.0, 109.0)
    assert "海南岛" in regions


def test_estimate_impact_regions_guangdong(disaster_service: DisasterAlertService) -> None:
    """测试影响区域估算 — 广东"""
    regions = disaster_service._estimate_impact_regions(22.0, 115.0)
    assert "广东沿海" in regions


def test_estimate_impact_regions_other(disaster_service: DisasterAlertService) -> None:
    """测试影响区域估算 — 其他区域"""
    regions = disaster_service._estimate_impact_regions(0.0, 100.0)
    assert "南海" not in regions
    assert "海南岛" not in regions


def test_qweather_level_to_standard(disaster_service: DisasterAlertService) -> None:
    """测试和风天气等级转换"""
    assert disaster_service._qweather_level_to_standard("蓝色") == "blue"
    assert disaster_service._qweather_level_to_standard("黄色") == "yellow"
    assert disaster_service._qweather_level_to_standard("橙色") == "orange"
    assert disaster_service._qweather_level_to_standard("红色") == "red"
    assert disaster_service._qweather_level_to_standard("unknown") == "blue"  # 默认


def test_count_by_type(disaster_service: DisasterAlertService) -> None:
    """测试按类型统计"""
    alerts = [
        {"type": "暴雨", "level": "orange"},
        {"type": "暴雨", "level": "yellow"},
        {"type": "台风", "level": "red"},
    ]
    counts = disaster_service._count_by_type(alerts)
    assert counts["暴雨"] == 2
    assert counts["台风"] == 1


def test_count_by_type_empty(disaster_service: DisasterAlertService) -> None:
    """测试按类型统计 — 空"""
    counts = disaster_service._count_by_type([])
    assert len(counts) == 0


# === 模拟数据测试 ===


def test_get_mock_typhoon_data(disaster_service: DisasterAlertService) -> None:
    """测试模拟台风数据"""
    mock_data = disaster_service._get_mock_typhoon_data()
    assert len(mock_data) > 0
    assert "name" in mock_data[0]
    assert "code" in mock_data[0]
    assert "intensity" in mock_data[0]
    assert "position" in mock_data[0]


def test_get_mock_alerts(disaster_service: DisasterAlertService) -> None:
    """测试模拟预警数据"""
    mock_alerts = disaster_service._get_mock_alerts("guangxi")
    assert len(mock_alerts) > 0
    assert "level" in mock_alerts[0]
    assert "type_name" in mock_alerts[0]
    assert "title" in mock_alerts[0]


def test_get_mock_alerts_different_regions(disaster_service: DisasterAlertService) -> None:
    """测试模拟预警数据 — 不同区域"""
    regions = ["guangxi", "vietnam", "thailand"]
    for region in regions:
        alerts = disaster_service._get_mock_alerts(region)
        assert len(alerts) > 0
        assert "id" in alerts[0]
        assert "type" in alerts[0]


# === 缓存集成测试 ===


def test_typhoon_cache(disaster_service: DisasterAlertService) -> None:
    """测试台风缓存"""
    # 初始缓存为空
    assert disaster_service._typhoon_cache is None

    # 设置缓存
    disaster_service._typhoon_cache = {
        "typhoons": [{"name": "测试台风"}],
        "source": "mock",
    }
    disaster_service._typhoon_cache_time = datetime.now()

    # 缓存应该有效
    assert disaster_service._is_cache_valid(disaster_service._typhoon_cache_time, disaster_service._typhoon_cache_ttl) is True


def test_alert_cache(disaster_service: DisasterAlertService) -> None:
    """测试预警缓存"""
    # 初始缓存为空
    assert disaster_service._cache_time is None

    # 设置缓存
    disaster_service._alert_cache = {"guangxi": [{"title": "暴雨预警"}]}
    disaster_service._cache_time = datetime.now()

    # 缓存应该有效
    assert disaster_service._is_cache_valid(disaster_service._cache_time, disaster_service._cache_ttl) is True


# === 关闭测试 ===


@pytest.mark.asyncio
async def test_close(disaster_service: DisasterAlertService) -> None:
    """测试关闭服务"""
    client = disaster_service._http_client
    assert not client.is_closed

    await disaster_service.close()
    assert client.is_closed


# === 农业预警测试 ===


@pytest.mark.asyncio
async def test_get_agriculture_alert(disaster_service: DisasterAlertService) -> None:
    """测试农业预警"""
    result = await disaster_service.get_agriculture_alert("guangxi")

    assert result["region"] == "guangxi"
    assert "alerts" in result
    assert len(result["alerts"]) > 0
    assert "update_time" in result

    first_alert = result["alerts"][0]
    assert "crop" in first_alert
    assert "stage" in first_alert
    assert "risk" in first_alert
    assert "level" in first_alert
    assert "advice" in first_alert


@pytest.mark.asyncio
async def test_get_agriculture_alert_vietnam(disaster_service: DisasterAlertService) -> None:
    """测试农业预警 — 越南"""
    result = await disaster_service.get_agriculture_alert("vietnam")
    assert result["region"] == "vietnam"


# === 物流预警测试 ===


@pytest.mark.asyncio
async def test_get_logistics_alert(disaster_service: DisasterAlertService) -> None:
    """测试物流预警"""
    result = await disaster_service.get_logistics_alert("nanning_hcmc")

    assert "route" in result
    assert "risk_level" in result
    assert "segments" in result
    assert "recommendation" in result
    assert len(result["segments"]) > 0

    first_segment = result["segments"][0]
    assert "segment" in first_segment
    assert "risk" in first_segment
    assert "weather" in first_segment


@pytest.mark.asyncio
async def test_get_logistics_alert_unknown_route(disaster_service: DisasterAlertService) -> None:
    """测试物流预警 — 未知路线"""
    result = await disaster_service.get_logistics_alert("unknown_route")
    assert len(result) == 0


# === 四阶段预警测试 ===


@pytest.mark.asyncio
async def test_get_four_stage_warning(disaster_service: DisasterAlertService) -> None:
    """测试四阶段预警"""
    result = await disaster_service.get_four_stage_warning("test_disaster_001")

    assert result["disaster_id"] == "test_disaster_001"
    assert result["disaster_type"] == "typhoon"
    assert result["disaster_name"] == "帕布"
    assert result["current_stage"] == "pre_disaster"
    assert "stages" in result
    assert "update_time" in result

    stages = result["stages"]
    assert "pre_disaster" in stages
    assert "imminent" in stages
    assert "during_disaster" in stages
    assert "post_disaster" in stages

    # 验证每个阶段的结构
    for stage_name, stage_data in stages.items():
        assert "name" in stage_data
        assert "time_range" in stage_data
        assert "status" in stage_data
        assert "content" in stage_data
        assert "actions" in stage_data
        assert len(stage_data["actions"]) > 0


# === 台风详情测试 ===


@pytest.mark.asyncio
async def test_get_typhoon_detail_found(disaster_service: DisasterAlertService) -> None:
    """测试获取台风详情 — 找到"""
    # 使用模拟数据
    disaster_service._typhoon_cache = {
        "typhoons": [
            {
                "id": "202425",
                "name": "帕布",
                "code": "PABUK",
                "position": {"lat": 18.5, "lon": 112.3},
                "intensity": "TS",
                "max_wind_speed": 65,
            },
        ],
        "source": "mock",
    }
    disaster_service._typhoon_cache_time = datetime.now()

    result = await disaster_service.get_typhoon_detail("202425")
    assert result is not None
    assert result["name"] == "帕布"


@pytest.mark.asyncio
async def test_get_typhoon_detail_not_found(disaster_service: DisasterAlertService) -> None:
    """测试获取台风详情 — 未找到"""
    # 使用模拟数据
    disaster_service._typhoon_cache = {
        "typhoons": [
            {
                "id": "202425",
                "name": "帕布",
                "code": "PABUK",
                "position": {"lat": 18.5, "lon": 112.3},
                "intensity": "TS",
                "max_wind_speed": 65,
            },
        ],
        "source": "mock",
    }
    disaster_service._typhoon_cache_time = datetime.now()

    result = await disaster_service.get_typhoon_detail("99999")
    assert result is None


# === 台风路径数据测试 ===


@pytest.mark.asyncio
async def test_get_typhoon_track_data_found(disaster_service: DisasterAlertService) -> None:
    """测试获取台风路径数据 — 找到"""
    # 使用模拟数据
    disaster_service._typhoon_cache = {
        "typhoons": [
            {
                "id": "202425",
                "name": "帕布",
                "code": "PABUK",
                "position": {"lat": 18.5, "lon": 112.3},
                "intensity": "TS",
                "max_wind_speed": 65,
                "pressure": 990,
                "historical_track": [],
                "forecast_track": [
                    {"hour": 24, "lat": 19.2, "lon": 110.5, "wind": 70},
                ],
                "radius_7": 150,
                "radius_10": 80,
                "impact_regions": ["海南岛", "北部湾"],
                "source": "模拟数据",
            },
        ],
        "source": "mock",
    }
    disaster_service._typhoon_cache_time = datetime.now()

    result = await disaster_service.get_typhoon_track_data("202425")
    assert "id" in result
    assert "name" in result
    assert "current" in result
    assert "historical_track" in result
    assert "forecast_track" in result
    assert "impact_radius" in result
    assert "impact_regions" in result
    assert result["name"] == "帕布"


@pytest.mark.asyncio
async def test_get_typhoon_track_data_not_found(disaster_service: DisasterAlertService) -> None:
    """测试获取台风路径数据 — 未找到"""
    # 使用模拟数据
    disaster_service._typhoon_cache = {
        "typhoons": [],
        "source": "mock",
    }
    disaster_service._typhoon_cache_time = datetime.now()

    result = await disaster_service.get_typhoon_track_data("99999")
    assert len(result) == 0


# === 预警汇总测试 ===


@pytest.mark.asyncio
async def test_get_alert_summary_single_region(disaster_service: DisasterAlertService) -> None:
    """测试预警汇总 — 单区域"""
    result = await disaster_service.get_alert_summary(["guangxi"])

    assert "total" in result
    assert "by_level" in result
    assert "by_type" in result
    assert "alerts" in result
    assert "update_time" in result
    assert result["total"] > 0


@pytest.mark.asyncio
async def test_get_alert_summary_multiple_regions(disaster_service: DisasterAlertService) -> None:
    """测试预警汇总 — 多区域"""
    result = await disaster_service.get_alert_summary(["guangxi", "vietnam", "thailand"])

    assert result["total"] > 0
    assert len(result["alerts"]) > 0


@pytest.mark.asyncio
async def test_get_alert_summary_empty_regions(disaster_service: DisasterAlertService) -> None:
    """测试预警汇总 — 空区域"""
    result = await disaster_service.get_alert_summary([])

    assert result["total"] == 0
    assert len(result["alerts"]) == 0


# === 全局单例测试 ===


def test_get_disaster_service_singleton() -> None:
    """测试全局单例"""
    from app.services.disaster_service import get_disaster_service

    service1 = get_disaster_service()
    service2 = get_disaster_service()

    assert service1 is service2
    assert isinstance(service1, DisasterAlertService)
