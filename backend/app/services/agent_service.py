"""
Agent 服务 — LLM + 工具调用
"""

from __future__ import annotations

import structlog

from app.core.config import get_settings
from app.services.weather_service import WeatherService

logger = structlog.get_logger("services.agent")


class AgentService:
    """LLM Agent服务 - 处理用户对话"""

    def __init__(self):
        self.weather_service = WeatherService()
        self._agent = None  # LangChain Agent (Phase 2 lazy init)

    async def chat(
        self,
        message: str,
        language: str = "zh",
        latitude: float | None = None,
        longitude: float | None = None,
        session_id: str | None = None,
    ) -> dict:
        """处理用户对话"""
        settings = get_settings()
        # 尝试使用LangChain Agent（需要配置API Key）
        if settings.DASHSCOPE_API_KEY or settings.OPENAI_API_KEY:
            try:
                return await self._chat_with_agent(message, language, latitude, longitude, session_id)
            except Exception as e:
                logger.warning("agent_call_failed_fallback_to_rules", error=str(e))

        # 回退：简单规则匹配模式
        return await self._chat_with_rules(message, language, latitude, longitude)

    async def _chat_with_agent(
        self, message: str, language: str, latitude: float | None, longitude: float | None, session_id: str | None
    ) -> dict:
        """使用LangChain Agent处理对话"""
        if self._agent is None:
            self._init_agent()

        # 构建系统提示
        lang_name = {"zh": "中文", "en": "English", "vi": "Tiếng Việt", "th": "ภาษาไทย", "id": "Bahasa Indonesia"}.get(
            language, "English"
        )

        system_msg = (
            f"你是万语风(PolyWind)，面向中国—东盟的多语言气象智能决策助手。"
            f"请用{lang_name}回复。当前用户位置：纬度{latitude or 22.82}，经度{longitude or 108.32}。"
            f"如果用户问天气，请使用工具查询实时数据后给出建议。"
            f"When the user asks for a weather report or summary, "
            f"use the generate_weather_report tool to compose a structured report."
        )

        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [SystemMessage(content=system_msg), HumanMessage(content=message)]

        result = await self._agent.ainvoke({"messages": messages})

        # 提取最终回复和使用的工具
        reply = ""
        tools_used = []
        for msg in result.get("messages", []):
            if hasattr(msg, "content") and msg.content:
                reply = msg.content
            if hasattr(msg, "tool_calls"):
                for tc in msg.tool_calls:
                    tools_used.append(tc.get("name", ""))

        return {
            "reply": reply or self._get_default_reply(language),
            "language": language,
            "tools_used": tools_used,
        }

    def _init_agent(self):
        """初始化LangChain Agent"""
        from langchain_openai import ChatOpenAI
        from langgraph.prebuilt import create_react_agent

        from app.tools.weather_tools import WEATHER_TOOLS

        settings = get_settings()
        if settings.DASHSCOPE_API_KEY:
            # 通义千问（Qwen3）- 支持100+语言
            llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                api_key=settings.DASHSCOPE_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=settings.LLM_TEMPERATURE,
            )
            logger.info("llm_provider_selected", provider="dashscope", model=settings.LLM_MODEL)
        elif settings.OPENAI_API_KEY:
            # 自定义API端点（用户提供的API）
            llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.LLM_BASE_URL,
                temperature=settings.LLM_TEMPERATURE,
            )
            logger.info(
                "llm_provider_selected",
                provider="custom",
                model=settings.LLM_MODEL,
                base_url=settings.LLM_BASE_URL,
            )
        else:
            raise ValueError("未配置任何LLM API Key，请设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY")

        self._agent = create_react_agent(llm, WEATHER_TOOLS)
        logger.info("agent_initialized")

    async def _chat_with_rules(
        self, message: str, language: str, latitude: float | None, longitude: float | None
    ) -> dict:
        """规则匹配模式（MVP回退）"""
        tools_used = []

        if self._is_typhoon_query(message):
            from app.services.disaster_service import get_disaster_service

            service = get_disaster_service()
            typhoons = await service.get_typhoon_list()
            tools_used.append("get_typhoon_info")
            reply = self._format_typhoon_response(typhoons, language)
        elif self._is_alert_query(message):
            from app.services.disaster_service import get_disaster_service

            service = get_disaster_service()
            alerts = await service.get_regional_alerts("guangxi")
            tools_used.append("get_disaster_alert")
            reply = self._format_alert_response(alerts, language)
        elif self._is_agriculture_query(message):
            from app.services.disaster_service import get_disaster_service

            service = get_disaster_service()
            agri = await service.get_agriculture_alert("guangxi")
            tools_used.append("get_agriculture_advice")
            reply = self._format_agriculture_response(agri, language)
        elif self._is_earthquake_query(message):
            from app.services.earthquake_service import EarthquakeService

            service = EarthquakeService()
            result = await service.get_recent_earthquakes()
            await service.close()
            tools_used.append("get_earthquake_info")
            reply = self._format_earthquake_response(result, language)
        elif self._is_aqi_query(message):
            from app.services.air_quality_service import AirQualityService

            service = AirQualityService()
            lat = latitude or 22.82
            lon = longitude or 108.32
            aqi = await service.get_current(lat, lon)
            await service.close()
            tools_used.append("get_current_air_quality")
            reply = self._format_aqi_response(aqi, language)
        elif self._is_weather_query(message):
            lat = latitude or 22.82
            lon = longitude or 108.32
            weather = await self.weather_service.get_current_weather(lat, lon)
            tools_used.append("get_current_weather")
            reply = self._format_weather_response(weather, language)
        elif self._is_forecast_query(message):
            lat = latitude or 22.82
            lon = longitude or 108.32
            forecast = await self.weather_service.get_forecast(lat, lon, 3)
            tools_used.append("get_forecast")
            reply = self._format_forecast_response(forecast, language)
        elif self._is_lifestyle_query(message):
            from app.services.lifestyle_service import LifestyleService

            service = LifestyleService()
            lat = latitude or 22.82
            lon = longitude or 108.32
            result = await service.get_lifestyle_indices(lat, lon, language)
            tools_used.append("get_lifestyle_indices")
            reply = self._format_lifestyle_response(result, language)
        elif self._is_report_query(message):
            return await self._generate_report(latitude, longitude, language)
        elif self._is_health_index_query(message):
            from app.services.health_index_service import HealthIndexService

            service = HealthIndexService()
            lat = latitude or 22.82
            lon = longitude or 108.32
            result = await service.calculate(lat, lon, language)
            tools_used.append("get_health_index")
            level = result.get("level_zh", result["level"])
            rec = result.get("recommendation", "")
            reply = f"健康指数: {result['score']}/100 ({level})\n{rec}"
        elif self._is_construction_query(message):
            from app.services.construction_safety_service import ConstructionSafetyService

            service = ConstructionSafetyService()
            lat = latitude or 22.82
            lon = longitude or 108.32
            result = await service.assess(lat, lon, language)
            tools_used.append("get_construction_safety")
            decision = result.get("overall_decision_zh", result["overall_decision"])
            desc = result.get("description", "")
            reply = f"施工安全评估: {decision}\n{desc}"
        elif self._is_marine_query(message):
            reply = "海事气象功能可用，请提供起终点坐标获取航线风险评估"
            tools_used.append("get_marine_safety")
        elif self._is_energy_query(message):
            reply = "能源发电预测功能可用，请提供位置和装机容量获取预测"
            tools_used.append("get_solar_energy_forecast")
        elif self._is_insurance_query(message):
            reply = "农业保险指数功能可用，请提供位置和作物类型获取触发条件"
            tools_used.append("get_insurance_index")
        else:
            reply = self._get_default_reply(language)

        return {"reply": reply, "language": language, "tools_used": tools_used}

    def _is_typhoon_query(self, message: str) -> bool:
        keywords = ["台风", "typhoon", "bão", "พายุ", "badai", "bão tố"]
        return any(kw in message.lower() for kw in keywords)

    def _is_alert_query(self, message: str) -> bool:
        keywords = ["预警", "警报", "alert", "warning", "cảnh báo", "เตือน", "peringatan"]
        return any(kw in message.lower() for kw in keywords)

    def _is_agriculture_query(self, message: str) -> bool:
        keywords = ["农业", "农田", "水稻", "甘蔗", "agriculture", "farm", "crop", "nông nghiệp", "lúa", "เกษตร", "ข้าว"]
        return any(kw in message.lower() for kw in keywords)

    def _is_aqi_query(self, message: str) -> bool:
        keywords = [
            "空气质量",
            "aqi",
            "air quality",
            "pm2.5",
            "pm2_5",
            "pm10",
            "污染物",
            "雾霾",
            "粉尘",
            "chất lượng không khí",
            "ô nhiễm",
            "คุณภาพอากาศ",
            "ฝุ่น",
            "kualitas udara",
            "polusi",
        ]
        return any(kw in message.lower() for kw in keywords)

    def _is_earthquake_query(self, message: str) -> bool:
        keywords = [
            "地震",
            "earthquake",
            "động đất",
            "แผ่นดินไหว",
            "earth quake",
            "seismic",
            "gempa",
        ]
        return any(kw in message.lower() for kw in keywords)

    def _is_health_index_query(self, message: str) -> bool:
        keywords = ["健康指数", "健康评分", "health index", "health score", "chỉ số sức khỏe", "ดัชนีสุขภาพ"]
        return any(kw in message.lower() for kw in keywords)

    def _is_construction_query(self, message: str) -> bool:
        keywords = ["施工", "工地", "建筑安全", "construction", "build site", "thi công", "xây dựng", "ก่อสร้าง"]
        return any(kw in message.lower() for kw in keywords)

    def _is_marine_query(self, message: str) -> bool:
        keywords = ["海事", "航海", "航运", "浪高", "marine", "shipping", "sailing", "hàng hải", "เดินเรือ"]
        return any(kw in message.lower() for kw in keywords)

    def _is_energy_query(self, message: str) -> bool:
        keywords = ["太阳能", "光伏发电", "风力发电", "能源", "solar", "wind power", "energy", "năng lượng", "พลังงาน"]
        return any(kw in message.lower() for kw in keywords)

    def _is_insurance_query(self, message: str) -> bool:
        keywords = ["保险", "赔付", "触发条件", "insurance", "parametric", "bảo hiểm", "ประกัน"]
        return any(kw in message.lower() for kw in keywords)

    def _format_typhoon_response(self, typhoons: list, language: str) -> str:
        if not typhoons:
            no_typhoon = {
                "zh": "当前没有活跃台风",
                "en": "No active typhoons",
                "vi": "Không có bão hoạt động",
            }
            return no_typhoon.get(language, "No active typhoons")

        header = {
            "zh": "当前活跃台风：",
            "en": "Active Typhoons:",
            "vi": "Bão đang hoạt động:",
        }
        lines = [header.get(language, "Active Typhoons:")]
        for t in typhoons:
            lines.append(f"🌀 {t['name']} - {t['intensity']}, 风速 {t['max_wind_speed']} km/h")
            lines.append(f"   位置: 北纬{t['position']['lat']}°, 东经{t['position']['lon']}°")
            lines.append(f"   移动: {t['move_direction']} {t['move_speed']} km/h")
        return "\n".join(lines)

    def _format_alert_response(self, alerts: list, language: str) -> str:
        if not alerts:
            no_alert = {
                "zh": "暂无预警信息",
                "en": "No alerts",
                "vi": "Khong co canh bao",
            }
            return no_alert.get(language, "No alerts")

        headers = {
            "zh": f"灾害预警（共{len(alerts)}条）：",
            "en": f"Disaster Alerts ({len(alerts)}):",
            "vi": f"Canh bao ({len(alerts)}):",
        }
        lines = [headers.get(language, headers["en"])]
        for a in alerts[:3]:
            lines.append(f"⚠️ {a['level_name']}级 {a['type_name']}: {a['title']}")
        return "\n".join(lines)

    def _format_agriculture_response(self, agri: dict, language: str) -> str:
        headers = {"zh": "农业气象建议：", "en": "Agriculture Advice:", "vi": "Tu van nong nghiep:"}
        lines = [headers.get(language, headers["en"])]
        for a in agri.get("alerts", []):
            lines.append(f"🌾 {a['crop']} ({a['stage']})")
            lines.append(f"   风险: {a['risk']} - {a['advice']}")
        return "\n".join(lines)

    def _format_aqi_response(self, aqi: dict, language: str) -> str:
        current = aqi.get("current", {})
        pm25 = current.get("pm2_5", "N/A")
        pm10 = current.get("pm10", "N/A")
        aqi_val = current.get("us_aqi", "N/A")

        responses = {
            "zh": f"当前空气质量：US AQI {aqi_val}，PM2.5 {pm25} μg/m³，PM10 {pm10} μg/m³。",
            "en": f"Current air quality: US AQI {aqi_val}, PM2.5 {pm25} μg/m³, PM10 {pm10} μg/m³.",
            "vi": f"Chất lượng không khí hiện tại: US AQI {aqi_val}, PM2.5 {pm25} μg/m³, PM10 {pm10} μg/m³.",
        }
        return responses.get(language, responses["en"])

    def _format_earthquake_response(self, result: dict, language: str) -> str:
        earthquakes = result.get("earthquakes", [])
        if not earthquakes:
            no_eq = {
                "zh": "暂无近期地震信息",
                "en": "No recent earthquake information",
                "vi": "Không có thông tin động đất gần đây",
            }
            return no_eq.get(language, "No recent earthquake information")

        header = {
            "zh": f"近期地震信息（共{result.get('total', 0)}条）：",
            "en": f"Recent Earthquakes ({result.get('total', 0)}):",
            "vi": f"Thông tin động đất gần đây ({result.get('total', 0)}):",
        }
        lines = [header.get(language, header["en"])]
        for eq in earthquakes[:5]:
            lines.append(f"🔴 {eq['hypocenter']} - M{eq['magnitude']}")
            if eq.get("max_intensity"):
                lines.append(f"   最大烈度: {eq['max_intensity']}")
            if eq.get("occurred_at"):
                lines.append(f"   时间: {eq['occurred_at']}")
        return "\n".join(lines)

    def _is_weather_query(self, message: str) -> bool:
        keywords = [
            "天气",
            "气温",
            "温度",
            "下雨",
            "weather",
            "temperature",
            "rain",
            "mưa",
            "nhiệt độ",
            "thời tiết",
            "ฝน",
            "อุณหภูมิ",
            "สภาพอากาศ",
            "cuaca",
            "suhu",
        ]
        return any(kw in message.lower() for kw in keywords)

    def _is_forecast_query(self, message: str) -> bool:
        keywords = ["预报", "明天", "未来", "forecast", "tomorrow", "ngày mai", "พรุ่งนี้", "besok"]
        return any(kw in message.lower() for kw in keywords)

    def _is_report_query(self, message: str) -> bool:
        keywords = {
            "zh": ["天气报告", "天气预报总结", "天气总结", "天气概览"],
            "en": ["weather report", "weather summary", "weather overview"],
            "vi": ["báo cáo thời tiết", "tóm tắt thời tiết"],
            "th": ["รายงานสภาพอากาศ"],
            "id": ["laporan cuaca"],
        }
        lower_msg = message.lower()
        for lang_keywords in keywords.values():
            if any(k in lower_msg for k in lang_keywords):
                return True
        return False

    def _is_lifestyle_query(self, message: str) -> bool:
        keywords = {
            "zh": ["穿衣", "穿什么", "生活指数", "出门", "洗车"],
            "en": ["clothing", "what to wear", "dress", "lifestyle", "umbrella"],
            "vi": ["quần áo", "mặc gì", "chỉ số"],
            "th": ["เสื้อผ้า", "ใส่อะไร"],
            "id": ["pakaian", "pakai apa"],
        }
        lower_msg = message.lower()
        for lang_keywords in keywords.values():
            if any(k in lower_msg for k in lang_keywords):
                return True
        return False

    async def _generate_report(self, latitude: float | None, longitude: float | None, language: str) -> dict:
        """生成天气报告"""
        if latitude and longitude:
            from app.tools.weather_tools import WEATHER_TOOLS

            report_tool = next((t for t in WEATHER_TOOLS if t.name == "generate_weather_report"), None)
            if report_tool:
                report = report_tool.invoke({"latitude": latitude, "longitude": longitude, "language": language})
                return {"reply": report, "language": language, "tools_used": ["generate_weather_report"]}
        return {"reply": self._get_default_reply(language), "language": language}

    def _format_lifestyle_response(self, result: dict, language: str) -> str:
        """格式化生活指数响应"""
        indices = result.get("indices", [])
        if not indices:
            no_data = {
                "zh": "暂无生活指数数据",
                "en": "No lifestyle index data available",
                "vi": "Không có dữ liệu chỉ số sinh hoạt",
            }
            return no_data.get(language, "No lifestyle index data available")

        header = {
            "zh": "今日生活指数：",
            "en": "Today's Lifestyle Indices:",
            "vi": "Chỉ số sinh hoạt hôm nay:",
        }
        lines = [header.get(language, header["en"])]
        for idx in indices:
            icon_emoji = {
                "shirt": "👔",
                "car": "🚗",
                "run": "🏃",
                "sun": "☀️",
                "umbrella": "☂️",
                "map": "🗺️",
            }.get(idx.get("icon", ""), "📌")
            lines.append(f"{icon_emoji} {idx['name_zh']}：{idx['level_zh']} — {idx['description']}")
        return "\n".join(lines)

    def _format_weather_response(self, weather: dict, language: str) -> str:
        temp = weather.get("temperature", "N/A")
        humidity = weather.get("humidity", "N/A")
        wind = weather.get("wind_speed", "N/A")
        precip = weather.get("precipitation", 0)

        responses = {
            "zh": f"当前天气：气温 {temp}°C，湿度 {humidity}%，风速 {wind} km/h，降水量 {precip} mm。",
            "en": f"Current weather: Temperature {temp}°C, "
            f"Humidity {humidity}%, Wind {wind} km/h, "
            f"Precipitation {precip} mm.",
            "vi": f"Thời tiết hiện tại: Nhiệt độ {temp}°C, Độ ẩm {humidity}%, Gió {wind} km/h, Lượng mưa {precip} mm.",
        }
        return responses.get(language, responses["en"])

    def _format_forecast_response(self, forecast: dict, language: str) -> str:
        days = forecast.get("forecast", [])
        if not days:
            return "暂无预报数据" if language == "zh" else "No forecast data available"

        lines = []
        header = {"zh": "未来天气预报：", "en": "Weather Forecast:", "vi": "Dự báo thời tiết:"}
        lines.append(header.get(language, header["en"]))

        for day in days[:3]:
            date = day["date"]
            tmax = day["temp_max"]
            tmin = day["temp_min"]
            precip = day["precipitation"]
            lines.append(f"  {date}: {tmin}~{tmax}°C, {precip}mm")

        return "\n".join(lines)

    def _get_default_reply(self, language: str) -> str:
        replies = {
            "zh": "你好！我是万语风，你的多语言气象智能助手。你可以问我天气相关的问题，比如'南宁今天天气怎么样？'",
            "en": "Hello! I'm PolyWind, your multilingual weather assistant. Ask me about weather in any language!",
            "vi": "Xin chào! Tôi là PolyWind, trợ lý thời tiết đa ngôn ngữ. Hãy hỏi tôi về thời tiết.",
            "th": "สวัสดี! ฉันคือ PolyWind ผู้ช่วยด้านสภาพอากาศหลายภาษา ถามฉันเกี่ยวกับสภาพอากาศได้เลย",
            "id": "Halo! Saya PolyWind, asisten cuaca multilingual Anda. Tanyakan tentang cuaca kepada saya.",
        }
        return replies.get(language, replies["en"])
