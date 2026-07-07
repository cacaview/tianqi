"""
Agent服务 - LLM + 工具调用
Phase 1 MVP: 规则匹配 + 天气查询
Phase 2: LangChain Agent + Qwen3
"""
from typing import Optional
from app.services.weather_service import WeatherService
from app.core.config import settings


class AgentService:
    """LLM Agent服务 - 处理用户对话"""

    def __init__(self):
        self.weather_service = WeatherService()
        self._agent = None  # LangChain Agent (Phase 2 lazy init)

    async def chat(
        self,
        message: str,
        language: str = "zh",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        session_id: Optional[str] = None,
    ) -> dict:
        """处理用户对话"""
        # 尝试使用LangChain Agent（需要配置API Key）
        if settings.DASHSCOPE_API_KEY or settings.OPENAI_API_KEY:
            try:
                return await self._chat_with_agent(message, language, latitude, longitude, session_id)
            except Exception as e:
                print(f"Agent调用失败，回退到规则模式: {e}")

        # 回退：简单规则匹配模式
        return await self._chat_with_rules(message, language, latitude, longitude)

    async def _chat_with_agent(
        self, message: str, language: str, latitude: Optional[float],
        longitude: Optional[float], session_id: Optional[str]
    ) -> dict:
        """使用LangChain Agent处理对话"""
        if self._agent is None:
            self._init_agent()

        # 构建系统提示
        lang_name = {"zh": "中文", "en": "English", "vi": "Tiếng Việt",
                      "th": "ภาษาไทย", "id": "Bahasa Indonesia"}.get(language, "English")

        system_msg = (
            f"你是万语风(PolyWind)，面向中国—东盟的多语言气象智能决策助手。"
            f"请用{lang_name}回复。当前用户位置：纬度{latitude or 22.82}，经度{longitude or 108.32}。"
            f"如果用户问天气，请使用工具查询实时数据后给出建议。"
        )

        from langchain_core.messages import SystemMessage, HumanMessage
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

        if settings.DASHSCOPE_API_KEY:
            # 通义千问（Qwen3）- 支持100+语言
            llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                api_key=settings.DASHSCOPE_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=settings.LLM_TEMPERATURE,
            )
            print(f"✅ 使用通义千问 API，模型: {settings.LLM_MODEL}")
        elif settings.OPENAI_API_KEY:
            # 自定义API端点（用户提供的API）
            llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.LLM_BASE_URL,
                temperature=settings.LLM_TEMPERATURE,
            )
            print(f"✅ 使用自定义API，模型: {settings.LLM_MODEL}, 端点: {settings.LLM_BASE_URL}")
        else:
            raise ValueError("未配置任何LLM API Key，请设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY")

        self._agent = create_react_agent(llm, WEATHER_TOOLS)
        print(f"✅ Agent初始化完成")

    async def _chat_with_rules(
        self, message: str, language: str,
        latitude: Optional[float], longitude: Optional[float]
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

    def _format_typhoon_response(self, typhoons: list, language: str) -> str:
        if not typhoons:
            return {"zh": "当前没有活跃台风", "en": "No active typhoons", "vi": "Không có bão hoạt động"}.get(language, "No active typhoons")

        lines = [{"zh": "当前活跃台风：", "en": "Active Typhoons:", "vi": "Bão đang hoạt động:"}.get(language, "Active Typhoons:")]
        for t in typhoons:
            lines.append(f"🌀 {t['name']} - {t['intensity']}, 风速 {t['max_wind_speed']} km/h")
            lines.append(f"   位置: 北纬{t['position']['lat']}°, 东经{t['position']['lon']}°")
            lines.append(f"   移动: {t['move_direction']} {t['move_speed']} km/h")
        return "\n".join(lines)

    def _format_alert_response(self, alerts: list, language: str) -> str:
        if not alerts:
            return {"zh": "暂无预警信息", "en": "No alerts", "vi": "Khong co canh bao"}.get(language, "No alerts")

        headers = {"zh": f"灾害预警（共{len(alerts)}条）：", "en": f"Disaster Alerts ({len(alerts)}):", "vi": f"Canh bao ({len(alerts)}):"}
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

    def _is_weather_query(self, message: str) -> bool:
        keywords = ["天气", "气温", "温度", "下雨", "weather", "temperature", "rain",
                     "mưa", "nhiệt độ", "thời tiết", "ฝน", "อุณหภูมิ", "สภาพอากาศ", "cuaca", "suhu"]
        return any(kw in message.lower() for kw in keywords)

    def _is_forecast_query(self, message: str) -> bool:
        keywords = ["预报", "明天", "未来", "forecast", "tomorrow", "ngày mai", "พรุ่งนี้", "besok"]
        return any(kw in message.lower() for kw in keywords)

    def _format_weather_response(self, weather: dict, language: str) -> str:
        temp = weather.get("temperature", "N/A")
        humidity = weather.get("humidity", "N/A")
        wind = weather.get("wind_speed", "N/A")
        precip = weather.get("precipitation", 0)

        responses = {
            "zh": f"当前天气：气温 {temp}°C，湿度 {humidity}%，风速 {wind} km/h，降水量 {precip} mm。",
            "en": f"Current weather: Temperature {temp}°C, Humidity {humidity}%, Wind {wind} km/h, Precipitation {precip} mm.",
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
            "en": "Hello! I'm PolyWind, your multilingual weather assistant. Ask me about weather, e.g. 'What's the weather in Hanoi?'",
            "vi": "Xin chào! Tôi là PolyWind, trợ lý thời tiết đa ngôn ngữ. Hãy hỏi tôi về thời tiết.",
            "th": "สวัสดี! ฉันคือ PolyWind ผู้ช่วยด้านสภาพอากาศหลายภาษา ถามฉันเกี่ยวกับสภาพอากาศได้เลย",
            "id": "Halo! Saya PolyWind, asisten cuaca multilingual Anda. Tanyakan tentang cuaca kepada saya.",
        }
        return replies.get(language, replies["en"])
