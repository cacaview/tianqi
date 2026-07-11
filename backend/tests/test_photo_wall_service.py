"""
PhotoWallService 单元测试
"""

from __future__ import annotations

import pytest

from app.services.photo_wall_service import PhotoWallService


@pytest.fixture
def photo_service() -> PhotoWallService:
    return PhotoWallService()


@pytest.mark.asyncio
async def test_upload_photo(photo_service: PhotoWallService) -> None:
    """测试上传照片"""
    result = await photo_service.upload_photo(
        user_id=1,
        latitude=22.82,
        longitude=108.32,
        photo_url="https://example.com/photo.jpg",
        weather_type="sunny",
        description="晴天",
        language="zh",
    )
    assert result["user_id"] == 1
    assert result["latitude"] == 22.82
    assert result["photo_url"] == "https://example.com/photo.jpg"
    assert result["weather_type"] == "sunny"


@pytest.mark.asyncio
async def test_upload_photo_minimal(photo_service: PhotoWallService) -> None:
    """测试上传照片 — 最小参数"""
    result = await photo_service.upload_photo(
        user_id=1,
        latitude=22.82,
        longitude=108.32,
        photo_url="https://example.com/photo.jpg",
    )
    assert result["weather_type"] == "unknown"
    assert result["description"] is None


@pytest.mark.asyncio
async def test_get_photos(photo_service: PhotoWallService) -> None:
    """测试获取照片列表"""
    result = await photo_service.get_photos(latitude=22.82, longitude=108.32)
    assert "photos" in result
    assert "total" in result
    assert result["total"] == 0


@pytest.mark.asyncio
async def test_classify_photo(photo_service: PhotoWallService) -> None:
    """测试AI分类照片"""
    result = await photo_service.classify_photo("https://example.com/photo.jpg")
    assert result["photo_url"] == "https://example.com/photo.jpg"
    assert result["weather_type"] == "unknown"
    assert result["confidence"] == 0.0
