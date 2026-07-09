"""
城市天气健康指数 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import HealthIndexServiceDep, SettingsDep
from app.api.schemas import HealthIndexResponse

router = APIRouter()


@router.get("/health-index", response_model=HealthIndexResponse)
async def get_health_index(
    latitude: float,
    longitude: float,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    health_index_service: HealthIndexServiceDep = None,  # type: ignore[assignment]
) -> HealthIndexResponse:
    """获取城市天气健康指数 — 综合温度/AQI/UV/降水的0-100评分"""
    data = await health_index_service.calculate(latitude, longitude, language)
    return HealthIndexResponse(**data)
