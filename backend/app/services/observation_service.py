"""
众包天气观测服务
用户提交天气观测报告，存储到数据库
"""

from __future__ import annotations

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.observation import Observation

logger = structlog.get_logger("services.observation")


class ObservationService:
    """众包天气观测服务"""

    async def submit_observation(
        self,
        db: AsyncSession,
        user_id: int,
        latitude: float,
        longitude: float,
        weather_type: str,
        description: str | None = None,
        photo_url: str | None = None,
        temperature: float | None = None,
        language: str = "zh",
    ) -> dict:
        """提交天气观测"""
        obs = Observation(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            weather_type=weather_type,
            description=description,
            photo_url=photo_url,
            temperature=temperature,
            language=language,
        )
        db.add(obs)
        await db.flush()

        logger.info("observation_submitted", user_id=user_id, obs_id=obs.id, weather_type=weather_type)

        return {
            "id": obs.id,
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "weather_type": weather_type,
            "description": description,
            "photo_url": photo_url,
            "temperature": temperature,
            "language": language,
            "created_at": obs.created_at.isoformat() if obs.created_at else None,
        }

    async def get_nearby(
        self,
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 50.0,
        limit: int = 20,
    ) -> list[dict]:
        """获取附近的观测记录 — 简化版（使用经纬度矩形过滤）"""
        # 简化：约 0.01° ≈ 1.1km
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * max(abs(latitude), 0.1))

        result = await db.execute(
            select(Observation)
            .where(
                Observation.latitude.between(latitude - lat_delta, latitude + lat_delta),
                Observation.longitude.between(longitude - lon_delta, longitude + lon_delta),
            )
            .order_by(Observation.created_at.desc())
            .limit(limit)
        )
        observations = result.scalars().all()

        return [
            {
                "id": o.id,
                "user_id": o.user_id,
                "latitude": o.latitude,
                "longitude": o.longitude,
                "weather_type": o.weather_type,
                "description": o.description,
                "temperature": o.temperature,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in observations
        ]

    async def get_heatmap_data(
        self,
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float = 100.0,
    ) -> dict:
        """获取热力图数据 — 返回经纬度+权重列表"""
        nearby = await self.get_nearby(db, latitude, longitude, radius_km, limit=100)

        points = []
        for obs in nearby:
            weight = 1.0
            if obs.get("weather_type") in ("stormy", "flood", "extreme_heat"):
                weight = 2.0
            points.append({
                "lat": obs["latitude"],
                "lon": obs["longitude"],
                "weight": weight,
            })

        return {
            "center": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius_km,
            "total_points": len(points),
            "points": points,
        }
