"""
Config 和 Logging 单元测试
"""

from __future__ import annotations

import pytest

from app.core.config import Environment, Settings, get_settings


def test_settings_defaults() -> None:
    """测试默认配置"""
    settings = Settings()
    assert settings.APP_NAME == "PolyWind 万语风"
    assert settings.ENVIRONMENT == Environment.DEVELOPMENT
    assert settings.DEBUG is True
    assert settings.PORT == 8000
    assert settings.LLM_TEMPERATURE == 0.3


def test_settings_temperature_validation() -> None:
    """测试温度范围校验"""
    with pytest.raises(Exception):
        Settings(LLM_TEMPERATURE=3.0)

    with pytest.raises(Exception):
        Settings(LLM_TEMPERATURE=-1.0)


def test_settings_port_validation() -> None:
    """测试端口范围校验"""
    with pytest.raises(Exception):
        Settings(PORT=0)

    with pytest.raises(Exception):
        Settings(PORT=99999)


def test_settings_language_validation() -> None:
    """测试语言代码校验"""
    with pytest.raises(Exception):
        Settings(SUPPORTED_LANGUAGES=["xx", "yy"])


def test_settings_properties() -> None:
    """测试派生属性"""
    dev = Settings(ENVIRONMENT=Environment.DEVELOPMENT)
    assert dev.is_development is True
    assert dev.is_production is False

    prod = Settings(
        ENVIRONMENT=Environment.PRODUCTION,
        OPENAI_API_KEY="test-key",
        CORS_ORIGINS=["https://example.com"],
    )
    assert prod.is_production is True
    assert prod.is_development is False


def test_settings_has_llm_key() -> None:
    """测试 LLM Key 检查"""
    s1 = Settings(DASHSCOPE_API_KEY="test", _env_file=None)
    assert s1.has_llm_key is True

    s2 = Settings(OPENAI_API_KEY="test", _env_file=None)
    assert s2.has_llm_key is True

    s3 = Settings(_env_file=None)
    assert s3.has_llm_key is False


def test_get_llm_config() -> None:
    """测试 LLM 配置获取"""
    s1 = Settings(DASHSCOPE_API_KEY="key1", LLM_MODEL="qwen-plus")
    config = s1.get_llm_config()
    assert config["provider"] == "dashscope"
    assert config["api_key"] == "key1"

    s2 = Settings(
        OPENAI_API_KEY="key2",
        LLM_PROVIDER="custom",
        LLM_BASE_URL="https://custom.api/v1",
        LLM_MODEL="gpt-4",
    )
    config = s2.get_llm_config()
    assert config["provider"] == "custom"
    assert config["base_url"] == "https://custom.api/v1"


def test_get_settings_singleton() -> None:
    """测试配置单例"""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
