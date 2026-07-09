"""
Schema 和 Exception 单元测试
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.api.schemas import (
    AlertResponse,
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    TyphoonResponse,
    WeatherCurrentResponse,
)
from app.core.exceptions import (
    AppError,
    ErrorCode,
    LlmNotConfiguredError,
    NotFoundError,
    WeatherApiError,
)


def test_chat_request_valid() -> None:
    """测试有效 ChatRequest"""
    req = ChatRequest(message="今天天气", language="zh")
    assert req.message == "今天天气"
    assert req.language == "zh"
    assert req.latitude is None


def test_chat_request_message_too_long() -> None:
    """测试消息过长"""
    with pytest.raises(ValidationError):
        ChatRequest(message="x" * 2001)


def test_chat_request_empty_message() -> None:
    """测试空消息"""
    with pytest.raises(ValidationError):
        ChatRequest(message="")


def test_chat_request_invalid_language() -> None:
    """测试无效语言代码"""
    with pytest.raises(ValidationError):
        ChatRequest(message="hello", language="xx")


def test_chat_request_valid_coordinates() -> None:
    """测试有效坐标"""
    req = ChatRequest(
        message="天气",
        latitude=22.82,
        longitude=108.32,
    )
    assert req.latitude == 22.82


def test_chat_request_invalid_latitude() -> None:
    """测试无效纬度"""
    with pytest.raises(ValidationError):
        ChatRequest(message="天气", latitude=999)


def test_weather_response() -> None:
    """测试天气响应模型"""
    resp = WeatherCurrentResponse(
        temperature=25.0,
        humidity=80,
        latitude=22.82,
        longitude=108.32,
    )
    assert resp.temperature == 25.0
    assert resp.latitude == 22.82


def test_chat_response() -> None:
    """测试对话响应模型"""
    resp = ChatResponse(
        reply="天气晴朗",
        language="zh",
        tools_used=["get_weather"],
    )
    assert resp.reply == "天气晴朗"
    assert len(resp.tools_used) == 1


def test_error_response() -> None:
    """测试错误响应模型"""
    resp = ErrorResponse(
        error="请求失败",
        detail="超时",
        code="TIMEOUT",
    )
    assert resp.error == "请求失败"


def test_alert_response() -> None:
    """测试预警响应模型"""
    resp = AlertResponse(
        id="ALERT-001",
        type="rainstorm",
        type_name="暴雨",
        level="orange",
        level_name="橙色",
        title="暴雨预警",
        content="预计未来24小时有大暴雨",
        start_time="2024-01-01T00:00:00",
        end_time="2024-01-02T00:00:00",
        source="中央气象台",
    )
    assert resp.level == "orange"


def test_typhoon_response() -> None:
    """测试台风响应模型"""
    resp = TyphoonResponse(
        id="202425",
        name="帕布",
        code="PABUK",
        status="active",
        position={"lat": 18.5, "lon": 112.3},
        intensity="TS",
        max_wind_speed=65.0,
        pressure=990.0,
        source="NHC",
    )
    assert resp.intensity == "TS"


def test_app_error() -> None:
    """测试应用基础异常"""
    err = AppError(
        code=ErrorCode.WEATHER_API_TIMEOUT,
        message="天气数据请求超时",
        status_code=504,
    )
    assert err.code == ErrorCode.WEATHER_API_TIMEOUT
    assert err.status_code == 504


def test_weather_api_error() -> None:
    """测试天气 API 异常"""
    err = WeatherApiError()
    assert err.code == ErrorCode.WEATHER_API_ERROR
    assert err.status_code == 502


def test_not_found_error() -> None:
    """测试资源不存在异常"""
    err = NotFoundError("台风", "202425")
    assert err.code == ErrorCode.NOT_FOUND
    assert "台风" in err.message
    assert err.status_code == 404


def test_llm_not_configured_error() -> None:
    """测试 LLM 未配置异常"""
    err = LlmNotConfiguredError()
    assert err.code == ErrorCode.LLM_NOT_CONFIGURED
    assert err.status_code == 503
