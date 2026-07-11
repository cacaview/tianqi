"""
HealthIndexService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.health_index_service import HealthIndexService


@pytest.fixture
def health_service() -> HealthIndexService:
    """创建 HealthIndexService 实例"""
    return HealthIndexService()


@pytest.mark.asyncio
async def test_calculate_excellent(health_service: HealthIndexService) -> None:
    """测试健康指数计算 — 优秀"""
    mock_weather = {
        "current": {
            "temperature": 22.0,
            "weather_code": 0,
            "precipitation_probability": 0,
        },
        "timezone": "Asia/Shanghai",
    }
    mock_aqi = {
        "current": {"us_aqi": 30},
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_weather)
        )
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_aqi)
        )
        result = await health_service.calculate(22.82, 108.32, "zh")

    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["score"] >= 65
    assert result["level"] == "good"
    assert result["level_zh"] == "良好"
    assert len(result["components"]) == 4
    assert "recommendation" in result
    assert len(result["recommendation"]) > 0


@pytest.mark.asyncio
async def test_calculate_good(health_service: HealthIndexService) -> None:
    """测试健康指数计算 — 良好"""
    mock_weather = {
        "current": {
            "temperature": 25.0,
            "weather_code": 2,
            "precipitation_probability": 20,
        },
        "timezone": "Asia/Shanghai",
    }
    mock_aqi = {
        "current": {"us_aqi": 80},
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_weather)
        )
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_aqi)
        )
        result = await health_service.calculate(22.82, 108.32, "zh")

    assert result["score"] >= 60
    assert result["level"] == "good"
    assert result["level_zh"] == "良好"


@pytest.mark.asyncio
async def test_calculate_moderate(health_service: HealthIndexService) -> None:
    """测试健康指数计算 — 一般"""
    mock_weather = {
        "current": {
            "temperature": 30.0,
            "weather_code": 61,
            "precipitation_probability": 50,
        },
        "timezone": "Asia/Shanghai",
    }
    mock_aqi = {
        "current": {"us_aqi": 120},
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_weather)
        )
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_aqi)
        )
        result = await health_service.calculate(22.82, 108.32, "zh")

    assert result["score"] >= 60
    assert result["level"] == "good"
    assert result["level_zh"] == "良好"


@pytest.mark.asyncio
async def test_calculate_poor(health_service: HealthIndexService) -> None:
    """测试健康指数计算 — 较差"""
    mock_weather = {
        "current": {
            "temperature": 35.0,
            "weather_code": 95,
            "precipitation_probability": 80,
        },
        "timezone": "Asia/Shanghai",
    }
    mock_aqi = {
        "current": {"us_aqi": 180},
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_weather)
        )
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_aqi)
        )
        result = await health_service.calculate(22.82, 108.32, "zh")

    assert result["score"] >= 40
    assert result["level"] == "moderate"
    assert result["level_zh"] == "一般"


@pytest.mark.asyncio
async def test_calculate_very_poor(health_service: HealthIndexService) -> None:
    """测试健康指数计算 — 很差"""
    mock_weather = {
        "current": {
            "temperature": 40.0,
            "weather_code": 99,
            "precipitation_probability": 100,
        },
        "timezone": "Asia/Shanghai",
    }
    mock_aqi = {
        "current": {"us_aqi": 300},
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_weather)
        )
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_aqi)
        )
        result = await health_service.calculate(22.82, 108.32, "zh")

    assert result["score"] < 50
    assert result["level"] in ["moderate", "poor", "very_poor"]
    assert result["level_zh"] in ["一般", "较差", "很差"]


@pytest.mark.asyncio
async def test_calculate_different_languages(health_service: HealthIndexService) -> None:
    """测试健康指数计算 — 多语言"""
    mock_weather = {
        "current": {
            "temperature": 22.0,
            "weather_code": 0,
            "precipitation_probability": 0,
        },
        "timezone": "Asia/Shanghai",
    }
    mock_aqi = {
        "current": {"us_aqi": 30},
    }

    languages = ["zh", "en", "vi", "th", "id"]
    for lang in languages:
        with respx.mock:
            respx.get("https://api.open-meteo.com/v1/forecast").mock(
                return_value=httpx.Response(200, json=mock_weather)
            )
            respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
                return_value=httpx.Response(200, json=mock_aqi)
            )
            result = await health_service.calculate(22.82, 108.32, lang)

        assert result["language"] == lang
        assert "recommendation" in result
        assert len(result["recommendation"]) > 0


@pytest.mark.asyncio
async def test_calculate_with_null_values(health_service: HealthIndexService) -> None:
    """测试健康指数计算 — 空值处理"""
    mock_weather = {
        "current": {
            "temperature": None,
            "weather_code": None,
            "precipitation_probability": None,
        },
        "timezone": "Asia/Shanghai",
    }
    mock_aqi = {
        "current": {"us_aqi": None},
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_weather)
        )
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_aqi)
        )
        result = await health_service.calculate(22.82, 108.32, "zh")

    assert result["score"] > 0
    assert result["level"] in ["excellent", "good", "moderate", "poor", "very_poor"]
    assert len(result["components"]) == 4
    for component in result["components"]:
        assert "score" in component
        assert "weight" in component
        assert "description" in component


@pytest.mark.asyncio
async def test_calculate_weather_http_error(health_service: HealthIndexService) -> None:
    """测试健康指数计算 — 天气API错误"""
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await health_service.calculate(22.82, 108.32, "zh")


@pytest.mark.asyncio
async def test_calculate_aqi_http_error(health_service: HealthIndexService) -> None:
    """测试健康指数计算 — AQI API错误"""
    mock_weather = {
        "current": {"temperature": 25.0, "weather_code": 0},
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_weather)
        )
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await health_service.calculate(22.82, 108.32, "zh")


@pytest.mark.asyncio
async def test_calculate_components(health_service: HealthIndexService) -> None:
    """测试健康指数计算 — 组件详情"""
    mock_weather = {
        "current": {
            "temperature_2m": 25.0,
            "relative_humidity_2m": 60,
            "apparent_temperature": 26.0,
            "precipitation": 0.0,
            "weather_code": 2,
            "wind_speed_10m": 10.0,
            "wind_direction_10m": 180,
        },
        "timezone": "Asia/Shanghai",
    }
    mock_aqi = {
        "current": {"us_aqi": 75},
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_weather)
        )
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json=mock_aqi)
        )
        result = await health_service.calculate(22.82, 108.32, "zh")

    assert len(result["components"]) == 4

    # 验证温度组件
    temp_comp = result["components"][0]
    assert temp_comp["name"] == "temperature_comfort"
    assert temp_comp["name_zh"] == "温度舒适度"
    assert temp_comp["weight"] == 0.30

    # 验证AQI组件
    aqi_comp = result["components"][1]
    assert aqi_comp["name"] == "air_quality"
    assert aqi_comp["name_zh"] == "空气质量"
    assert aqi_comp["weight"] == 0.30

    # 验证UV组件
    uv_comp = result["components"][2]
    assert uv_comp["name"] == "uv_index"
    assert uv_comp["name_zh"] == "紫外线"
    assert uv_comp["weight"] == 0.20

    # 验证降水组件
    precip_comp = result["components"][3]
    assert precip_comp["name"] == "precipitation"
    assert precip_comp["name_zh"] == "降水概率"
    assert precip_comp["weight"] == 0.20
