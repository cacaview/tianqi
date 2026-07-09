"""
社区天气照片墙 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import PhotoWallServiceDep, SettingsDep
from app.api.schemas import PhotoListResponse, PhotoUploadResponse

router = APIRouter()


@router.post("/upload", response_model=PhotoUploadResponse)
async def upload_photo(
    user_id: int,
    latitude: float,
    longitude: float,
    photo_url: str,
    weather_type: str | None = None,
    description: str | None = None,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
    photo_service: PhotoWallServiceDep = None,  # type: ignore[assignment]
) -> PhotoUploadResponse:
    """上传天气照片"""
    data = await photo_service.upload_photo(
        user_id, latitude, longitude, photo_url, weather_type, description, language
    )
    return PhotoUploadResponse(**data)


@router.get("/list", response_model=PhotoListResponse)
async def list_photos(
    latitude: float | None = None,
    longitude: float | None = None,
    weather_type: str | None = None,
    limit: int = 20,
    settings: SettingsDep = None,  # type: ignore[assignment]
    photo_service: PhotoWallServiceDep = None,  # type: ignore[assignment]
) -> PhotoListResponse:
    """获取照片列表"""
    data = await photo_service.get_photos(latitude, longitude, weather_type, limit)
    return PhotoListResponse(**data)
