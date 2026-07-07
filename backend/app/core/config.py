"""
万语风 (PolyWind) - 核心配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础
    APP_NAME: str = "PolyWind 万语风"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # LLM配置
    LLM_PROVIDER: str = "dashscope"  # dashscope(通义千问) / openai / custom
    DASHSCOPE_API_KEY: Optional[str] = None  # 通义千问API Key（支持Qwen3多语言）
    OPENAI_API_KEY: Optional[str] = None
    LLM_BASE_URL: str = "https://api.openai.com/v1"  # 自定义API端点
    LLM_MODEL: str = "qwen-plus"  # 默认模型
    LLM_TEMPERATURE: float = 0.3

    # 气象API配置
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    QWEATHER_API_KEY: Optional[str] = None  # 和风天气API Key
    QWEATHER_BASE_URL: str = "https://devapi.qweather.com/v7"

    # Redis缓存
    REDIS_URL: str = "redis://localhost:6379/0"

    # 服务端口
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 支持的语言
    SUPPORTED_LANGUAGES: list = ["zh", "en", "vi", "th", "id", "my", "lo"]
    DEFAULT_LANGUAGE: str = "zh"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
