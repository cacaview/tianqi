"""
可再生能源发电预测 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import EnergyForecastServiceDep, SettingsDep
from app.api.schemas import SolarForecastResponse, WindPowerForecastResponse

router = APIRouter()


@router.get("/solar-forecast", response_model=SolarForecastResponse)
async def get_solar_forecast(
    latitude: float,
    longitude: float,
    capacity_kw: float = 10.0,
    days: int = 3,
    settings: SettingsDep = None,  # type: ignore[assignment]
    energy_service: EnergyForecastServiceDep = None,  # type: ignore[assignment]
) -> SolarForecastResponse:
    """太阳能发电预测"""
    data = await energy_service.solar_forecast(latitude, longitude, capacity_kw, days)
    return SolarForecastResponse(**data)


@router.get("/wind-forecast", response_model=WindPowerForecastResponse)
async def get_wind_forecast(
    latitude: float,
    longitude: float,
    rated_power_kw: float = 100.0,
    days: int = 3,
    settings: SettingsDep = None,  # type: ignore[assignment]
    energy_service: EnergyForecastServiceDep = None,  # type: ignore[assignment]
) -> WindPowerForecastResponse:
    """风力发电预测"""
    data = await energy_service.wind_power_forecast(latitude, longitude, rated_power_kw, days)
    return WindPowerForecastResponse(**data)
