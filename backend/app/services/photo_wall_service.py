"""
社区天气照片墙服务
照片上传 + AI分类 + 地理标记
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger("services.photo_wall")


class PhotoWallService:
    """社区天气照片墙服务"""

    async def upload_photo(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
        photo_url: str,
        weather_type: str | None = None,
        description: str | None = None,
        language: str = "zh",
    ) -> dict:
        """上传天气照片"""
        logger.info("photo_uploaded", user_id=user_id, weather_type=weather_type)

        return {
            "id": 1,  # 模拟ID
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "photo_url": photo_url,
            "weather_type": weather_type or "unknown",
            "description": description,
            "language": language,
        }

    async def get_photos(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        weather_type: str | None = None,
        limit: int = 20,
    ) -> dict:
        """获取照片列表"""
        return {
            "photos": [],
            "total": 0,
            "latitude": latitude,
            "longitude": longitude,
        }

    async def classify_photo(self, photo_url: str) -> dict:
        """AI分类照片 — 识别天气类型"""
        return {
            "photo_url": photo_url,
            "weather_type": "unknown",
            "confidence": 0.0,
            "message": "AI classification requires LLM configured",
        }
