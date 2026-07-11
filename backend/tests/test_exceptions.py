"""
异常类单元测试
"""

from __future__ import annotations

import pytest

from app.core.exceptions import (
    AppError,
    DisasterApiError,
    ErrorCode,
    LlmApiError,
    NotFoundError,
    WeatherApiError,
    WeatherApiTimeoutError,
)


def test_app_error_creation():
    """测试 AppError 创建"""
    err = AppError(
        code=ErrorCode.WEATHER_API_ERROR,
        message="test error",
        detail="test detail",
        status_code=500,
    )
    assert err.code == ErrorCode.WEATHER_API_ERROR
    assert err.message == "test error"
    assert err.detail == "test detail"
    assert err.status_code == 500
    assert str(err) == "test error"


def test_weather_api_error():
    """测试 WeatherApiError"""
    err = WeatherApiError()
    assert err.code == ErrorCode.WEATHER_API_ERROR
    assert err.status_code == 502
    assert "天气数据获取失败" in err.message


def test_weather_api_error_custom_message():
    """测试 WeatherApiError 自定义消息"""
    err = WeatherApiError(message="custom error", detail="custom detail")
    assert err.message == "custom error"
    assert err.detail == "custom detail"


def test_weather_api_timeout_error():
    """测试 WeatherApiTimeoutError"""
    err = WeatherApiTimeoutError()
    assert err.code == ErrorCode.WEATHER_API_TIMEOUT
    assert err.status_code == 504
    assert "超时" in err.message


def test_disaster_api_error():
    """测试 DisasterApiError"""
    err = DisasterApiError()
    assert err.code == ErrorCode.DISASTER_API_ERROR
    assert err.status_code == 502


def test_disaster_api_error_custom():
    """测试 DisasterApiError 自定义"""
    err = DisasterApiError(message="custom", detail="detail")
    assert err.message == "custom"
    assert err.detail == "detail"


def test_llm_api_error():
    """测试 LlmApiError"""
    err = LlmApiError()
    assert err.code == ErrorCode.LLM_API_ERROR
    assert err.status_code == 502


def test_llm_api_error_custom():
    """测试 LlmApiError 自定义"""
    err = LlmApiError(message="custom llm error")
    assert err.message == "custom llm error"


def test_not_found_error():
    """测试 NotFoundError"""
    err = NotFoundError(resource="用户", resource_id="123")
    assert err.code == ErrorCode.NOT_FOUND
    assert err.status_code == 404
    assert "用户" in err.message
    assert "123" in err.message


def test_error_code_enum():
    """测试 ErrorCode 枚举值"""
    assert ErrorCode.WEATHER_API_ERROR.value == "WEATHER_API_ERROR"
    assert ErrorCode.DISASTER_API_ERROR.value == "DISASTER_API_ERROR"
    assert ErrorCode.LLM_API_ERROR.value == "LLM_API_ERROR"
    assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
    assert ErrorCode.NOT_FOUND.value == "NOT_FOUND"
