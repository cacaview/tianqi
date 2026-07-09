"""
灾害预警 API 路由
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DisasterServiceDep, EarthquakeServiceDep
from app.api.schemas import (
    AlertResponse,
    AlertSummaryResponse,
    EarthquakeListResponse,
    EarthquakeResponse,
    EEWAlertResponse,
    FourStageWarningResponse,
)

router = APIRouter()


@router.get("/alerts", response_model=AlertSummaryResponse)
async def get_alerts(
    disaster_service: DisasterServiceDep,
    regions: str = Query(default="guangxi", description="逗号分隔的区域列表"),
) -> AlertSummaryResponse:
    """
    获取多区域灾害预警汇总。
    示例: /api/disaster/alerts?regions=guangxi,vietnam,thailand
    """
    region_list = [r.strip() for r in regions.split(",")]
    summary = await disaster_service.get_alert_summary(region_list)
    return AlertSummaryResponse(**summary)


@router.get("/alerts/region/{region}", response_model=list[AlertResponse])
async def get_regional_alerts(
    region: str,
    disaster_service: DisasterServiceDep,
) -> list[AlertResponse]:
    """
    获取指定区域灾害预警列表。
    区域可选: guangxi, vietnam, thailand, indonesia, philippines,
    myanmar, malaysia, singapore, cambodia, laos
    """
    alerts = await disaster_service.get_regional_alerts(region)
    return [AlertResponse(**a) for a in alerts]


@router.get("/typhoons")
async def get_typhoons(
    disaster_service: DisasterServiceDep,
) -> list[dict]:
    """获取当前活跃台风列表"""
    return await disaster_service.get_typhoon_list()


@router.get("/typhoons/{typhoon_id}")
async def get_typhoon_detail(
    typhoon_id: str,
    disaster_service: DisasterServiceDep,
) -> dict:
    """获取台风详细信息"""
    typhoon = await disaster_service.get_typhoon_detail(typhoon_id)
    if not typhoon:
        raise HTTPException(status_code=404, detail=f"未找到台风: {typhoon_id}")
    return typhoon


@router.get("/four-stage/{disaster_id}", response_model=FourStageWarningResponse)
async def get_four_stage_warning(
    disaster_id: str,
    disaster_service: DisasterServiceDep,
) -> FourStageWarningResponse:
    """
    获取递进式四阶段预警。
    灾前预判 → 临灾预警 → 灾中追踪 → 灾后评估
    """
    result = await disaster_service.get_four_stage_warning(disaster_id)
    return FourStageWarningResponse(**result)


@router.get("/agriculture")
async def get_agriculture_alerts(
    disaster_service: DisasterServiceDep,
    region: str = Query(default="guangxi", description="区域"),
) -> dict:
    """获取农业气象灾害预警"""
    return await disaster_service.get_agriculture_alert(region)


@router.get("/logistics")
async def get_logistics_alerts(
    disaster_service: DisasterServiceDep,
    route: str = Query(default="nanning_hcmc", description="路线"),
) -> dict:
    """获取物流气象风险预警"""
    return await disaster_service.get_logistics_alert(route)


@router.get("/map-data")
async def get_weather_map_data(
    disaster_service: DisasterServiceDep,
) -> dict:
    """
    获取气象地图可视化数据。
    包含：城市天气点、预警信息、台风位置
    """
    return await disaster_service.get_weather_map_data()


@router.get("/typhoon-track/{typhoon_id}")
async def get_typhoon_track(
    typhoon_id: str,
    disaster_service: DisasterServiceDep,
) -> dict:
    """
    获取台风路径数据（用于地图可视化）。
    返回 GeoJSON 格式的路径坐标。
    """
    track = await disaster_service.get_typhoon_track_data(typhoon_id)
    if not track:
        raise HTTPException(status_code=404, detail=f"未找到台风路径数据: {typhoon_id}")

    geojson: dict = {"type": "FeatureCollection", "features": []}

    # 当前台风位置
    if track.get("current"):
        geojson["features"].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [track["current"]["lon"], track["current"]["lat"]],
                },
                "properties": {
                    "type": "current",
                    "name": track["name"],
                    "intensity": track["current"]["intensity"],
                    "wind_speed": track["current"]["wind_speed"],
                },
            }
        )

    # 历史路径
    if track.get("historical_track"):
        coords = [[p["lon"], p["lat"]] for p in track["historical_track"]]
        geojson["features"].append(
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords},
                "properties": {"type": "historical", "name": track["name"]},
            }
        )

    # 预报路径
    if track.get("forecast_track") and track.get("current"):
        coords = [[track["current"]["lon"], track["current"]["lat"]]]
        coords.extend([[p["lon"], p["lat"]] for p in track["forecast_track"]])
        geojson["features"].append(
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords},
                "properties": {"type": "forecast", "name": track["name"]},
            }
        )

    return geojson


# ── 地震预警 ──


@router.get("/earthquakes", response_model=EarthquakeListResponse)
async def get_earthquakes(
    earthquake_service: EarthquakeServiceDep,
    source: str = Query("cenc", description="数据源: cenc/jma/usgs"),
) -> EarthquakeListResponse:
    """获取近期地震列表"""
    result = await earthquake_service.get_recent_earthquakes(source=source)
    return EarthquakeListResponse(**result)


@router.get("/earthquakes/{earthquake_id}", response_model=EarthquakeResponse)
async def get_earthquake_detail(
    earthquake_id: str,
    earthquake_service: EarthquakeServiceDep,
    source: str = Query("cenc", description="数据源: cenc/jma/usgs"),
) -> EarthquakeResponse:
    """获取地震详情"""
    result = await earthquake_service.get_recent_earthquakes(source=source)
    for eq in result.get("earthquakes", []):
        if eq["id"] == earthquake_id:
            return EarthquakeResponse(**eq)
    raise HTTPException(status_code=404, detail=f"未找到地震记录: {earthquake_id}")


@router.get("/eew", response_model=list[EEWAlertResponse])
async def get_eew_alerts(
    earthquake_service: EarthquakeServiceDep,
) -> list[EEWAlertResponse]:
    """获取地震预警 (EEW) 列表"""
    alerts = await earthquake_service.get_eew_alerts()
    return [EEWAlertResponse(**a) for a in alerts]
