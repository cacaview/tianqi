"""
海事气象决策引擎 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import MarineDecisionServiceDep, SettingsDep
from app.api.schemas import MarineConditionResponse, RouteRiskResponse

router = APIRouter()


@router.get("/route-assessment", response_model=RouteRiskResponse)
async def get_route_assessment(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    marine_decision_service: MarineDecisionServiceDep = None,  # type: ignore[assignment]
) -> RouteRiskResponse:
    """航线风险评估 — Go/No-Go/Caution"""
    data = await marine_decision_service.assess_route(origin_lat, origin_lon, dest_lat, dest_lon, language)
    return RouteRiskResponse(**data)


@router.get("/current-condition", response_model=MarineConditionResponse)
async def get_marine_condition(
    latitude: float,
    longitude: float,
    settings: SettingsDep = None,  # type: ignore[assignment]
    marine_decision_service: MarineDecisionServiceDep = None,  # type: ignore[assignment]
) -> MarineConditionResponse:
    """获取当前海况"""
    data = await marine_decision_service.get_current_condition(latitude, longitude)
    return MarineConditionResponse(**data)
