"""
建筑工地气象安全评估服务
基于风速、雷暴、热应力、降水四因子判断Go/No-Go/Caution
"""

from __future__ import annotations

import structlog

from app.services.weather_service import WeatherService

logger = structlog.get_logger("services.construction_safety")

# 安全阈值（参考中国建筑施工安全标准JGJ59-2011）
WIND_SPEED_LIMIT: float = 40.0  # km/h — 高空作业停止
WIND_SPEED_CAUTION: float = 25.0  # km/h — 注意
RAINFALL_LIMIT: float = 10.0  # mm/h — 停工
RAINFALL_CAUTION: float = 5.0  # mm/h — 注意
HEAT_STRESS_LIMIT: float = 40.0  # °C 体感温度 — 停工
HEAT_STRESS_CAUTION: float = 35.0  # °C — 注意
LIGHTNING_RISK_CODES: set[int] = {95, 96, 99}  # 雷暴天气代码

# 多语言描述
DESCRIPTIONS: dict[str, dict[str, str]] = {
    "go": {
        "zh": "天气条件适合施工",
        "en": "Weather conditions suitable for construction",
        "vi": "Điều kiện thời tiết phù hợp để thi công",
        "th": "สภาพอากาศเหมาะสมสำหรับการก่อสร้าง",
        "id": "Kondisi cuaca cocok untuk konstruksi",
    },
    "caution": {
        "zh": "天气条件需注意，建议加强防护",
        "en": "Weather requires caution, enhanced protection recommended",
        "vi": "Thời tiết cần chú ý, nên tăng cường biện pháp bảo vệ",
        "th": "สภาพอากาศต้องระวัง ควรเพิ่มมาตรการป้องกัน",
        "id": "Cuaca perlu kewaspadaan, tingkatkan perlindungan",
    },
    "no_go": {
        "zh": "天气条件恶劣，建议停工",
        "en": "Severe weather, work stoppage recommended",
        "vi": "Thời tiết khắc nghiệt, khuyến nghị ngừng thi công",
        "th": "สภาพอากาศรุนแรง แนะนำหยุดทำงาน",
        "id": "Cuaca ekstrem, disarankan menghentikan pekerjaan",
    },
}

# 工种限制风速
OCCUPATION_WIND_LIMITS: dict[str, float] = {
    "crane": 20.0,  # 起重机
    "scaffolding": 25.0,  # 脚手架
    "high_rise": 30.0,  # 高层作业
    "general": WIND_SPEED_LIMIT,  # 一般施工
}


class ConstructionSafetyService:
    """建筑工地气象安全评估服务"""

    def __init__(self) -> None:
        self._weather_service = WeatherService()

    async def assess(self, latitude: float, longitude: float, language: str = "zh") -> dict:
        """评估施工安全条件"""
        forecast = await self._weather_service.get_forecast(latitude, longitude, days=1)
        current = await self._weather_service.get_current_weather(latitude, longitude)

        current_data = current.get("current", {})
        forecast_data = forecast.get("forecast", [])
        today = forecast_data[0] if forecast_data else {}

        factors = []

        # 1. 风速评估
        wind_speed = current_data.get("wind_speed", 0) or 0
        wind_status = "go"
        if wind_speed >= WIND_SPEED_LIMIT:
            wind_status = "no_go"
        elif wind_speed >= WIND_SPEED_CAUTION:
            wind_status = "caution"
        factors.append({
            "name": "wind",
            "name_zh": "风速",
            "status": wind_status,
            "value": wind_speed,
            "threshold": WIND_SPEED_LIMIT,
            "unit": "km/h",
            "detail": f"当前风速 {wind_speed} km/h",
        })

        # 2. 雷暴评估
        weather_code = current_data.get("weather_code") or today.get("weather_code")
        lightning_status = "go"
        if weather_code in LIGHTNING_RISK_CODES:
            lightning_status = "no_go"
        factors.append({
            "name": "lightning",
            "name_zh": "雷暴",
            "status": lightning_status,
            "value": weather_code,
            "threshold": None,
            "detail": "存在雷暴风险" if lightning_status == "no_go" else "无雷暴风险",
        })

        # 3. 热应力评估
        temp = current_data.get("feels_like") or current_data.get("temperature", 0) or 0
        heat_status = "go"
        if temp >= HEAT_STRESS_LIMIT:
            heat_status = "no_go"
        elif temp >= HEAT_STRESS_CAUTION:
            heat_status = "caution"
        factors.append({
            "name": "heat_stress",
            "name_zh": "热应力",
            "status": heat_status,
            "value": temp,
            "threshold": HEAT_STRESS_LIMIT,
            "unit": "°C",
            "detail": f"体感温度 {temp}°C",
        })

        # 4. 降水评估
        precipitation = today.get("precipitation", 0) or 0
        precip_status = "go"
        if precipitation >= RAINFALL_LIMIT:
            precip_status = "no_go"
        elif precipitation >= RAINFALL_CAUTION:
            precip_status = "caution"
        factors.append({
            "name": "rainfall",
            "name_zh": "降水",
            "status": precip_status,
            "value": precipitation,
            "threshold": RAINFALL_LIMIT,
            "unit": "mm",
            "detail": f"预计降水 {precipitation} mm",
        })

        # 综合决策 — 取最严格值
        status_order = {"go": 0, "caution": 1, "no_go": 2}
        worst = max(factors, key=lambda f: status_order.get(f["status"], 0))
        overall = worst["status"]

        lang = language if language in DESCRIPTIONS.get(overall, {}) else "en"
        description = DESCRIPTIONS.get(overall, {}).get(lang, DESCRIPTIONS[overall]["en"])

        logger.info(
            "construction_safety_assessed",
            latitude=latitude,
            longitude=longitude,
            overall=overall,
        )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "overall_decision": overall,
            "overall_decision_zh": {"go": "可以施工", "caution": "注意施工", "no_go": "建议停工"}[overall],
            "factors": factors,
            "description": description,
            "language": language,
        }
