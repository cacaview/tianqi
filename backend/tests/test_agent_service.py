"""
AgentService 单元测试
"""

from __future__ import annotations

import httpx
import pytest
import respx

from app.services.agent_service import AgentService


@pytest.fixture
def agent_service() -> AgentService:
    """创建 AgentService 实例"""
    return AgentService()


def test_is_typhoon_query(agent_service: AgentService) -> None:
    """测试台风意图识别"""
    assert agent_service._is_typhoon_query("现在有台风吗") is True
    assert agent_service._is_typhoon_query("typhoon info") is True
    assert agent_service._is_typhoon_query("天气怎么样") is False


def test_is_alert_query(agent_service: AgentService) -> None:
    """测试预警意图识别"""
    assert agent_service._is_alert_query("有预警吗") is True
    assert agent_service._is_alert_query("warning alert") is True
    assert agent_service._is_alert_query("今天天气好") is False


def test_is_agriculture_query(agent_service: AgentService) -> None:
    """测试农业意图识别"""
    assert agent_service._is_agriculture_query("农业气象") is True
    assert agent_service._is_agriculture_query("水稻种植") is True
    assert agent_service._is_agriculture_query("weather forecast") is False


def test_is_weather_query(agent_service: AgentService) -> None:
    """测试天气意图识别"""
    assert agent_service._is_weather_query("今天天气") is True
    assert agent_service._is_weather_query("weather") is True
    assert agent_service._is_weather_query("台风路径") is False


def test_is_forecast_query(agent_service: AgentService) -> None:
    """测试预报意图识别"""
    assert agent_service._is_forecast_query("明天天气预报") is True
    assert agent_service._is_forecast_query("forecast") is True
    assert agent_service._is_forecast_query("现在天气") is False


def test_is_report_query(agent_service: AgentService) -> None:
    """测试报告意图识别"""
    assert agent_service._is_report_query("生成天气报告") is True
    assert agent_service._is_report_query("weather report") is True
    assert agent_service._is_report_query("今天天气怎么样") is False


def test_get_default_reply(agent_service: AgentService) -> None:
    """测试默认回复"""
    reply_zh = agent_service._get_default_reply("zh")
    assert "万语风" in reply_zh

    reply_en = agent_service._get_default_reply("en")
    assert "PolyWind" in reply_en

    reply_vi = agent_service._get_default_reply("vi")
    assert "PolyWind" in reply_vi


def test_format_weather_response(agent_service: AgentService) -> None:
    """测试天气响应格式化"""
    weather = {
        "temperature": 28.5,
        "humidity": 75,
        "wind_speed": 12.3,
        "precipitation": 0.0,
    }
    reply_zh = agent_service._format_weather_response(weather, "zh")
    assert "28.5" in reply_zh
    assert "75" in reply_zh

    reply_en = agent_service._format_weather_response(weather, "en")
    assert "Temperature" in reply_en


def test_format_typhoon_response(agent_service: AgentService) -> None:
    """测试台风响应格式化"""
    # 空列表
    reply = agent_service._format_typhoon_response([], "zh")
    assert "没有活跃台风" in reply

    # 有台风
    typhoons = [
        {
            "name": "帕布",
            "intensity": "TS",
            "max_wind_speed": 65,
            "position": {"lat": 18.5, "lon": 112.3},
            "move_direction": "西北",
            "move_speed": 20,
        }
    ]
    reply = agent_service._format_typhoon_response(typhoons, "zh")
    assert "帕布" in reply
    assert "65" in reply


def test_format_alert_response(agent_service: AgentService) -> None:
    """测试预警响应格式化"""
    # 空列表
    reply = agent_service._format_alert_response([], "zh")
    assert "暂无预警信息" in reply

    # 有预警
    alerts = [
        {
            "level_name": "橙色",
            "type_name": "暴雨",
            "title": "暴雨橙色预警",
        }
    ]
    reply = agent_service._format_alert_response(alerts, "zh")
    assert "暴雨" in reply


def test_format_agriculture_response(agent_service: AgentService) -> None:
    """测试农业响应格式化"""
    agri = {
        "alerts": [
            {
                "crop": "水稻",
                "stage": "抽穗期",
                "risk": "暴雨倒伏",
                "advice": "提前排水",
            }
        ]
    }
    reply = agent_service._format_agriculture_response(agri, "zh")
    assert "水稻" in reply
    assert "提前排水" in reply


def test_format_forecast_response(agent_service: AgentService) -> None:
    """测试预报响应格式化"""
    # 空数据
    reply = agent_service._format_forecast_response({}, "zh")
    assert "暂无预报数据" in reply

    # 有数据
    forecast = {
        "forecast": [
            {"date": "2024-01-01", "temp_max": 28, "temp_min": 20, "precipitation": 0},
            {"date": "2024-01-02", "temp_max": 26, "temp_min": 18, "precipitation": 5},
        ]
    }
    reply = agent_service._format_forecast_response(forecast, "zh")
    assert "2024-01-01" in reply
    assert "28" in reply


@pytest.mark.asyncio
async def test_chat_fallback_to_rules(agent_service: AgentService) -> None:
    """测试对话回退到规则模式（无 API Key）"""
    with respx.mock:
        # 模拟天气查询
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(
                200,
                json={
                    "current": {
                        "temperature_2m": 25.0,
                        "relative_humidity_2m": 80,
                        "apparent_temperature": 27.0,
                        "precipitation": 0.0,
                        "weather_code": 2,
                        "wind_speed_10m": 10.0,
                        "wind_direction_10m": 90,
                    },
                    "timezone": "Asia/Shanghai",
                },
            )
        )
        result = await agent_service.chat(
            message="今天天气怎么样",
            language="zh",
            latitude=22.82,
            longitude=108.32,
        )

    assert "reply" in result
    assert result["language"] == "zh"


@pytest.mark.asyncio
async def test_chat_typhoon_query(agent_service: AgentService) -> None:
    """测试台风查询对话"""
    with respx.mock:
        respx.get("https://www.nhc.noaa.gov/CurrentStorms.json").mock(return_value=httpx.Response(500))
        result = await agent_service.chat(
            message="有台风吗",
            language="zh",
        )

    assert "reply" in result
    assert "台风" in result["reply"] or "bão" in result["reply"]


@pytest.mark.asyncio
async def test_chat_unknown_query(agent_service: AgentService) -> None:
    """测试未知意图查询"""
    result = await agent_service.chat(
        message="你好",
        language="zh",
    )

    assert "reply" in result
    assert "万语风" in result["reply"]
