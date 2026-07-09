"""
众包天气观测 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import DbSession, ObservationServiceDep, SettingsDep
from app.api.schemas import ObservationListResponse, ObservationRequest, ObservationResponse

router = APIRouter()


@router.post("/submit", response_model=ObservationResponse)
async def submit_observation(
    request: ObservationRequest,
    db: DbSession = None,  # type: ignore[assignment]
    settings: SettingsDep = None,  # type: ignore[assignment]
    observation_service: ObservationServiceDep = None,  # type: ignore[assignment]
) -> ObservationResponse:
    """提交天气观测报告"""
    data = await observation_service.submit_observation(
        db=db,
        user_id=request.user_id,
        latitude=request.latitude,
        longitude=request.longitude,
        weather_type=request.weather_type,
        description=request.description,
        photo_url=request.photo_url,
        temperature=request.temperature,
        language=request.language,
    )
    return ObservationResponse(**data)


@router.get("/nearby", response_model=ObservationListResponse)
async def get_nearby_observations(
    latitude: float,
    longitude: float,
    radius_km: float = 50.0,
    limit: int = 20,
    db: DbSession = None,  # type: ignore[assignment]
    settings: SettingsDep = None,  # type: ignore[assignment]
    observation_service: ObservationServiceDep = None,  # type: ignore[assignment]
) -> ObservationListResponse:
    """获取附近的观测记录"""
    observations = await observation_service.get_nearby(db, latitude, longitude, radius_km, limit)
    return ObservationListResponse(observations=observations, total=len(observations))
