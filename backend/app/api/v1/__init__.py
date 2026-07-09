"""
企业气象APIaaS v1 API
"""

from __future__ import annotations

from fastapi import APIRouter, Header

from app.api.deps import AirQualityServiceDep, ApiGatewayServiceDep, SettingsDep, WeatherServiceDep
from app.api.schemas import V1AirQualityResponse, V1UsageResponse, V1WeatherResponse

router = APIRouter()


@router.get("/weather/current", response_model=V1WeatherResponse)
async def v1_weather_current(
    latitude: float,
    longitude: float,
    x_api_key: str = Header(..., alias="X-API-Key"),
    settings: SettingsDep = None,  # type: ignore[assignment]
    weather_service: WeatherServiceDep = None,  # type: ignore[assignment]
    gateway_service: ApiGatewayServiceDep = None,  # type: ignore[assignment]
) -> V1WeatherResponse:
    """企业API — 当前天气"""
    if not gateway_service.validate_key(x_api_key):
        return V1WeatherResponse(error="Invalid API key")
    if not gateway_service.check_rate_limit(x_api_key):
        return V1WeatherResponse(error="Rate limit exceeded")

    data = await weather_service.get_current_weather(latitude, longitude)
    return V1WeatherResponse(data=data)


@router.get("/air-quality/current", response_model=V1AirQualityResponse)
async def v1_air_quality_current(
    latitude: float,
    longitude: float,
    x_api_key: str = Header(..., alias="X-API-Key"),
    settings: SettingsDep = None,  # type: ignore[assignment]
    aq_service: AirQualityServiceDep = None,  # type: ignore[assignment]
    gateway_service: ApiGatewayServiceDep = None,  # type: ignore[assignment]
) -> V1AirQualityResponse:
    """企业API — 当前空气质量"""
    if not gateway_service.validate_key(x_api_key):
        return V1AirQualityResponse(error="Invalid API key")
    if not gateway_service.check_rate_limit(x_api_key):
        return V1AirQualityResponse(error="Rate limit exceeded")

    data = await aq_service.get_current(latitude, longitude)
    return V1AirQualityResponse(data=data)


@router.get("/usage", response_model=V1UsageResponse)
async def v1_usage(
    x_api_key: str = Header(..., alias="X-API-Key"),
    gateway_service: ApiGatewayServiceDep = None,  # type: ignore[assignment]
) -> V1UsageResponse:
    """查询API使用量"""
    usage = gateway_service.get_usage(x_api_key)
    return V1UsageResponse(**usage)
