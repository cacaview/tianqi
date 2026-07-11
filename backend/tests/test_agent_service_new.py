"""
AgentService 单元测试
测试规则匹配模式和查询识别
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


# === 查询识别测试 ===


def test_is_typhoon_query_chinese(agent_service: AgentService) -> None:
    """测试台风查询识别 — 中文"""
    assert agent_service._is_typhoon_query("今天有台风吗") is True
    assert agent_service._is_typhoon_query("台风路径") is True
    assert agent_service._is_typhoon_query("台风来了") is True


def test_is_typhoon_query_english(agent_service: AgentService) -> None:
    """测试台风查询识别 — 英文"""
    assert agent_service._is_typhoon_query("Is there a typhoon?") is True
    assert agent_service._is_typhoon_query("typhoon warning") is True


def test_is_typhoon_query_vietnamese(agent_service: AgentService) -> None:
    """测试台风查询识别 — 越南语"""
    assert agent_service._is_typhoon_query("Có bão không?") is True


def test_is_typhoon_query_negative(agent_service: AgentService) -> None:
    """测试台风查询识别 — 否定"""
    assert agent_service._is_typhoon_query("今天天气怎么样") is False
    assert agent_service._is_typhoon_query("我想吃饭") is False


def test_is_alert_query_chinese(agent_service: AgentService) -> None:
    """测试预警查询识别 — 中文"""
    assert agent_service._is_alert_query("有预警吗") is True
    assert agent_service._is_alert_query("暴雨警报") is True
    assert agent_service._is_alert_query("天气预警") is True


def test_is_alert_query_english(agent_service: AgentService) -> None:
    """测试预警查询识别 — 英文"""
    assert agent_service._is_alert_query("Any weather alerts?") is True
    assert agent_service._is_alert_query("warning signal") is True


def test_is_alert_query_negative(agent_service: AgentService) -> None:
    """测试预警查询识别 — 否定"""
    assert agent_service._is_alert_query("今天天气好") is False


def test_is_agriculture_query_chinese(agent_service: AgentService) -> None:
    """测试农业查询识别 — 中文"""
    assert agent_service._is_agriculture_query("水稻种植") is True
    assert agent_service._is_agriculture_query("甘蔗农田") is True
    assert agent_service._is_agriculture_query("农业建议") is True


def test_is_agriculture_query_english(agent_service: AgentService) -> None:
    """测试农业查询识别 — 英文"""
    assert agent_service._is_agriculture_query("agriculture advice") is True
    assert agent_service._is_agriculture_query("farm crop") is True


def test_is_aqi_query_chinese(agent_service: AgentService) -> None:
    """测试AQI查询识别 — 中文"""
    assert agent_service._is_aqi_query("空气质量怎么样") is True
    assert agent_service._is_aqi_query("PM2.5多少") is True
    assert agent_service._is_aqi_query("有雾霾吗") is True


def test_is_aqi_query_english(agent_service: AgentService) -> None:
    """测试AQI查询识别 — 英文"""
    assert agent_service._is_aqi_query("What's the air quality?") is True
    assert agent_service._is_aqi_query("PM2.5 level") is True


def test_is_weather_query_chinese(agent_service: AgentService) -> None:
    """测试天气查询识别 — 中文"""
    assert agent_service._is_weather_query("今天天气怎么样") is True
    assert agent_service._is_weather_query("温度多少") is True
    assert agent_service._is_weather_query("会下雨吗") is True


def test_is_weather_query_english(agent_service: AgentService) -> None:
    """测试天气查询识别 — 英文"""
    assert agent_service._is_weather_query("What's the weather like?") is True
    assert agent_service._is_weather_query("temperature today") is True


def test_is_forecast_query_chinese(agent_service: AgentService) -> None:
    """测试预报查询识别 — 中文"""
    assert agent_service._is_forecast_query("明天天气预报") is True
    assert agent_service._is_forecast_query("未来三天预报") is True


def test_is_forecast_query_english(agent_service: AgentService) -> None:
    """测试预报查询识别 — 英文"""
    assert agent_service._is_forecast_query("weather forecast tomorrow") is True
    assert agent_service._is_forecast_query("3 day forecast") is True


def test_is_earthquake_query_chinese(agent_service: AgentService) -> None:
    """测试地震查询识别 — 中文"""
    assert agent_service._is_earthquake_query("有地震吗") is True
    assert agent_service._is_earthquake_query("地震预警") is True


def test_is_earthquake_query_english(agent_service: AgentService) -> None:
    """测试地震查询识别 — 英文"""
    assert agent_service._is_earthquake_query("any earthquakes?") is True


def test_is_health_index_query(agent_service: AgentService) -> None:
    """测试健康指数查询识别"""
    assert agent_service._is_health_index_query("健康指数") is True
    assert agent_service._is_health_index_query("health index") is True


def test_is_construction_query(agent_service: AgentService) -> None:
    """测试施工安全查询识别"""
    assert agent_service._is_construction_query("可以施工吗") is True
    assert agent_service._is_construction_query("construction safety") is True


def test_is_marine_query(agent_service: AgentService) -> None:
    """测试海事查询识别"""
    assert agent_service._is_marine_query("海事安全吗") is True
    assert agent_service._is_marine_query("marine weather") is True


def test_is_energy_query(agent_service: AgentService) -> None:
    """测试能源查询识别"""
    assert agent_service._is_energy_query("光伏发电") is True
    assert agent_service._is_energy_query("solar energy") is True


def test_is_insurance_query(agent_service: AgentService) -> None:
    """测试保险查询识别"""
    assert agent_service._is_insurance_query("农业保险") is True
    assert agent_service._is_insurance_query("insurance index") is True


# === 默认回复测试 ===


def test_get_default_reply_chinese(agent_service: AgentService) -> None:
    """测试默认回复 — 中文"""
    reply = agent_service._get_default_reply("zh")
    assert len(reply) > 0
    assert "万语风" in reply


def test_get_default_reply_english(agent_service: AgentService) -> None:
    """测试默认回复 — 英文"""
    reply = agent_service._get_default_reply("en")
    assert len(reply) > 0
    assert "PolyWind" in reply


def test_get_default_reply_vietnamese(agent_service: AgentService) -> None:
    """测试默认回复 — 越南语"""
    reply = agent_service._get_default_reply("vi")
    assert len(reply) > 0


def test_get_default_reply_thai(agent_service: AgentService) -> None:
    """测试默认回复 — 泰语"""
    reply = agent_service._get_default_reply("th")
    assert len(reply) > 0


def test_get_default_reply_indonesian(agent_service: AgentService) -> None:
    """测试默认回复 — 印尼语"""
    reply = agent_service._get_default_reply("id")
    assert len(reply) > 0


def test_get_default_reply_unknown(agent_service: AgentService) -> None:
    """测试默认回复 — 未知语言"""
    reply = agent_service._get_default_reply("fr")
    assert len(reply) > 0


# === 格式化响应测试 ===


def test_format_weather_response(agent_service: AgentService) -> None:
    """测试天气响应格式化"""
    weather = {
        "temperature": 28.5,
        "humidity": 75,
        "wind_speed": 12.3,
        "precipitation": 0.0,
        "weather_code": 1,
    }
    reply = agent_service._format_weather_response(weather, "zh")
    assert "28.5" in reply
    assert "75" in reply


def test_format_forecast_response(agent_service: AgentService) -> None:
    """测试预报响应格式化"""
    forecast = {
        "forecast": [
            {
                "date": "2024-01-01",
                "temp_max": 28.0,
                "temp_min": 20.0,
                "precipitation": 0.0,
                "weather_code": 0,
            },
            {
                "date": "2024-01-02",
                "temp_max": 26.0,
                "temp_min": 18.0,
                "precipitation": 10.0,
                "weather_code": 61,
            },
        ],
    }
    reply = agent_service._format_forecast_response(forecast, "zh")
    assert "2024-01-01" in reply
    assert "28" in reply


def test_format_typhoon_response_empty(agent_service: AgentService) -> None:
    """测试台风响应格式化 — 空"""
    reply = agent_service._format_typhoon_response([], "zh")
    assert "无" in reply or "没有" in reply


def test_format_typhoon_response_with_data(agent_service: AgentService) -> None:
    """测试台风响应格式化 — 有数据"""
    typhoons = [
        {
            "name": "测试台风",
            "code": "WP01",
            "intensity": "TY",
            "max_wind_speed": 120,
            "position": {"lat": 15.0, "lon": 110.0},
            "move_direction": "西北",
            "move_speed": 20,
        },
    ]
    reply = agent_service._format_typhoon_response(typhoons, "zh")
    assert "测试台风" in reply


def test_format_alert_response_empty(agent_service: AgentService) -> None:
    """测试预警响应格式化 — 空"""
    reply = agent_service._format_alert_response([], "zh")
    assert "无" in reply or "没有" in reply


def test_format_alert_response_with_data(agent_service: AgentService) -> None:
    """测试预警响应格式化 — 有数据"""
    alerts = [
        {
            "level_name": "橙色",
            "type_name": "暴雨",
            "title": "暴雨橙色预警",
        },
    ]
    reply = agent_service._format_alert_response(alerts, "zh")
    assert "暴雨" in reply


def test_format_aqi_response(agent_service: AgentService) -> None:
    """测试AQI响应格式化"""
    aqi = {
        "current": {
            "us_aqi": 85,
            "pm2_5": 35.5,
            "pm10": 50.2,
        },
    }
    reply = agent_service._format_aqi_response(aqi, "zh")
    assert "85" in reply


def test_format_earthquake_response(agent_service: AgentService) -> None:
    """测试地震响应格式化"""
    result = {
        "earthquakes": [
            {
                "magnitude": 5.0,
                "hypocenter": "云南",
                "time": "2024-01-01T00:00:00",
            },
        ],
    }
    reply = agent_service._format_earthquake_response(result, "zh")
    assert "5" in reply


def test_format_agriculture_response(agent_service: AgentService) -> None:
    """测试农业响应格式化"""
    agri = {
        "alerts": [
            {
                "crop": "水稻",
                "stage": "抽穗期",
                "risk": "干旱",
                "advice": "注意灌溉",
            },
        ],
    }
    reply = agent_service._format_agriculture_response(agri, "zh")
    assert len(reply) > 0


def test_format_lifestyle_response(agent_service: AgentService) -> None:
    """测试生活指数响应格式化"""
    lifestyle = {
        "indices": [
            {
                "name": "clothing",
                "name_zh": "穿衣",
                "level": "comfortable",
                "level_zh": "舒适",
                "description": "建议穿长袖",
                "icon": "shirt",
            },
        ],
    }
    reply = agent_service._format_lifestyle_response(lifestyle, "zh")
    assert "穿衣" in reply


# === 规则匹配测试 ===


@pytest.mark.asyncio
async def test_chat_weather_query(agent_service: AgentService) -> None:
    """测试聊天 — 天气查询"""
    mock_response = {
        "current": {
            "temperature": 28.0,
            "humidity": 70,
            "wind_speed": 10.0,
            "precipitation": 0.0,
            "weather_code": 0,
        },
        "timezone": "Asia/Shanghai",
    }

    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        result = await agent_service.chat("今天天气怎么样", "zh", 22.82, 108.32)

    assert "reply" in result
    assert "language" in result
    assert "tools_used" in result
    assert result["language"] == "zh"
    assert len(result["reply"]) > 0


@pytest.mark.asyncio
async def test_chat_unknown_query(agent_service: AgentService) -> None:
    """测试聊天 — 未知查询"""
    result = await agent_service.chat("你好", "zh", 22.82, 108.32)

    assert "reply" in result
    assert result["language"] == "zh"
    assert len(result["reply"]) > 0


@pytest.mark.asyncio
async def test_chat_english(agent_service: AgentService) -> None:
    """测试聊天 — 英文"""
    result = await agent_service.chat("hello", "en", 22.82, 108.32)

    assert result["language"] == "en"
    assert len(result["reply"]) > 0


# === 更多查询识别测试 ===


def test_is_report_query_chinese(agent_service: AgentService) -> None:
    """测试报告查询识别 — 中文"""
    assert agent_service._is_report_query("天气报告") is True
    assert agent_service._is_report_query("天气总结") is True


def test_is_report_query_english(agent_service: AgentService) -> None:
    """测试报告查询识别 — 英文"""
    assert agent_service._is_report_query("weather report") is True
    assert agent_service._is_report_query("weather summary") is True


def test_is_lifestyle_query_chinese(agent_service: AgentService) -> None:
    """测试生活指数查询识别 — 中文"""
    assert agent_service._is_lifestyle_query("今天穿什么") is True
    assert agent_service._is_lifestyle_query("洗车指数") is True


def test_is_lifestyle_query_english(agent_service: AgentService) -> None:
    """测试生活指数查询识别 — 英文"""
    assert agent_service._is_lifestyle_query("what to wear today") is True
    assert agent_service._is_lifestyle_query("should I bring umbrella") is True


def test_is_earthquake_query_vietnamese(agent_service: AgentService) -> None:
    """测试地震查询识别 — 越南语"""
    assert agent_service._is_earthquake_query("động đất") is True


def test_is_aqi_query_vietnamese(agent_service: AgentService) -> None:
    """测试AQI查询识别 — 越南语"""
    assert agent_service._is_aqi_query("chất lượng không khí") is True


def test_is_weather_query_vietnamese(agent_service: AgentService) -> None:
    """测试天气查询识别 — 越南语"""
    assert agent_service._is_weather_query("thời tiết hôm nay") is True


def test_is_forecast_query_vietnamese(agent_service: AgentService) -> None:
    """测试预报查询识别 — 越南语"""
    assert agent_service._is_forecast_query("ngày mai") is True


def test_is_weather_query_thai(agent_service: AgentService) -> None:
    """测试天气查询识别 — 泰语"""
    assert agent_service._is_weather_query("สภาพอากาศ") is True


def test_is_forecast_query_thai(agent_service: AgentService) -> None:
    """测试预报查询识别 — 泰语"""
    assert agent_service._is_forecast_query("พรุ่งนี้") is True


def test_is_weather_query_indonesian(agent_service: AgentService) -> None:
    """测试天气查询识别 — 印尼语"""
    assert agent_service._is_weather_query("cuaca hari ini") is True


def test_is_forecast_query_indonesian(agent_service: AgentService) -> None:
    """测试预报查询识别 — 印尼语"""
    assert agent_service._is_forecast_query("besok") is True


def test_is_typhoon_query_thai(agent_service: AgentService) -> None:
    """测试台风查询识别 — 泰语"""
    assert agent_service._is_typhoon_query("พายุ") is True


def test_is_alert_query_thai(agent_service: AgentService) -> None:
    """测试预警查询识别 — 泰语"""
    assert agent_service._is_alert_query("เตือน") is True


def test_is_alert_query_indonesian(agent_service: AgentService) -> None:
    """测试预警查询识别 — 印尼语"""
    assert agent_service._is_alert_query("peringatan") is True


def test_is_agriculture_query_vietnamese(agent_service: AgentService) -> None:
    """测试农业查询识别 — 越南语"""
    assert agent_service._is_agriculture_query("nông nghiệp") is True
    assert agent_service._is_agriculture_query("lúa") is True


def test_is_agriculture_query_thai(agent_service: AgentService) -> None:
    """测试农业查询识别 — 泰语"""
    assert agent_service._is_agriculture_query("เกษตร") is True


def test_is_construction_query_vietnamese(agent_service: AgentService) -> None:
    """测试施工查询识别 — 越南语"""
    assert agent_service._is_construction_query("thi công") is True


def test_is_construction_query_thai(agent_service: AgentService) -> None:
    """测试施工查询识别 — 泰语"""
    assert agent_service._is_construction_query("ก่อสร้าง") is True


def test_is_marine_query_vietnamese(agent_service: AgentService) -> None:
    """测试海事查询识别 — 越南语"""
    assert agent_service._is_marine_query("hàng hải") is True


def test_is_energy_query_vietnamese(agent_service: AgentService) -> None:
    """测试能源查询识别 — 越南语"""
    assert agent_service._is_energy_query("năng lượng") is True


def test_is_insurance_query_vietnamese(agent_service: AgentService) -> None:
    """测试保险查询识别 — 越南语"""
    assert agent_service._is_insurance_query("bảo hiểm") is True


# === 格式化响应测试（更多场景）===


def test_format_typhoon_response_multiple(agent_service: AgentService) -> None:
    """测试台风响应格式化 — 多个台风"""
    typhoons = [
        {"name": "帕布", "intensity": "TS", "max_wind_speed": 65, "position": {"lat": 18.5, "lon": 112.3},
         "move_direction": "西北", "move_speed": 20},
        {"name": "蝴蝶", "intensity": "TY", "max_wind_speed": 120, "position": {"lat": 15.0, "lon": 130.0},
         "move_direction": "北", "move_speed": 15},
    ]
    reply = agent_service._format_typhoon_response(typhoons, "zh")
    assert "帕布" in reply
    assert "蝴蝶" in reply


def test_format_typhoon_response_english(agent_service: AgentService) -> None:
    """测试台风响应格式化 — 英文"""
    reply = agent_service._format_typhoon_response([], "en")
    assert "No active" in reply


def test_format_typhoon_response_vietnamese(agent_service: AgentService) -> None:
    """测试台风响应格式化 — 越南语"""
    reply = agent_service._format_typhoon_response([], "vi")
    assert len(reply) > 0


def test_format_alert_response_multiple(agent_service: AgentService) -> None:
    """测试预警响应格式化 — 多条预警"""
    alerts = [
        {"level_name": "橙色", "type_name": "暴雨", "title": "暴雨橙色预警"},
        {"level_name": "蓝色", "type_name": "台风", "title": "台风蓝色预警"},
    ]
    reply = agent_service._format_alert_response(alerts, "zh")
    assert "暴雨" in reply
    assert "台风" in reply


def test_format_alert_response_english(agent_service: AgentService) -> None:
    """测试预警响应格式化 — 英文"""
    reply = agent_service._format_alert_response([], "en")
    assert "No alerts" in reply


def test_format_aqi_response_english(agent_service: AgentService) -> None:
    """测试AQI响应格式化 — 英文"""
    aqi = {"current": {"us_aqi": 50, "pm2_5": 20.0, "pm10": 35.0}}
    reply = agent_service._format_aqi_response(aqi, "en")
    assert "50" in reply


def test_format_aqi_response_vietnamese(agent_service: AgentService) -> None:
    """测试AQI响应格式化 — 越南语"""
    aqi = {"current": {"us_aqi": 85, "pm2_5": 35.5, "pm10": 50.2}}
    reply = agent_service._format_aqi_response(aqi, "vi")
    assert "85" in reply


def test_format_earthquake_response_multiple(agent_service: AgentService) -> None:
    """测试地震响应格式化 — 多条"""
    result = {
        "total": 2,
        "earthquakes": [
            {"magnitude": 5.0, "hypocenter": "云南", "occurred_at": "2024-01-01T00:00:00"},
            {"magnitude": 4.5, "hypocenter": "四川", "occurred_at": "2024-01-02T00:00:00"},
        ],
    }
    reply = agent_service._format_earthquake_response(result, "zh")
    assert "云南" in reply
    assert "四川" in reply


def test_format_earthquake_response_empty(agent_service: AgentService) -> None:
    """测试地震响应格式化 — 空"""
    reply = agent_service._format_earthquake_response({"earthquakes": []}, "en")
    assert "No" in reply


def test_format_earthquake_response_vietnamese(agent_service: AgentService) -> None:
    """测试地震响应格式化 — 越南语"""
    reply = agent_service._format_earthquake_response({"earthquakes": []}, "vi")
    assert len(reply) > 0


def test_format_forecast_response_multi_day(agent_service: AgentService) -> None:
    """测试预报响应格式化 — 多天"""
    forecast = {
        "forecast": [
            {"date": "2024-01-01", "temp_max": 28.0, "temp_min": 20.0, "precipitation": 0.0},
            {"date": "2024-01-02", "temp_max": 26.0, "temp_min": 18.0, "precipitation": 10.0},
            {"date": "2024-01-03", "temp_max": 24.0, "temp_min": 16.0, "precipitation": 20.0},
        ],
    }
    reply = agent_service._format_forecast_response(forecast, "zh")
    assert "2024-01-01" in reply
    assert "2024-01-02" in reply
    assert "2024-01-03" in reply


def test_format_forecast_response_empty(agent_service: AgentService) -> None:
    """测试预报响应格式化 — 空"""
    reply = agent_service._format_forecast_response({"forecast": []}, "zh")
    assert "暂无" in reply


def test_format_forecast_response_english(agent_service: AgentService) -> None:
    """测试预报响应格式化 — 英文"""
    reply = agent_service._format_forecast_response({"forecast": []}, "en")
    assert "No" in reply


def test_format_lifestyle_response_empty(agent_service: AgentService) -> None:
    """测试生活指数响应格式化 — 空"""
    reply = agent_service._format_lifestyle_response({"indices": []}, "zh")
    assert "暂无" in reply


def test_format_lifestyle_response_english(agent_service: AgentService) -> None:
    """测试生活指数响应格式化 — 英文空"""
    reply = agent_service._format_lifestyle_response({"indices": []}, "en")
    assert "No" in reply


def test_format_lifestyle_response_multiple(agent_service: AgentService) -> None:
    """测试生活指数响应格式化 — 多项"""
    lifestyle = {
        "indices": [
            {"name": "clothing", "name_zh": "穿衣", "level_zh": "舒适", "description": "建议穿长袖", "icon": "shirt"},
            {"name": "car_wash", "name_zh": "洗车", "level_zh": "适宜", "description": "适合洗车", "icon": "car"},
            {"name": "exercise", "name_zh": "运动", "level_zh": "适宜", "description": "适合运动", "icon": "run"},
        ],
    }
    reply = agent_service._format_lifestyle_response(lifestyle, "zh")
    assert "穿衣" in reply
    assert "洗车" in reply
    assert "运动" in reply


def test_format_weather_response_english(agent_service: AgentService) -> None:
    """测试天气响应格式化 — 英文"""
    weather = {"temperature": 28.5, "humidity": 75, "wind_speed": 12.3, "precipitation": 0.0}
    reply = agent_service._format_weather_response(weather, "en")
    assert "28.5" in reply
    assert "75" in reply


def test_format_weather_response_vietnamese(agent_service: AgentService) -> None:
    """测试天气响应格式化 — 越南语"""
    weather = {"temperature": 28.5, "humidity": 75, "wind_speed": 12.3, "precipitation": 0.0}
    reply = agent_service._format_weather_response(weather, "vi")
    assert "28.5" in reply


def test_format_agriculture_response_with_alerts(agent_service: AgentService) -> None:
    """测试农业响应格式化 — 有预警"""
    agri = {
        "alerts": [
            {"crop": "水稻", "stage": "抽穗期", "risk": "暴雨倒伏", "advice": "提前排水"},
        ],
    }
    reply = agent_service._format_agriculture_response(agri, "zh")
    assert "水稻" in reply


@pytest.mark.asyncio
async def test_chat_with_rules_alert_query(agent_service: AgentService) -> None:
    """测试规则匹配 — 预警查询"""
    with respx.mock:
        respx.get("https://www.nhc.noaa.gov/CurrentStorms.json").mock(
            return_value=httpx.Response(500)
        )
        result = await agent_service._chat_with_rules("有预警吗", "zh", None, None)

    assert "reply" in result
    assert "tools_used" in result


@pytest.mark.asyncio
async def test_chat_with_rules_agriculture_query(agent_service: AgentService) -> None:
    """测试规则匹配 — 农业查询"""
    with respx.mock:
        respx.get("https://www.nhc.noaa.gov/CurrentStorms.json").mock(
            return_value=httpx.Response(500)
        )
        result = await agent_service._chat_with_rules("农业气象怎么样", "zh", None, None)

    assert "reply" in result


@pytest.mark.asyncio
async def test_chat_with_rules_earthquake_query(agent_service: AgentService) -> None:
    """测试规则匹配 — 地震查询"""
    result = await agent_service._chat_with_rules("最近有地震吗", "zh", None, None)

    assert "reply" in result


@pytest.mark.asyncio
async def test_chat_with_rules_aqi_query(agent_service: AgentService) -> None:
    """测试规则匹配 — 空气质量查询"""
    with respx.mock:
        respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
            return_value=httpx.Response(200, json={
                "current": {
                    "pm10": 25,
                    "pm2_5": 12,
                    "us_aqi": 48,
                },
            })
        )
        result = await agent_service._chat_with_rules("空气质量怎么样", "zh", 22.82, 108.32)

    assert "reply" in result


@pytest.mark.asyncio
async def test_chat_with_rules_weather_query(agent_service: AgentService) -> None:
    """测试规则匹配 — 天气查询"""
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json={
                "current": {
                    "temperature_2m": 25.0,
                    "relative_humidity_2m": 60,
                    "weather_code": 0,
                    "wind_speed_10m": 10.0,
                },
                "timezone": "Asia/Shanghai",
            })
        )
        result = await agent_service._chat_with_rules("今天天气怎么样", "zh", 22.82, 108.32)

    assert "reply" in result


@pytest.mark.asyncio
async def test_chat_with_rules_forecast_query(agent_service: AgentService) -> None:
    """测试规则匹配 — 预报查询"""
    with respx.mock:
        respx.get("https://api.open-meteo.com/v1/forecast").mock(
            return_value=httpx.Response(200, json={
                "daily": {
                    "time": ["2026-07-11", "2026-07-12"],
                    "temperature_2m_max": [30.0, 32.0],
                    "temperature_2m_min": [22.0, 23.0],
                    "precipitation_sum": [0.0, 5.0],
                    "weather_code": [0, 61],
                    "wind_speed_10m_max": [15.0, 20.0],
                },
                "timezone": "Asia/Shanghai",
            })
        )
        result = await agent_service._chat_with_rules("明天天气预报", "zh", 22.82, 108.32)

    assert "reply" in result


@pytest.mark.asyncio
async def test_chat_with_rules_unknown_query(agent_service: AgentService) -> None:
    """测试规则匹配 — 未知查询"""
    result = await agent_service._chat_with_rules("你好", "zh", None, None)

    assert "reply" in result
    assert "tools_used" in result
