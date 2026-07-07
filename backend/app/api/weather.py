"""
气象数据API接口
"""
from fastapi import APIRouter, Query
from typing import Optional
from app.services.weather_service import WeatherService

router = APIRouter()
weather_service = WeatherService()


@router.get("/current")
async def get_current_weather(
    latitude: float = Query(..., description="纬度"),
    longitude: float = Query(..., description="经度"),
    city: Optional[str] = Query(None, description="城市名称（可选）"),
):
    """获取当前天气"""
    data = await weather_service.get_current_weather(latitude, longitude)
    return data


@router.get("/forecast")
async def get_forecast(
    latitude: float = Query(..., description="纬度"),
    longitude: float = Query(..., description="经度"),
    days: int = Query(7, description="预报天数", ge=1, le=16),
):
    """获取天气预报"""
    data = await weather_service.get_forecast(latitude, longitude, days)
    return data


@router.get("/cities")
async def get_asean_cities():
    """获取东盟主要城市列表"""
    return weather_service.get_asean_cities()
