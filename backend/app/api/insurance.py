"""
农业气象保险指数 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import InsuranceIndexServiceDep, SettingsDep
from app.api.schemas import InsuranceRiskProfileResponse, InsuranceTriggerResponse

router = APIRouter()


@router.get("/trigger-check", response_model=InsuranceTriggerResponse)
async def get_trigger_check(
    latitude: float,
    longitude: float,
    crop_type: str = "rice",
    policy_period_days: int = 90,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    insurance_service: InsuranceIndexServiceDep = None,  # type: ignore[assignment]
) -> InsuranceTriggerResponse:
    """计算参数化保险触发条件"""
    data = await insurance_service.calculate_trigger(latitude, longitude, crop_type, policy_period_days, language)
    return InsuranceTriggerResponse(**data)


@router.get("/risk-profile", response_model=InsuranceRiskProfileResponse)
async def get_risk_profile(
    latitude: float,
    longitude: float,
    crop_type: str = "rice",
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    insurance_service: InsuranceIndexServiceDep = None,  # type: ignore[assignment]
) -> InsuranceRiskProfileResponse:
    """历史风险画像"""
    data = await insurance_service.historical_risk_profile(latitude, longitude, crop_type, language)
    return InsuranceRiskProfileResponse(**data)
