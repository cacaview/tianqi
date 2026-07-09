"""
跨境灾害协同预警 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CrossBorderServiceDep, SettingsDep
from app.api.schemas import CrossBorderCorrelateResponse, ImpactChainResponse

router = APIRouter()


@router.get("/correlate", response_model=CrossBorderCorrelateResponse)
async def correlate_events(
    time_window_hours: int = 48,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    cross_border_service: CrossBorderServiceDep = None,  # type: ignore[assignment]
) -> CrossBorderCorrelateResponse:
    """跨国灾害关联分析"""
    data = await cross_border_service.correlate_events(time_window_hours, language)
    return CrossBorderCorrelateResponse(**data)


@router.get("/impact-chain", response_model=ImpactChainResponse)
async def get_impact_chain(
    disaster_type: str = "typhoon",
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    cross_border_service: CrossBorderServiceDep = None,  # type: ignore[assignment]
) -> ImpactChainResponse:
    """灾害影响传播链"""
    data = await cross_border_service.impact_chain(disaster_type, language)
    return ImpactChainResponse(**data)
