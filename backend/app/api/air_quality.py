"""
空气质量 API 路由
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import AirQualityServiceDep
from app.api.schemas import AirQualityCurrentResponse, AirQualityForecastResponse

router = APIRouter()


@router.get("/current", response_model=AirQualityCurrentResponse)
async def get_current_air_quality(
    air_quality_service: AirQualityServiceDep,
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    longitude: float = Query(..., description="经度", ge=-180, le=180),
) -> AirQualityCurrentResponse:
    """获取当前空气质量"""
    data = await air_quality_service.get_current(latitude, longitude)
    return AirQualityCurrentResponse(**data)


@router.get("/forecast", response_model=AirQualityForecastResponse)
async def get_air_quality_forecast(
    air_quality_service: AirQualityServiceDep,
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    longitude: float = Query(..., description="经度", ge=-180, le=180),
    days: int = Query(3, description="预报天数", ge=1, le=7),
) -> AirQualityForecastResponse:
    """获取空气质量预报"""
    data = await air_quality_service.get_forecast(latitude, longitude, days)
    return AirQualityForecastResponse(**data)
