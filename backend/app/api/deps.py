"""
依赖注入容器
使用 FastAPI 原生 Depends() + 工厂模式
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.services.agent_service import AgentService
from app.services.agro_decision_service import AgroDecisionService
from app.services.air_quality_service import AirQualityService
from app.services.api_gateway_service import ApiGatewayService
from app.services.construction_safety_service import ConstructionSafetyService
from app.services.cross_border_service import CrossBorderService
from app.services.disaster_service import DisasterAlertService
from app.services.earthquake_service import EarthquakeService
from app.services.energy_forecast_service import EnergyForecastService
from app.services.flood_service import FloodService
from app.services.haze_monitor_service import HazeMonitorService
from app.services.health_index_service import HealthIndexService
from app.services.historical_service import HistoricalService
from app.services.insurance_index_service import InsuranceIndexService
from app.services.journal_service import JournalService
from app.services.lifestyle_service import LifestyleService
from app.services.marine_decision_service import MarineDecisionService
from app.services.marine_service import MarineService
from app.services.mutual_aid_service import MutualAidService
from app.services.observation_service import ObservationService
from app.services.photo_wall_service import PhotoWallService
from app.services.weather_service import WeatherService

# ── Service 工厂函数 ──


@lru_cache(maxsize=1)
def get_weather_service() -> WeatherService:
    """WeatherService 单例工厂"""
    return WeatherService()


_disaster_service_singleton: DisasterAlertService | None = None


def get_disaster_service_instance() -> DisasterAlertService:
    """DisasterAlertService 单例工厂（应用生命周期内复用）"""
    global _disaster_service_singleton
    if _disaster_service_singleton is None:
        _disaster_service_singleton = DisasterAlertService()
    return _disaster_service_singleton


async def close_disaster_service() -> None:
    """关闭灾害服务（应用 shutdown 时调用）"""
    global _disaster_service_singleton
    if _disaster_service_singleton is not None:
        await _disaster_service_singleton.close()
        _disaster_service_singleton = None


@lru_cache(maxsize=1)
def get_agent_service() -> AgentService:
    """AgentService 单例工厂"""
    return AgentService()


# ── AirQualityService ──

_air_quality_service_singleton: AirQualityService | None = None


def get_air_quality_service_instance() -> AirQualityService:
    """AirQualityService 单例工厂（应用生命周期内复用）"""
    global _air_quality_service_singleton
    if _air_quality_service_singleton is None:
        _air_quality_service_singleton = AirQualityService()
    return _air_quality_service_singleton


async def close_air_quality_service() -> None:
    """关闭空气质量服务（应用 shutdown 时调用）"""
    global _air_quality_service_singleton
    if _air_quality_service_singleton is not None:
        await _air_quality_service_singleton.close()
        _air_quality_service_singleton = None


# ── EarthquakeService ──

_earthquake_service_singleton: EarthquakeService | None = None


def get_earthquake_service_instance() -> EarthquakeService:
    """EarthquakeService 单例工厂（应用生命周期内复用）"""
    global _earthquake_service_singleton
    if _earthquake_service_singleton is None:
        _earthquake_service_singleton = EarthquakeService()
    return _earthquake_service_singleton


async def close_earthquake_service() -> None:
    """关闭地震服务（应用 shutdown 时调用）"""
    global _earthquake_service_singleton
    if _earthquake_service_singleton is not None:
        await _earthquake_service_singleton.close()
        _earthquake_service_singleton = None


# ── LifestyleService ──

_lifestyle_service_singleton: LifestyleService | None = None


def get_lifestyle_service_instance() -> LifestyleService:
    """LifestyleService 单例工厂（应用生命周期内复用）"""
    global _lifestyle_service_singleton
    if _lifestyle_service_singleton is None:
        _lifestyle_service_singleton = LifestyleService()
    return _lifestyle_service_singleton


# ── MarineService ──

_marine_service_singleton: MarineService | None = None


def get_marine_service_instance() -> MarineService:
    """MarineService 单例工厂（应用生命周期内复用）"""
    global _marine_service_singleton
    if _marine_service_singleton is None:
        _marine_service_singleton = MarineService()
    return _marine_service_singleton


async def close_marine_service() -> None:
    """关闭海洋气象服务（应用 shutdown 时调用）"""
    global _marine_service_singleton
    if _marine_service_singleton is not None:
        await _marine_service_singleton.close()
        _marine_service_singleton = None


# ── FloodService ──

_flood_service_singleton: FloodService | None = None


def get_flood_service_instance() -> FloodService:
    """FloodService 单例工厂（应用生命周期内复用）"""
    global _flood_service_singleton
    if _flood_service_singleton is None:
        _flood_service_singleton = FloodService()
    return _flood_service_singleton


async def close_flood_service() -> None:
    """关闭洪水预报服务（应用 shutdown 时调用）"""
    global _flood_service_singleton
    if _flood_service_singleton is not None:
        await _flood_service_singleton.close()
        _flood_service_singleton = None


# ── HistoricalService ──

_historical_service_singleton: HistoricalService | None = None


def get_historical_service_instance() -> HistoricalService:
    """HistoricalService 单例工厂（应用生命周期内复用）"""
    global _historical_service_singleton
    if _historical_service_singleton is None:
        _historical_service_singleton = HistoricalService()
    return _historical_service_singleton


async def close_historical_service() -> None:
    """关闭历史气象服务（应用 shutdown 时调用）"""
    global _historical_service_singleton
    if _historical_service_singleton is not None:
        await _historical_service_singleton.close()
        _historical_service_singleton = None


# ── HealthIndexService（无状态，@lru_cache） ──


@lru_cache(maxsize=1)
def get_health_index_service() -> HealthIndexService:
    """HealthIndexService 单例工厂"""
    return HealthIndexService()


# ── ConstructionSafetyService（无状态，@lru_cache） ──


@lru_cache(maxsize=1)
def get_construction_safety_service() -> ConstructionSafetyService:
    """ConstructionSafetyService 单例工厂"""
    return ConstructionSafetyService()


# ── JournalService（无状态，@lru_cache） ──


@lru_cache(maxsize=1)
def get_journal_service() -> JournalService:
    """JournalService 单例工厂"""
    return JournalService()


@lru_cache(maxsize=1)
def get_marine_decision_service() -> MarineDecisionService:
    """MarineDecisionService 单例工厂"""
    return MarineDecisionService()


@lru_cache(maxsize=1)
def get_energy_forecast_service() -> EnergyForecastService:
    """EnergyForecastService 单例工厂"""
    return EnergyForecastService()


@lru_cache(maxsize=1)
def get_agro_decision_service() -> AgroDecisionService:
    """AgroDecisionService 单例工厂"""
    return AgroDecisionService()


@lru_cache(maxsize=1)
def get_observation_service() -> ObservationService:
    """ObservationService 单例工厂"""
    return ObservationService()


@lru_cache(maxsize=1)
def get_insurance_index_service() -> InsuranceIndexService:
    """InsuranceIndexService 单例工厂"""
    return InsuranceIndexService()


@lru_cache(maxsize=1)
def get_cross_border_service() -> CrossBorderService:
    """CrossBorderService 单例工厂"""
    return CrossBorderService()


_haze_monitor_service_singleton: HazeMonitorService | None = None


def get_haze_monitor_service_instance() -> HazeMonitorService:
    """HazeMonitorService 单例工厂"""
    global _haze_monitor_service_singleton
    if _haze_monitor_service_singleton is None:
        _haze_monitor_service_singleton = HazeMonitorService()
    return _haze_monitor_service_singleton


async def close_haze_monitor_service() -> None:
    """关闭烟霾监测服务"""
    global _haze_monitor_service_singleton
    if _haze_monitor_service_singleton is not None:
        await _haze_monitor_service_singleton.close()
        _haze_monitor_service_singleton = None


@lru_cache(maxsize=1)
def get_photo_wall_service() -> PhotoWallService:
    """PhotoWallService 单例工厂"""
    return PhotoWallService()


@lru_cache(maxsize=1)
def get_mutual_aid_service() -> MutualAidService:
    """MutualAidService 单例工厂"""
    return MutualAidService()


@lru_cache(maxsize=1)
def get_api_gateway_service() -> ApiGatewayService:
    """ApiGatewayService 单例工厂"""
    return ApiGatewayService()


# ── FastAPI Depends 类型别名 ──

SettingsDep = Annotated[Settings, Depends(get_settings)]
WeatherServiceDep = Annotated[WeatherService, Depends(get_weather_service)]
DisasterServiceDep = Annotated[DisasterAlertService, Depends(get_disaster_service_instance)]
EarthquakeServiceDep = Annotated[EarthquakeService, Depends(get_earthquake_service_instance)]
AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]
AirQualityServiceDep = Annotated[AirQualityService, Depends(get_air_quality_service_instance)]
LifestyleServiceDep = Annotated[LifestyleService, Depends(get_lifestyle_service_instance)]
MarineServiceDep = Annotated[MarineService, Depends(get_marine_service_instance)]
FloodServiceDep = Annotated[FloodService, Depends(get_flood_service_instance)]
HistoricalServiceDep = Annotated[HistoricalService, Depends(get_historical_service_instance)]
HealthIndexServiceDep = Annotated[HealthIndexService, Depends(get_health_index_service)]
ConstructionSafetyServiceDep = Annotated[ConstructionSafetyService, Depends(get_construction_safety_service)]
JournalServiceDep = Annotated[JournalService, Depends(get_journal_service)]
MarineDecisionServiceDep = Annotated[MarineDecisionService, Depends(get_marine_decision_service)]
EnergyForecastServiceDep = Annotated[EnergyForecastService, Depends(get_energy_forecast_service)]
AgroDecisionServiceDep = Annotated[AgroDecisionService, Depends(get_agro_decision_service)]
ObservationServiceDep = Annotated[ObservationService, Depends(get_observation_service)]
InsuranceIndexServiceDep = Annotated[InsuranceIndexService, Depends(get_insurance_index_service)]
CrossBorderServiceDep = Annotated[CrossBorderService, Depends(get_cross_border_service)]
HazeMonitorServiceDep = Annotated[HazeMonitorService, Depends(get_haze_monitor_service_instance)]
PhotoWallServiceDep = Annotated[PhotoWallService, Depends(get_photo_wall_service)]
MutualAidServiceDep = Annotated[MutualAidService, Depends(get_mutual_aid_service)]
ApiGatewayServiceDep = Annotated[ApiGatewayService, Depends(get_api_gateway_service)]

# ── 数据库会话 ──
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
