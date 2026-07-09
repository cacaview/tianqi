"""
天气应急互助圈 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import DbSession, MutualAidServiceDep, SettingsDep
from app.api.schemas import MutualAidCreateRequest, MutualAidListResponse, MutualAidMatchResponse, MutualAidResponse

router = APIRouter()


@router.post("/request", response_model=MutualAidResponse)
async def create_request(
    request: MutualAidCreateRequest,
    db: DbSession = None,  # type: ignore[assignment]
    settings: SettingsDep = None,  # type: ignore[assignment]
    mutual_aid_service: MutualAidServiceDep = None,  # type: ignore[assignment]
) -> MutualAidResponse:
    """创建互助请求"""
    data = await mutual_aid_service.create_request(
        db=db,
        user_id=request.user_id,
        request_type=request.request_type,
        category=request.category,
        description=request.description,
        latitude=request.latitude,
        longitude=request.longitude,
        language=request.language,
    )
    return MutualAidResponse(**data)


@router.get("/list", response_model=MutualAidListResponse)
async def list_requests(
    latitude: float | None = None,
    longitude: float | None = None,
    limit: int = 20,
    db: DbSession = None,  # type: ignore[assignment]
    settings: SettingsDep = None,  # type: ignore[assignment]
    mutual_aid_service: MutualAidServiceDep = None,  # type: ignore[assignment]
) -> MutualAidListResponse:
    """获取开放的互助请求"""
    requests = await mutual_aid_service.get_open_requests(db, latitude, longitude, limit)
    return MutualAidListResponse(requests=requests, total=len(requests))


@router.post("/respond/{request_id}", response_model=MutualAidMatchResponse)
async def respond_to_request(
    request_id: int,
    responder_id: int,
    db: DbSession = None,  # type: ignore[assignment]
    settings: SettingsDep = None,  # type: ignore[assignment]
    mutual_aid_service: MutualAidServiceDep = None,  # type: ignore[assignment]
) -> MutualAidMatchResponse:
    """响应互助请求"""
    data = await mutual_aid_service.respond_to_request(db, request_id, responder_id)
    return MutualAidMatchResponse(**data)
