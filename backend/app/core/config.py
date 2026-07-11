"""
万语风 (PolyWind) - 核心配置
支持多环境：development / staging / production
环境变量优先级 > .env 文件 > 默认值
"""

from __future__ import annotations

import os
import sys
from enum import StrEnum

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """运行环境枚举"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """应用配置 — 支持环境变量覆盖"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",
    )

    # ── 应用基础 ──
    APP_NAME: str = "PolyWind 万语风"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True

    # ── LLM 配置 ──
    LLM_PROVIDER: str = "dashscope"  # dashscope(通义千问) / openai / custom
    DASHSCOPE_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "qwen-plus"
    LLM_TEMPERATURE: float = 0.3
    LLM_TIMEOUT: float = 60.0  # 秒

    # ── 气象 API 配置 ──
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    OPEN_METEO_TIMEOUT: float = 10.0
    OPEN_METEO_AQ_BASE_URL: str = "https://air-quality-api.open-meteo.com/v1"
    OPEN_METEO_AQ_TIMEOUT: float = 10.0
    QWEATHER_API_KEY: str | None = None
    QWEATHER_BASE_URL: str = "https://devapi.qweather.com/v7"

    # ── NHC 台风数据 ──
    NHC_BASE_URL: str = "https://www.nhc.noaa.gov"
    NHC_TIMEOUT: float = 15.0

    # ── 海洋气象 API ──
    OPEN_METEO_MARINE_BASE_URL: str = "https://marine-api.open-meteo.com/v1"
    OPEN_METEO_MARINE_TIMEOUT: float = 10.0

    # ── 洪水预报 API ──
    OPEN_METEO_FLOOD_BASE_URL: str = "https://flood-api.open-meteo.com/v1"
    OPEN_METEO_FLOOD_TIMEOUT: float = 10.0

    # ── 历史气象 API ──
    OPEN_METEO_HISTORICAL_BASE_URL: str = "https://archive-api.open-meteo.com/v1"
    OPEN_METEO_HISTORICAL_TIMEOUT: float = 15.0

    # ── Wolfx 地震数据 ──
    WOLFX_BASE_URL: str = "https://api.wolfx.jp"
    WOLFX_TIMEOUT: float = 15.0

    # ── NASA FIRMS 火点数据 ──
    NASA_FIRMS_API_KEY: str | None = None

    # ── Redis 缓存 ──
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_ALERTS: int = 900  # 15 分钟（秒）
    CACHE_TTL_TYPHOONS: int = 1800  # 30 分钟（秒）

    # ── 服务配置 ──
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ── CORS ──
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── 限流 ──
    RATE_LIMIT: str = "60/minute"

    # ── 多语言 ──
    SUPPORTED_LANGUAGES: list[str] = ["zh", "en", "vi", "th", "id", "my", "lo"]
    DEFAULT_LANGUAGE: str = "zh"

    # ── 数据库配置 ──
    DATABASE_URL: str = "sqlite+aiosqlite:///./polywind.db"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20

    # ── 外部调用超时 ──
    HTTPX_DEFAULT_TIMEOUT: float = 30.0

    # ── 验证器 ──

    @field_validator("LLM_TEMPERATURE")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError(f"LLM_TEMPERATURE 必须在 0.0-2.0 之间，当前值: {v}")
        return v

    @field_validator("PORT")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError(f"PORT 必须在 1-65535 之间，当前值: {v}")
        return v

    @field_validator("SUPPORTED_LANGUAGES")
    @classmethod
    def validate_languages(cls, v: list[str]) -> list[str]:
        allowed = {"zh", "en", "vi", "th", "id", "my", "lo"}
        invalid = set(v) - allowed
        if invalid:
            raise ValueError(f"不支持的语言代码: {invalid}，允许的值: {allowed}")
        return v

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Settings:
        """生产环境必须配置至少一个 LLM API Key"""
        if self.ENVIRONMENT == Environment.PRODUCTION:
            if not self.DASHSCOPE_API_KEY and not self.OPENAI_API_KEY:
                raise ValueError("生产环境必须配置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY")
        return self

    # ── 派生属性 ──

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def has_llm_key(self) -> bool:
        return bool(self.DASHSCOPE_API_KEY or self.OPENAI_API_KEY)

    def get_llm_config(self) -> dict:
        """获取当前生效的 LLM 配置"""
        if self.DASHSCOPE_API_KEY:
            return {
                "provider": "dashscope",
                "api_key": self.DASHSCOPE_API_KEY,
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model": self.LLM_MODEL,
                "temperature": self.LLM_TEMPERATURE,
            }
        return {
            "provider": self.LLM_PROVIDER,
            "api_key": self.OPENAI_API_KEY,
            "base_url": self.LLM_BASE_URL,
            "model": self.LLM_MODEL,
            "temperature": self.LLM_TEMPERATURE,
        }


def create_settings() -> Settings:
    """
    创建 Settings 实例。
    支持通过 POLYWIND_ENV 环境变量切换环境（development/staging/production）。
    """
    env_name = os.environ.get("POLYWIND_ENV", "development")

    # 生产环境下 CORS 限制
    if env_name == "production":
        cors_raw = os.environ.get("CORS_ORIGINS", "")
        if not cors_raw:
            raise ValueError(
                "生产环境必须通过 CORS_ORIGINS 环境变量配置允许的域名，"
                "格式: CORS_ORIGINS=https://example.com,https://app.example.com"
            )

    return Settings(ENVIRONMENT=env_name)  # type: ignore[arg-type]


def validate_startup(settings: Settings) -> None:
    """
    启动时配置完整性校验。缺失必填配置时快速失败并给出明确提示。
    """
    errors: list[str] = []

    if settings.ENVIRONMENT == Environment.PRODUCTION:
        if not settings.DASHSCOPE_API_KEY and not settings.OPENAI_API_KEY:
            errors.append("❌ 未配置任何 LLM API Key。请设置环境变量 DASHSCOPE_API_KEY 或 OPENAI_API_KEY")
        if settings.CORS_ORIGINS == ["http://localhost:5173", "http://localhost:3000"]:
            errors.append("❌ 生产环境不应使用默认 CORS 配置。请设置 CORS_ORIGINS 为实际域名")
        if settings.DEBUG:
            errors.append("⚠️  生产环境建议关闭 DEBUG 模式 (DEBUG=false)")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        if any(e.startswith("❌") for e in errors):
            sys.exit(1)

    # 启动信息
    print(f"🌤️  {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   环境: {settings.ENVIRONMENT.value}")
    print(f"   模型: {settings.LLM_MODEL}")
    print(f"   语言: {', '.join(settings.SUPPORTED_LANGUAGES)}")
    print(f"   LLM: {'已配置' if settings.has_llm_key else '⚠️ 未配置（规则模式）'}")


# 全局单例（延迟初始化）
_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = create_settings()
    return _settings


def init_settings() -> Settings:
    """初始化并校验配置（应用启动时调用）"""
    global _settings
    _settings = create_settings()
    validate_startup(_settings)
    return _settings
