"""
InsuranceIndexService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.insurance_index_service import InsuranceIndexService


@pytest.fixture
def insurance_service() -> InsuranceIndexService:
    """创建 InsuranceIndexService 实例"""
    return InsuranceIndexService()


@pytest.mark.asyncio
async def test_calculate_trigger_success(insurance_service: InsuranceIndexService) -> None:
    """测试计算保险触发条件 — 成功"""
    mock_response = {
        "daily": {
            "time": ["2023-01-01", "2023-01-02"],
            "temperature_2m_max": [25.0, 26.0],
            "temperature_2m_min": [15.0, 16.0],
            "temperature_2m_mean": [20.0, 21.0],
            "precipitation_sum": [5.0, 10.0],
            "wind_speed_10m_max": [10.0, 12.0],
            "weather_code": [1, 3],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await insurance_service.calculate_trigger(22.82, 108.32, "rice", 90, "zh")

    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["crop_type"] == "rice"
    assert result["policy_period_days"] == 90
    assert result["language"] == "zh"
    assert "triggers" in result
    assert "baseline" in result


@pytest.mark.asyncio
async def test_calculate_trigger_with_triggers(insurance_service: InsuranceIndexService) -> None:
    """测试计算保险触发条件 — 有触发条件"""
    mock_response = {
        "daily": {
            "time": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "temperature_2m_max": [30.0, 32.0, 35.0],
            "temperature_2m_min": [20.0, 22.0, 25.0],
            "temperature_2m_mean": [25.0, 27.0, 30.0],
            "precipitation_sum": [5.0, 10.0, 0.0],  # 有变化才能计算std
            "wind_speed_10m_max": [5.0, 6.0, 7.0],
            "weather_code": [0, 0, 0],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await insurance_service.calculate_trigger(22.82, 108.32, "rice", 90, "zh")

    assert len(result["triggers"]) > 0
    # 应该有干旱触发
    drought_triggers = [t for t in result["triggers"] if t["type"] == "drought"]
    assert len(drought_triggers) > 0


@pytest.mark.asyncio
async def test_calculate_trigger_http_error(insurance_service: InsuranceIndexService) -> None:
    """测试计算保险触发条件 — HTTP错误"""
    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(httpx.HTTPStatusError):
            await insurance_service.calculate_trigger(22.82, 108.32, "rice", 90, "zh")


@pytest.mark.asyncio
async def test_historical_risk_profile_success(insurance_service: InsuranceIndexService) -> None:
    """测试历史风险画像 — 成功"""
    mock_response = {
        "daily": {
            "time": ["2023-01-01"],
            "temperature_2m_max": [25.0],
            "temperature_2m_min": [15.0],
            "temperature_2m_mean": [20.0],
            "precipitation_sum": [5.0],
            "wind_speed_10m_max": [10.0],
            "weather_code": [1],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await insurance_service.historical_risk_profile(22.82, 108.32, "rice", "zh")

    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["crop_type"] == "rice"
    assert result["language"] == "zh"
    assert "risk_profile" in result


@pytest.mark.asyncio
async def test_historical_risk_profile_english(insurance_service: InsuranceIndexService) -> None:
    """测试历史风险画像 — 英文"""
    mock_response = {
        "daily": {
            "time": ["2023-01-01"],
            "temperature_2m_max": [25.0],
            "temperature_2m_min": [15.0],
            "temperature_2m_mean": [20.0],
            "precipitation_sum": [5.0],
            "wind_speed_10m_max": [10.0],
            "weather_code": [1],
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await insurance_service.historical_risk_profile(22.82, 108.32, "wheat", "en")

    assert result["crop_type"] == "wheat"
    assert result["language"] == "en"
