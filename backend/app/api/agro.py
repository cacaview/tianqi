"""
智慧农业气象决策 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import AgroDecisionServiceDep, SettingsDep
from app.api.schemas import AgroHarvestWindowResponse, AgroIrrigationResponse, AgroPestRiskResponse

router = APIRouter()


@router.get("/irrigation", response_model=AgroIrrigationResponse)
async def get_irrigation_advice(
    latitude: float,
    longitude: float,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    agro_service: AgroDecisionServiceDep = None,  # type: ignore[assignment]
) -> AgroIrrigationResponse:
    """灌溉建议 — 基于土壤湿度和蒸发量"""
    data = await agro_service.irrigation_advice(latitude, longitude, language)
    return AgroIrrigationResponse(**data)


@router.get("/pest-risk", response_model=AgroPestRiskResponse)
async def get_pest_risk(
    latitude: float,
    longitude: float,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    agro_service: AgroDecisionServiceDep = None,  # type: ignore[assignment]
) -> AgroPestRiskResponse:
    """病虫害风险评估"""
    data = await agro_service.pest_risk(latitude, longitude, language)
    return AgroPestRiskResponse(**data)


@router.get("/harvest-window", response_model=AgroHarvestWindowResponse)
async def get_harvest_window(
    latitude: float,
    longitude: float,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    agro_service: AgroDecisionServiceDep = None,  # type: ignore[assignment]
) -> AgroHarvestWindowResponse:
    """收获窗口规划"""
    data = await agro_service.harvest_window(latitude, longitude, language)
    return AgroHarvestWindowResponse(**data)
