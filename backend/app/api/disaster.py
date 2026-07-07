"""
灾害预警API路由
"""
from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel
from app.services.disaster_service import get_disaster_service


router = APIRouter()


# 响应模型
class AlertResponse(BaseModel):
    id: str
    type: str
    type_name: str
    level: str
    level_name: str
    title: str
    content: str
    start_time: str
    end_time: str
    affected_areas: List[str]
    recommendations: List[str]
    source: str


class AlertSummaryResponse(BaseModel):
    total: int
    by_level: dict
    by_type: dict
    alerts: List[AlertResponse]
    update_time: str


class TyphoonResponse(BaseModel):
    id: str
    name: str
    code: str
    status: str
    position: dict
    intensity: str
    max_wind_speed: int
    pressure: int
    move_direction: str
    move_speed: int
    forecast_track: List[dict]


class FourStageWarningResponse(BaseModel):
    disaster_id: str
    disaster_type: str
    disaster_name: str
    current_stage: str
    stages: dict
    update_time: str


@router.get("/alerts", response_model=AlertSummaryResponse)
async def get_alerts(
    regions: str = Query(default="guangxi", description="逗号分隔的区域列表"),
):
    """
    获取多区域灾害预警汇总
    示例: /api/disaster/alerts?regions=guangxi,vietnam,thailand
    """
    region_list = [r.strip() for r in regions.split(",")]
    service = get_disaster_service()
    summary = await service.get_alert_summary(region_list)
    return summary


@router.get("/alerts/region/{region}", response_model=List[AlertResponse])
async def get_regional_alerts(region: str):
    """
    获取指定区域灾害预警列表
    区域可选: guangxi, vietnam, thailand, indonesia, philippines, myanmar, malaysia, singapore, cambodia, laos
    """
    service = get_disaster_service()
    return await service.get_regional_alerts(region)


@router.get("/typhoons")
async def get_typhoons():
    """获取当前活跃台风列表"""
    service = get_disaster_service()
    return await service.get_typhoon_list()


@router.get("/typhoons/{typhoon_id}")
async def get_typhoon_detail(typhoon_id: str):
    """获取台风详细信息"""
    service = get_disaster_service()
    typhoon = await service.get_typhoon_detail(typhoon_id)
    if not typhoon:
        return {"error": "未找到该台风"}, 404
    return typhoon


@router.get("/four-stage/{disaster_id}")
async def get_four_stage_warning(disaster_id: str):
    """
    获取递进式四阶段预警
    灾前预判 → 临灾预警 → 灾中追踪 → 灾后评估
    """
    service = get_disaster_service()
    return await service.get_four_stage_warning(disaster_id)


@router.get("/agriculture")
async def get_agriculture_alerts(
    region: str = Query(default="guangxi", description="区域")
):
    """获取农业气象灾害预警"""
    service = get_disaster_service()
    return await service.get_agriculture_alert(region)


@router.get("/logistics")
async def get_logistics_alerts(
    route: str = Query(default="nanning_hcmc", description="路线: nanning_hcmc")
):
    """获取物流气象风险预警"""
    service = get_disaster_service()
    return await service.get_logistics_alert(route)


@router.get("/map-data")
async def get_weather_map_data():
    """
    获取气象地图可视化数据
    包含：城市天气点、预警信息、台风位置
    """
    service = get_disaster_service()
    return await service.get_weather_map_data()


@router.get("/typhoon-track/{typhoon_id}")
async def get_typhoon_track(typhoon_id: str):
    """
    获取台风路径数据（用于地图可视化）
    返回GeoJSON格式的路径坐标
    """
    service = get_disaster_service()
    track = await service.get_typhoon_track_data(typhoon_id)
    if not track:
        return {"error": "未找到该台风"}, 404

    # 转换为GeoJSON格式
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    # 当前台风位置
    if track.get("current"):
        geojson["features"].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [track["current"]["lon"], track["current"]["lat"]]
            },
            "properties": {
                "type": "current",
                "name": track["name"],
                "intensity": track["current"]["intensity"],
                "wind_speed": track["current"]["wind_speed"],
            }
        })

    # 历史路径
    if track.get("historical_track"):
        coords = [[p["lon"], p["lat"]] for p in track["historical_track"]]
        geojson["features"].append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"type": "historical", "name": track["name"]}
        })

    # 预报路径
    if track.get("forecast_track"):
        coords = [[track["current"]["lon"], track["current"]["lat"]]]
        coords.extend([[p["lon"], p["lat"]] for p in track["forecast_track"]])
        geojson["features"].append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {"type": "forecast", "name": track["name"]}
        })

    return geojson
