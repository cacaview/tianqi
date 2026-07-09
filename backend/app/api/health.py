"""
健康检查 API 路由
"""

from __future__ import annotations

import time
from typing import Any

import httpx
import structlog
from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()
logger = structlog.get_logger("api.health")

_start_time = time.time()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """
    健康检查接口。
    返回服务状态、运行时长、依赖组件连通性。
    """
    settings = get_settings()
    uptime = time.time() - _start_time

    checks: dict[str, Any] = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT.value,
        "uptime_seconds": round(uptime, 1),
        "llm_configured": settings.has_llm_key,
        "supported_languages": settings.SUPPORTED_LANGUAGES,
    }

    # 检查外部依赖连通性
    dependencies: dict[str, Any] = {}

    # 1. Open-Meteo API
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            resp = await client.get(
                f"{settings.OPEN_METEO_BASE_URL}/forecast",
                params={"latitude": 22.82, "longitude": 108.32, "current": "temperature_2m"},
            )
            dependencies["open_meteo"] = "healthy" if resp.status_code == 200 else "degraded"
    except Exception:
        dependencies["open_meteo"] = "unhealthy"

    # 2. Redis（如果配置了）
    dependencies["redis"] = "not_configured"

    checks["dependencies"] = dependencies

    # 综合状态
    unhealthy = [k for k, v in dependencies.items() if v == "unhealthy"]
    if unhealthy:
        checks["status"] = "degraded"
        checks["degraded_dependencies"] = unhealthy

    return checks


@router.get("/metrics")
async def metrics() -> dict:
    """基础运行指标"""
    uptime = time.time() - _start_time
    return {
        "uptime_seconds": round(uptime, 1),
        "status": "running",
    }
