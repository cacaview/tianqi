"""
万语风 (PolyWind) - FastAPI 主入口
面向中国—东盟的多语言气象智能决策助手
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    agro,
    air_quality,
    chat,
    construction,
    disaster,
    disaster_cross_border,
    energy,
    haze,
    health,
    insurance,
    journal,
    marine,
    mutual_aid,
    notification,
    observation,
    photos,
    v1,
    weather,
    weather_health,
)
from app.api.deps import (
    close_air_quality_service,
    close_disaster_service,
    close_earthquake_service,
    close_flood_service,
    close_haze_monitor_service,
    close_historical_service,
    close_marine_service,
)
from app.core.config import get_settings, init_settings
from app.core.database import close_database
from app.core.logging import setup_logging
from app.middleware.error_handler import register_error_handlers
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security import register_security_middleware

logger = structlog.get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()
    logger.info(
        "app_starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT.value,
        llm_model=settings.LLM_MODEL,
    )
    yield
    await close_database()
    await close_haze_monitor_service()
    await close_marine_service()
    await close_flood_service()
    await close_historical_service()
    await close_earthquake_service()
    await close_air_quality_service()
    await close_disaster_service()
    logger.info("app_stopped", app_name=settings.APP_NAME)


# 启动时校验配置
settings = init_settings()

# 初始化日志系统
setup_logging(
    log_level="DEBUG" if settings.DEBUG else "INFO",
    json_output=settings.is_production,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="面向中国—东盟的多语言气象智能决策助手",
    lifespan=lifespan,
)

# 注册全局异常处理器
register_error_handlers(app)

# 注册安全中间件
register_security_middleware(app)

# 中间件（注意：后添加的中间件先执行）
# 1. 请求 ID
app.add_middleware(RequestIDMiddleware)

# 2. CORS（生产环境通过 CORS_ORIGINS 环境变量限制）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, tags=["健康检查"])
app.include_router(weather.router, prefix="/api/weather", tags=["气象数据"])
app.include_router(chat.router, prefix="/api/chat", tags=["智能对话"])
app.include_router(disaster.router, prefix="/api/disaster", tags=["灾害预警"])
app.include_router(air_quality.router, prefix="/api/air-quality", tags=["空气质量"])
app.include_router(weather_health.router, prefix="/api/weather", tags=["健康指数"])
app.include_router(construction.router, prefix="/api/construction", tags=["建筑安全"])
app.include_router(journal.router, prefix="/api/journal", tags=["气象日记"])
app.include_router(notification.router, prefix="/api/notification", tags=["天气播报"])
app.include_router(marine.router, prefix="/api/marine", tags=["海事气象"])
app.include_router(energy.router, prefix="/api/energy", tags=["能源预测"])
app.include_router(agro.router, prefix="/api/agro", tags=["农业决策"])
app.include_router(observation.router, prefix="/api/observation", tags=["众包观测"])
app.include_router(insurance.router, prefix="/api/insurance", tags=["保险指数"])
app.include_router(disaster_cross_border.router, prefix="/api/disaster/cross-border", tags=["跨境灾害"])
app.include_router(haze.router, prefix="/api/haze", tags=["烟霾监测"])
app.include_router(photos.router, prefix="/api/photos", tags=["照片墙"])
app.include_router(mutual_aid.router, prefix="/api/mutual-aid", tags=["互助圈"])
app.include_router(v1.router, prefix="/api/v1", tags=["企业API"])


@app.get("/")
async def root() -> dict:
    """服务根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "slogan": "万种语言，一种风 —— 以AI连接气象与世界",
        "supported_languages": settings.SUPPORTED_LANGUAGES,
    }
