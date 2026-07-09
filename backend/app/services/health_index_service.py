"""
城市天气健康指数服务
综合温度舒适度、空气质量、紫外线、降水概率计算0-100健康评分
"""

from __future__ import annotations

import structlog

from app.services.air_quality_service import AirQualityService
from app.services.weather_service import WeatherService

logger = structlog.get_logger("services.health_index")

# 评分权重
WEIGHT_TEMPERATURE: float = 0.30
WEIGHT_AQI: float = 0.30
WEIGHT_UV: float = 0.20
WEIGHT_PRECIPITATION: float = 0.20

# 健康等级阈值
LEVEL_THRESHOLDS: list[tuple[float, str, str]] = [
    (80, "excellent", "优秀"),
    (60, "good", "良好"),
    (40, "moderate", "一般"),
    (20, "poor", "较差"),
    (0, "very_poor", "很差"),
]

# 多语言建议模板
RECOMMENDATIONS: dict[str, dict[str, str]] = {
    "excellent": {
        "zh": "天气条件极佳，适合户外活动",
        "en": "Excellent weather conditions, perfect for outdoor activities",
        "vi": "Điều kiện thời tiết tuyệt vời, phù hợp cho hoạt động ngoài trời",
        "th": "สภาพอากาศดีเยี่ยม เหมาะสำหรับกิจกรรมกลางแจ้ง",
        "id": "Kondisi cuaca sangat baik, cocok untuk aktivitas luar ruangan",
    },
    "good": {
        "zh": "天气条件良好，适宜外出",
        "en": "Good weather, suitable for going out",
        "vi": "Thời tiết tốt, thích hợp để ra ngoài",
        "th": "สภาพอากาศดี เหมาะสำหรับการออกนอกบ้าน",
        "id": "Cuaca bagus, cocok untuk beraktivitas",
    },
    "moderate": {
        "zh": "天气条件一般，建议适当防护",
        "en": "Moderate conditions, some protection recommended",
        "vi": "Điều kiện trung bình, nên có biện pháp bảo vệ",
        "th": "สภาพอากาศปานกลาง ควรป้องกันตัวบ้าง",
        "id": "Kondisi sedang, disarankan perlindungan",
    },
    "poor": {
        "zh": "天气条件较差，减少户外活动",
        "en": "Poor conditions, minimize outdoor activities",
        "vi": "Điều kiện xấu, hạn chế hoạt động ngoài trời",
        "th": "สภาพอากาศย่ำแย่ ควรลดกิจกรรมกลางแจ้ง",
        "id": "Kondisi buruk, kurangi aktivitas luar ruangan",
    },
    "very_poor": {
        "zh": "天气条件很差，避免外出",
        "en": "Very poor conditions, avoid going out",
        "vi": "Điều kiện rất xấu, tránh ra ngoài",
        "th": "สภาพอากาศแย่มาก หลีกเลี่ยงการออกนอกบ้าน",
        "id": "Kondisi sangat buruk, hindari aktivitas luar",
    },
}


def _score_temperature(temp: float) -> float:
    """温度舒适度评分 — 22°C为最佳，偏离越远分越低"""
    if temp is None:
        return 50.0
    deviation = abs(temp - 22.0)
    return max(0, 100 - deviation * 4)


def _score_aqi(aqi: float) -> float:
    """空气质量评分 — AQI越低越好"""
    if aqi is None:
        return 50.0
    if aqi <= 50:
        return 100
    if aqi <= 100:
        return 80
    if aqi <= 150:
        return 50
    if aqi <= 200:
        return 25
    return 0


def _score_uv(weather_code: int | None) -> float:
    """紫外线评分 — 基于天气代码推断"""
    if weather_code is None:
        return 60.0
    # 晴天UV高，阴天/雨天UV低
    if weather_code in (0, 1):
        return 40.0  # 晴天UV较高，分较低（需要防晒）
    if weather_code in (2, 3):
        return 70.0  # 多云适中
    if weather_code in (45, 48, 51, 53, 55):
        return 85.0  # 雾天UV低
    if weather_code in (61, 63, 65, 71, 73, 75, 80, 81, 82, 95, 96, 99):
        return 90.0  # 雨雪天UV很低
    return 60.0


def _score_precipitation(precipitation_prob: float | None) -> float:
    """降水概率评分 — 概率越低越好"""
    if precipitation_prob is None:
        return 60.0
    return max(0, 100 - precipitation_prob)


class HealthIndexService:
    """城市天气健康指数服务"""

    def __init__(self) -> None:
        self._weather_service = WeatherService()
        self._air_quality_service = AirQualityService()

    async def calculate(self, latitude: float, longitude: float, language: str = "zh") -> dict:
        """计算综合健康指数"""
        # 获取天气和空气质量数据
        weather = await self._weather_service.get_current_weather(latitude, longitude)
        aqi_data = await self._air_quality_service.get_current(latitude, longitude)

        current = weather.get("current", {})
        aqi_current = aqi_data.get("current", {})

        # 计算四维度分数
        temp_score = _score_temperature(current.get("temperature"))
        aqi_score = _score_aqi(aqi_current.get("us_aqi"))
        uv_score = _score_uv(current.get("weather_code"))
        precip_score = _score_precipitation(current.get("precipitation_probability"))

        # 加权总分
        total_score = (
            temp_score * WEIGHT_TEMPERATURE
            + aqi_score * WEIGHT_AQI
            + uv_score * WEIGHT_UV
            + precip_score * WEIGHT_PRECIPITATION
        )
        total_score = round(total_score, 1)

        # 确定等级
        level = "very_poor"
        level_zh = "很差"
        for threshold, lvl, lvl_zh in LEVEL_THRESHOLDS:
            if total_score >= threshold:
                level = lvl
                level_zh = lvl_zh
                break

        # 多语言建议
        lang = language if language in RECOMMENDATIONS.get(level, {}) else "en"
        recommendation = RECOMMENDATIONS.get(level, {}).get(lang, RECOMMENDATIONS[level]["en"])

        components = [
            {
                "name": "temperature_comfort",
                "name_zh": "温度舒适度",
                "score": round(temp_score, 1),
                "weight": WEIGHT_TEMPERATURE,
                "description": f"当前温度 {current.get('temperature', '--')}°C",
            },
            {
                "name": "air_quality",
                "name_zh": "空气质量",
                "score": round(aqi_score, 1),
                "weight": WEIGHT_AQI,
                "description": f"AQI {aqi_current.get('us_aqi', '--')}",
            },
            {
                "name": "uv_index",
                "name_zh": "紫外线",
                "score": round(uv_score, 1),
                "weight": WEIGHT_UV,
                "description": f"天气代码 {current.get('weather_code', '--')}",
            },
            {
                "name": "precipitation",
                "name_zh": "降水概率",
                "score": round(precip_score, 1),
                "weight": WEIGHT_PRECIPITATION,
                "description": f"降水概率 {current.get('precipitation_probability', '--')}%",
            },
        ]

        logger.info(
            "health_index_calculated",
            latitude=latitude,
            longitude=longitude,
            score=total_score,
            level=level,
        )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "score": total_score,
            "level": level,
            "level_zh": level_zh,
            "components": components,
            "recommendation": recommendation,
            "language": language,
        }
