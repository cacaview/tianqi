"""
气象数据 API 路由
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import LifestyleServiceDep, WeatherServiceDep
from app.api.schemas import (
    LifestyleIndicesResponse,
    MinutelyPrecipitationResponse,
    WeatherCurrentResponse,
    WeatherForecastResponse,
    WeatherReportResponse,
)

router = APIRouter()


@router.get("/current", response_model=WeatherCurrentResponse)
async def get_current_weather(
    weather_service: WeatherServiceDep,
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    longitude: float = Query(..., description="经度", ge=-180, le=180),
) -> WeatherCurrentResponse:
    """获取当前天气"""
    data = await weather_service.get_current_weather(latitude, longitude)
    return WeatherCurrentResponse(**data)


@router.get("/forecast", response_model=WeatherForecastResponse)
async def get_forecast(
    weather_service: WeatherServiceDep,
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    longitude: float = Query(..., description="经度", ge=-180, le=180),
    days: int = Query(7, description="预报天数", ge=1, le=16),
) -> WeatherForecastResponse:
    """获取天气预报"""
    data = await weather_service.get_forecast(latitude, longitude, days)
    return WeatherForecastResponse(**data)


@router.get("/minutely-precipitation", response_model=MinutelyPrecipitationResponse)
async def get_minutely_precipitation(
    weather_service: WeatherServiceDep,
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    longitude: float = Query(..., description="经度", ge=-180, le=180),
) -> MinutelyPrecipitationResponse:
    """获取分钟级降水预报（未来2小时，15分钟间隔）"""
    data = await weather_service.get_minutely_precipitation(latitude, longitude)
    return MinutelyPrecipitationResponse(**data)


@router.get("/cities")
async def get_asean_cities(
    weather_service: WeatherServiceDep,
) -> dict:
    """获取东盟主要城市列表"""
    return weather_service.get_asean_cities()


@router.get("/lifestyle-indices", response_model=LifestyleIndicesResponse)
async def get_lifestyle_indices(
    lifestyle_service: LifestyleServiceDep,
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    longitude: float = Query(..., description="经度", ge=-180, le=180),
    language: str = Query("zh", description="语言代码"),
) -> LifestyleIndicesResponse:
    """获取生活指数（穿衣、洗车、运动等建议）"""
    data = await lifestyle_service.get_lifestyle_indices(latitude, longitude, language)
    return LifestyleIndicesResponse(**data)


@router.get("/report", response_model=WeatherReportResponse)
async def get_weather_report(
    weather_service: WeatherServiceDep,
    latitude: float = Query(..., description="纬度", ge=-90, le=90),
    longitude: float = Query(..., description="经度", ge=-180, le=180),
    language: str = Query("zh", description="语言代码"),
) -> WeatherReportResponse:
    """生成自然语言天气报告"""
    from app.core.constants import WMO_WEATHER_CODES

    current = await weather_service.get_current_weather(latitude, longitude)
    forecast = await weather_service.get_forecast(latitude, longitude, 3)

    weather_desc = WMO_WEATHER_CODES.get(current.get("weather_code", -1), "未知")
    temp = current.get("temperature", "N/A")
    humidity = current.get("humidity", "N/A")
    wind = current.get("wind_speed", "N/A")

    if language == "zh":
        report = "【天气报告】\n\n"
        report += f"📍 当前天气：{weather_desc}\n"
        report += f"🌡️ 气温：{temp}°C（体感 {current.get('feels_like', 'N/A')}°C）\n"
        report += f"💧 湿度：{humidity}%\n"
        report += f"🌬️ 风速：{wind} km/h\n\n"
        report += "📅 未来三天预报：\n"
        for day in forecast.get("forecast", [])[:3]:
            report += f"  {day.get('date')}: {day.get('temp_min')}~{day.get('temp_max')}°C\n"
    else:
        report = "[Weather Report]\n\n"
        report += f"Current: {weather_desc}, {temp}°C\n"
        report += f"Humidity: {humidity}%, Wind: {wind} km/h\n"
        report += "3-day forecast:\n"
        for day in forecast.get("forecast", [])[:3]:
            report += f"  {day.get('date')}: {day.get('temp_min')}~{day.get('temp_max')}°C\n"

    return WeatherReportResponse(report=report, language=language, generated_by="rules")
