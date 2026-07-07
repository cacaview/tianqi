"""
万语风 (PolyWind) - FastAPI 主入口
面向中国—东盟的多语言气象智能决策助手
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import chat, weather, health, disaster
from app.services.disaster_service import shutdown_disaster_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print(f"🌤️ {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    print(f"📡 LLM模型: {settings.LLM_MODEL}")
    print(f"🌐 支持语言: {', '.join(settings.SUPPORTED_LANGUAGES)}")
    yield
    # 关闭时清理
    await shutdown_disaster_service()
    print(f"🌤️ {settings.APP_NAME} 已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="面向中国—东盟的多语言气象智能决策助手",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, tags=["健康检查"])
app.include_router(weather.router, prefix="/api/weather", tags=["气象数据"])
app.include_router(chat.router, prefix="/api/chat", tags=["智能对话"])
app.include_router(disaster.router, prefix="/api/disaster", tags=["灾害预警"])


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "slogan": "万种语言，一种风 —— 以AI连接气象与世界",
        "supported_languages": settings.SUPPORTED_LANGUAGES,
    }
