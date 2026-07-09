"""
跨境烟霾监测 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import HazeMonitorServiceDep, SettingsDep
from app.api.schemas import FireHotspotResponse, HazeLevelResponse

router = APIRouter()


@router.get("/level", response_model=HazeLevelResponse)
async def get_haze_level(
    latitude: float,
    longitude: float,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    haze_service: HazeMonitorServiceDep = None,  # type: ignore[assignment]
) -> HazeLevelResponse:
    """评估烟霾等级"""
    data = await haze_service.get_haze_level(latitude, longitude, language)
    return HazeLevelResponse(**data)


@router.get("/hotspots", response_model=FireHotspotResponse)
async def get_fire_hotspots(
    region: str = "sumatra",
    days: int = 7,
    settings: SettingsDep = None,  # type: ignore[assignment]
    haze_service: HazeMonitorServiceDep = None,  # type: ignore[assignment]
) -> FireHotspotResponse:
    """获取火点热点数据"""
    data = await haze_service.get_fire_hotspots(region, days)
    return FireHotspotResponse(**data)
