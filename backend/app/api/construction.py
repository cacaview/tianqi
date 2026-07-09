"""
建筑工地气象安全评估 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import ConstructionSafetyServiceDep, SettingsDep
from app.api.schemas import ConstructionSafetyResponse

router = APIRouter()


@router.get("/safety-assessment", response_model=ConstructionSafetyResponse)
async def get_safety_assessment(
    latitude: float,
    longitude: float,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    construction_safety_service: ConstructionSafetyServiceDep = None,  # type: ignore[assignment]
) -> ConstructionSafetyResponse:
    """建筑工地气象安全评估 — 基于风速/雷暴/热应力/降水四因子Go/No-Go判断"""
    data = await construction_safety_service.assess(latitude, longitude, language)
    return ConstructionSafetyResponse(**data)
