"""
智慧农业气象决策服务
灌溉建议、病虫害风险、收获窗口规划
"""

from __future__ import annotations

import structlog

from app.services.weather_service import WeatherService

logger = structlog.get_logger("services.agro_decision")

# 灌溉阈值
SOIL_MOISTURE_LOW: float = 30.0  # % — 需要灌溉
SOIL_MOISTURE_HIGH: float = 70.0  # % — 充足
EVAPOTRANSPIRATION_HIGH: float = 5.0  # mm/day — 高蒸发需增加灌溉

# 病虫害风险条件
PEST_TEMP_RANGE: tuple[float, float] = (20.0, 30.0)  # °C
PEST_HUMIDITY_THRESHOLD: float = 80.0  # %

# 多语言建议
IRRIGATION_ADVICE: dict[str, str] = {
    "zh": "土壤湿度低（{soil_moisture}%），建议进行灌溉",
    "en": "Low soil moisture ({soil_moisture}%), irrigation recommended",
    "vi": "Độ ẩm đất thấp ({soil_moisture}%), nên tưới nước",
    "th": "ความชื้นในดินต่ำ ({soil_moisture}%) แนะนำให้รดน้ำ",
    "id": "Kelembaban tanah rendah ({soil_moisture}%), disarankan irigasi",
}

HARVEST_ADVICE: dict[str, str] = {
    "zh": "未来{dry_days}天无雨，适合收获作业",
    "en": "{dry_days} dry days ahead, suitable for harvest",
    "vi": "{dry_days} ngày không mưa, phù hợp cho thu hoạch",
    "th": "{dry_days} วันไม่มีฝน เหมาะสำหรับการเก็บเกี่ยว",
    "id": "{dry_days} hari tanpa hujan, cocok untuk panen",
}


class AgroDecisionService:
    """智慧农业气象决策服务"""

    def __init__(self) -> None:
        self._weather_service = WeatherService()

    async def irrigation_advice(self, latitude: float, longitude: float, language: str = "zh") -> dict:
        """灌溉建议 — 基于土壤湿度和蒸发量"""
        forecast = await self._weather_service.get_forecast(latitude, longitude, days=3)
        daily = forecast.get("forecast", [])

        if not daily:
            return {"latitude": latitude, "longitude": longitude, "advice": "数据不足", "irrigation_needed": None}

        # 基于降水和天气代码估算土壤湿度状态
        precip_today = daily[0].get("precipitation", 0) or 0
        code_today = daily[0].get("weather_code", 0) or 0

        # 简化估算
        if precip_today >= 10:
            moisture_est = 80.0
        elif precip_today >= 2:
            moisture_est = 55.0
        elif code_today in (0, 1):
            moisture_est = 25.0  # 晴天干燥
        else:
            moisture_est = 40.0

        irrigation_needed = moisture_est < SOIL_MOISTURE_LOW
        lang = language if language in IRRIGATION_ADVICE else "en"
        advice = IRRIGATION_ADVICE[lang].format(soil_moisture=moisture_est)

        return {
            "latitude": latitude,
            "longitude": longitude,
            "estimated_soil_moisture": moisture_est,
            "irrigation_needed": irrigation_needed,
            "advice": advice,
            "language": language,
        }

    async def pest_risk(self, latitude: float, longitude: float, language: str = "zh") -> dict:
        """病虫害风险评估 — 基于温度+湿度组合"""
        weather = await self._weather_service.get_current_weather(latitude, longitude)

        temp = weather.get("temperature", 0) or 0
        humidity = weather.get("humidity", 0) or 0

        # 风险评估
        risk_level = "low"
        if PEST_TEMP_RANGE[0] <= temp <= PEST_TEMP_RANGE[1] and humidity >= PEST_HUMIDITY_THRESHOLD:
            risk_level = "high"
        elif PEST_TEMP_RANGE[0] <= temp <= PEST_TEMP_RANGE[1] and humidity >= 60:
            risk_level = "moderate"

        return {
            "latitude": latitude,
            "longitude": longitude,
            "temperature": temp,
            "humidity": humidity,
            "risk_level": risk_level,
            "language": language,
        }

    async def harvest_window(self, latitude: float, longitude: float, language: str = "zh") -> dict:
        """收获窗口规划 — 找连续无雨天"""
        forecast = await self._weather_service.get_forecast(latitude, longitude, days=7)
        daily = forecast.get("forecast", [])

        dry_windows = []
        current_streak = []

        for day in daily:
            precip = day.get("precipitation", 0) or 0
            if precip < 1.0:
                current_streak.append(day.get("date"))
            else:
                if current_streak:
                    dry_windows.append(current_streak)
                    current_streak = []
        if current_streak:
            dry_windows.append(current_streak)

        best_window = max(dry_windows, key=len) if dry_windows else []
        lang = language if language in HARVEST_ADVICE else "en"
        advice = HARVEST_ADVICE[lang].format(dry_days=len(best_window)) if best_window else "近期无连续无雨窗口"

        return {
            "latitude": latitude,
            "longitude": longitude,
            "best_window": best_window,
            "dry_days": len(best_window),
            "advice": advice,
            "language": language,
        }
