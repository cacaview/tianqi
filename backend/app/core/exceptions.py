"""
统一错误码与异常体系
"""

from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    """业务错误码"""

    # 通用
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # 天气服务
    WEATHER_API_TIMEOUT = "WEATHER_API_TIMEOUT"
    WEATHER_API_ERROR = "WEATHER_API_ERROR"
    WEATHER_API_UNAVAILABLE = "WEATHER_API_UNAVAILABLE"

    # 灾害服务
    DISASTER_API_TIMEOUT = "DISASTER_API_TIMEOUT"
    DISASTER_API_ERROR = "DISASTER_API_ERROR"
    QWEATHER_API_ERROR = "QWEATHER_API_ERROR"

    # 空气质量服务
    AQ_API_TIMEOUT = "AQ_API_TIMEOUT"
    AQ_API_ERROR = "AQ_API_ERROR"

    # LLM
    LLM_API_TIMEOUT = "LLM_API_TIMEOUT"
    LLM_API_ERROR = "LLM_API_ERROR"
    LLM_NOT_CONFIGURED = "LLM_NOT_CONFIGURED"

    # 地震
    EARTHQUAKE_API_TIMEOUT = "EARTHQUAKE_API_TIMEOUT"
    EARTHQUAKE_API_ERROR = "EARTHQUAKE_API_ERROR"

    # 数据
    TYPHOON_NOT_FOUND = "TYPHOON_NOT_FOUND"

    # 海洋气象
    MARINE_API_TIMEOUT = "MARINE_API_TIMEOUT"
    MARINE_API_ERROR = "MARINE_API_ERROR"

    # 洪水预报
    FLOOD_API_TIMEOUT = "FLOOD_API_TIMEOUT"
    FLOOD_API_ERROR = "FLOOD_API_ERROR"

    # 历史气象
    HISTORICAL_API_TIMEOUT = "HISTORICAL_API_TIMEOUT"
    HISTORICAL_API_ERROR = "HISTORICAL_API_ERROR"


class AppError(Exception):
    """应用基础异常"""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        detail: str | None = None,
        status_code: int = 500,
    ):
        self.code = code
        self.message = message
        self.detail = detail
        self.status_code = status_code
        super().__init__(message)


class WeatherApiError(AppError):
    """天气 API 异常"""

    def __init__(self, message: str = "天气数据获取失败", detail: str | None = None):
        super().__init__(
            code=ErrorCode.WEATHER_API_ERROR,
            message=message,
            detail=detail,
            status_code=502,
        )


class WeatherApiTimeoutError(AppError):
    """天气 API 超时"""

    def __init__(self, message: str = "天气数据请求超时"):
        super().__init__(
            code=ErrorCode.WEATHER_API_TIMEOUT,
            message=message,
            status_code=504,
        )


class DisasterApiError(AppError):
    """灾害 API 异常"""

    def __init__(self, message: str = "灾害数据获取失败", detail: str | None = None):
        super().__init__(
            code=ErrorCode.DISASTER_API_ERROR,
            message=message,
            detail=detail,
            status_code=502,
        )


class LlmApiError(AppError):
    """LLM API 异常"""

    def __init__(self, message: str = "AI 服务调用失败", detail: str | None = None):
        super().__init__(
            code=ErrorCode.LLM_API_ERROR,
            message=message,
            detail=detail,
            status_code=502,
        )


class LlmNotConfiguredError(AppError):
    """LLM 未配置"""

    def __init__(self, message: str = "AI 服务未配置，请设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY"):
        super().__init__(
            code=ErrorCode.LLM_NOT_CONFIGURED,
            message=message,
            status_code=503,
        )


class AirQualityApiError(AppError):
    """空气质量 API 异常"""

    def __init__(self, message: str = "空气质量数据获取失败", detail: str | None = None):
        super().__init__(
            code=ErrorCode.AQ_API_ERROR,
            message=message,
            detail=detail,
            status_code=502,
        )


class NotFoundError(AppError):
    """资源不存在"""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=f"{resource} 不存在: {resource_id}",
            status_code=404,
        )


class EarthquakeApiError(AppError):
    """地震 API 异常"""

    def __init__(self, message: str = "地震数据获取失败", detail: str | None = None):
        super().__init__(
            code=ErrorCode.EARTHQUAKE_API_ERROR,
            message=message,
            detail=detail,
            status_code=502,
        )


class MarineApiError(AppError):
    """海洋气象 API 异常"""

    def __init__(self, message: str = "海洋气象数据获取失败", detail: str | None = None):
        super().__init__(
            code=ErrorCode.MARINE_API_ERROR,
            message=message,
            detail=detail,
            status_code=502,
        )


class FloodApiError(AppError):
    """洪水预报 API 异常"""

    def __init__(self, message: str = "洪水预报数据获取失败", detail: str | None = None):
        super().__init__(
            code=ErrorCode.FLOOD_API_ERROR,
            message=message,
            detail=detail,
            status_code=502,
        )


class HistoricalApiError(AppError):
    """历史气象 API 异常"""

    def __init__(self, message: str = "历史气象数据获取失败", detail: str | None = None):
        super().__init__(
            code=ErrorCode.HISTORICAL_API_ERROR,
            message=message,
            detail=detail,
            status_code=502,
        )
