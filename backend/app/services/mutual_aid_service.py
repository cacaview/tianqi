"""
天气应急互助圈服务 MVP
极端天气期间的社区互助
"""

from __future__ import annotations

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mutual_aid import MutualAidRequest

logger = structlog.get_logger("services.mutual_aid")


class MutualAidService:
    """天气应急互助圈服务"""

    async def create_request(
        self,
        db: AsyncSession,
        user_id: int,
        request_type: str,
        category: str,
        description: str,
        latitude: float,
        longitude: float,
        language: str = "zh",
    ) -> dict:
        """创建互助请求"""
        req = MutualAidRequest(
            user_id=user_id,
            request_type=request_type,
            category=category,
            description=description,
            latitude=latitude,
            longitude=longitude,
            language=language,
        )
        db.add(req)
        await db.flush()

        logger.info("mutual_aid_created", request_id=req.id, type=request_type, category=category)

        return {
            "id": req.id,
            "user_id": user_id,
            "request_type": request_type,
            "category": category,
            "description": description,
            "latitude": latitude,
            "longitude": longitude,
            "status": req.status,
            "language": language,
            "created_at": req.created_at.isoformat() if req.created_at else None,
        }

    async def get_open_requests(
        self,
        db: AsyncSession,
        latitude: float | None = None,
        longitude: float | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """获取开放的互助请求"""
        query = select(MutualAidRequest).where(MutualAidRequest.status == "open")

        if latitude is not None and longitude is not None:
            lat_delta = 1.0
            lon_delta = 1.0
            query = query.where(
                MutualAidRequest.latitude.between(latitude - lat_delta, latitude + lat_delta),
                MutualAidRequest.longitude.between(longitude - lon_delta, longitude + lon_delta),
            )

        query = query.order_by(MutualAidRequest.created_at.desc()).limit(limit)
        result = await db.execute(query)
        requests = result.scalars().all()

        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "request_type": r.request_type,
                "category": r.category,
                "description": r.description,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in requests
        ]

    async def respond_to_request(
        self,
        db: AsyncSession,
        request_id: int,
        responder_id: int,
    ) -> dict:
        """响应互助请求"""
        result = await db.execute(select(MutualAidRequest).where(MutualAidRequest.id == request_id))
        req = result.scalar_one_or_none()

        if not req:
            return {"error": "Request not found"}

        req.status = "matched"
        req.matched_with = responder_id

        logger.info("mutual_aid_matched", request_id=request_id, responder=responder_id)

        return {
            "request_id": request_id,
            "status": "matched",
            "responder_id": responder_id,
        }
