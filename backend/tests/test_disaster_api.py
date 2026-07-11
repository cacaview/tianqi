"""
灾害预警 API 路由测试
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Depends

from app.main import app
from app.api.deps import get_disaster_service_instance, get_earthquake_service_instance


@pytest.fixture
def mock_disaster_service():
    """模拟灾害服务"""
    service = AsyncMock()
    service.get_alert_summary.return_value = {
        "total": 2,
        "by_level": {"red": 0, "orange": 1, "yellow": 1, "blue": 0},
        "by_type": {"暴雨": 1, "台风": 1},
        "alerts": [
            {
                "id": "alert_001",
                "type": "暴雨",
                "type_name": "暴雨预警",
                "level": "orange",
                "level_name": "橙色",
                "title": "暴雨橙色预警",
                "content": "预计未来6小时有暴雨",
                "start_time": "2026-07-10T10:00:00",
                "end_time": "2026-07-10T18:00:00",
                "affected_areas": ["南宁"],
                "recommendations": ["减少外出"],
                "source": "中国气象局",
            },
            {
                "id": "alert_002",
                "type": "台风",
                "type_name": "台风预警",
                "level": "yellow",
                "level_name": "黄色",
                "title": "台风黄色预警",
                "content": "台风即将登陆",
                "start_time": "2026-07-10T12:00:00",
                "end_time": "2026-07-11T12:00:00",
                "affected_areas": ["越南"],
                "recommendations": ["做好防风准备"],
                "source": "越南气象局",
            },
        ],
        "update_time": "2026-07-10T10:30:00",
    }
    service.get_regional_alerts.return_value = [
        {
            "id": "alert_001",
            "type": "暴雨",
            "type_name": "暴雨预警",
            "level": "orange",
            "level_name": "橙色",
            "title": "暴雨橙色预警",
            "content": "预计未来6小时有暴雨",
            "start_time": "2026-07-10T10:00:00",
            "end_time": "2026-07-10T18:00:00",
            "affected_areas": ["南宁"],
            "recommendations": ["减少外出"],
            "source": "中国气象局",
        },
        {
            "id": "alert_002",
            "type": "台风",
            "type_name": "台风预警",
            "level": "yellow",
            "level_name": "黄色",
            "title": "台风黄色预警",
            "content": "台风即将登陆",
            "start_time": "2026-07-10T12:00:00",
            "end_time": "2026-07-11T12:00:00",
            "affected_areas": ["越南"],
            "recommendations": ["做好防风准备"],
            "source": "越南气象局",
        },
    ]
    service.get_typhoon_list.return_value = [
        {"id": "WP01", "name": "台风1号", "intensity": "台风"},
    ]
    service.get_typhoon_detail.return_value = {
        "id": "WP01",
        "name": "台风1号",
        "intensity": "台风",
        "wind_speed": 120,
    }
    service.get_four_stage_warning.return_value = {
        "disaster_id": "test123",
        "disaster_type": "暴雨",
        "disaster_name": "广西暴雨",
        "current_stage": "临灾预警",
        "stages": {
            "pre_judgment": {"stage": "灾前预判", "description": "可能发生暴雨"},
            "imminent": {"stage": "临灾预警", "description": "暴雨即将来临"},
        },
        "update_time": "2026-07-10T10:00:00",
    }
    service.get_agriculture_alert.return_value = {
        "region": "guangxi",
        "alerts": [{"type": "暴雨", "level": "orange"}],
    }
    service.get_logistics_alert.return_value = {
        "route": "nanning_hcmc",
        "risks": [{"type": "暴雨", "level": "yellow"}],
    }
    service.get_weather_map_data.return_value = {
        "cities": [{"name": "南宁", "lat": 22.82, "lon": 108.32}],
        "alerts": [],
    }
    service.get_typhoon_track_data.return_value = {
        "name": "台风1号",
        "current": {"lat": 15.0, "lon": 120.0, "intensity": "台风", "wind_speed": 120},
        "historical_track": [
            {"lat": 10.0, "lon": 115.0},
            {"lat": 12.0, "lon": 117.0},
        ],
        "forecast_track": [
            {"lat": 17.0, "lon": 122.0},
            {"lat": 20.0, "lon": 125.0},
        ],
    }
    return service


@pytest.fixture
def mock_earthquake_service():
    """模拟地震服务"""
    service = AsyncMock()
    service.get_recent_earthquakes.return_value = {
        "earthquakes": [
            {
                "id": "EQ001",
                "source": "cenc",
                "hypocenter": "四川",
                "magnitude": 5.0,
                "max_intensity": "V",
                "latitude": 30.0,
                "longitude": 103.0,
                "depth_km": 10,
                "occurred_at": "2026-07-10T10:00:00",
            },
            {
                "id": "EQ002",
                "source": "cenc",
                "hypocenter": "云南",
                "magnitude": 3.5,
                "max_intensity": "III",
                "latitude": 25.0,
                "longitude": 102.0,
                "depth_km": 8,
                "occurred_at": "2026-07-10T11:00:00",
            },
        ],
        "total": 2,
        "update_time": "2026-07-10T12:00:00",
    }
    service.get_eew_alerts.return_value = [
        {
            "id": "EEW001",
            "source": "cenc",
            "hypocenter": "四川",
            "magnitude": 5.0,
            "expected_max_intensity": "V",
            "latitude": 30.0,
            "longitude": 103.0,
            "depth_km": 10,
            "alert_time": "2026-07-10T10:00:05",
            "is_cancelled": False,
        },
    ]
    return service


@pytest.mark.asyncio
async def test_get_alerts(mock_disaster_service):
    """测试获取多区域预警汇总"""
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/alerts", params={"regions": "guangxi,vietnam"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_regional_alerts(mock_disaster_service):
    """测试获取区域预警列表"""
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/alerts/region/guangxi")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_typhoons(mock_disaster_service):
    """测试获取台风列表"""
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/typhoons")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_typhoon_detail_found(mock_disaster_service):
    """测试获取台风详情 — 存在"""
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/typhoons/WP01")

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "WP01"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_typhoon_detail_not_found(mock_disaster_service):
    """测试获取台风详情 — 不存在"""
    mock_disaster_service.get_typhoon_detail.return_value = None
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/typhoons/NOTEXIST")

        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_four_stage_warning(mock_disaster_service):
    """测试四阶段预警"""
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/four-stage/test123")

        assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_agriculture_alerts(mock_disaster_service):
    """测试农业灾害预警"""
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/agriculture", params={"region": "guangxi"})

        assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_logistics_alerts(mock_disaster_service):
    """测试物流灾害预警"""
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/logistics", params={"route": "nanning_hcmc"})

        assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_weather_map_data(mock_disaster_service):
    """测试气象地图数据"""
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/map-data")

        assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_typhoon_track(mock_disaster_service):
    """测试台风路径"""
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/typhoon-track/WP01")

        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 3  # current + historical + forecast
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_typhoon_track_not_found(mock_disaster_service):
    """测试台风路径 — 不存在"""
    mock_disaster_service.get_typhoon_track_data.return_value = None
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/typhoon-track/NOTEXIST")

        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_typhoon_track_no_forecast(mock_disaster_service):
    """测试台风路径 — 无预报路径"""
    mock_disaster_service.get_typhoon_track_data.return_value = {
        "name": "台风1号",
        "current": {"lat": 15.0, "lon": 120.0, "intensity": "台风", "wind_speed": 120},
        "historical_track": [{"lat": 10.0, "lon": 115.0}],
        "forecast_track": None,
    }
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/typhoon-track/WP01")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["features"]) == 2  # current + historical only
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_typhoon_track_no_current(mock_disaster_service):
    """测试台风路径 — 无当前位置"""
    mock_disaster_service.get_typhoon_track_data.return_value = {
        "name": "台风1号",
        "current": None,
        "historical_track": [{"lat": 10.0, "lon": 115.0}],
        "forecast_track": [{"lat": 17.0, "lon": 122.0}],
    }
    app.dependency_overrides[get_disaster_service_instance] = lambda: mock_disaster_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/typhoon-track/WP01")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["features"]) == 1  # historical only
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_earthquakes(mock_earthquake_service):
    """测试获取地震列表"""
    app.dependency_overrides[get_earthquake_service_instance] = lambda: mock_earthquake_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/earthquakes", params={"source": "cenc"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_earthquake_detail_found(mock_earthquake_service):
    """测试获取地震详情 — 存在"""
    app.dependency_overrides[get_earthquake_service_instance] = lambda: mock_earthquake_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/earthquakes/EQ001", params={"source": "cenc"})

        assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_earthquake_detail_not_found(mock_earthquake_service):
    """测试获取地震详情 — 不存在"""
    app.dependency_overrides[get_earthquake_service_instance] = lambda: mock_earthquake_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/earthquakes/NOTEXIST", params={"source": "cenc"})

        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_eew_alerts(mock_earthquake_service):
    """测试获取 EEW 预警"""
    app.dependency_overrides[get_earthquake_service_instance] = lambda: mock_earthquake_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/disaster/eew")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
    finally:
        app.dependency_overrides.clear()
