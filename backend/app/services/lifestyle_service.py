"""生活指数服务 — 基于天气数据生成穿衣、洗车、运动等建议"""

from __future__ import annotations

import structlog

from app.services.weather_service import WeatherService

logger = structlog.get_logger()


class LifestyleService:
    """生活指数服务"""

    # Index definitions for rule-based generation
    INDEX_DEFS = {
        "clothing": {"name_zh": "穿衣", "icon": "shirt"},
        "car_wash": {"name_zh": "洗车", "icon": "car"},
        "exercise": {"name_zh": "运动", "icon": "run"},
        "uv": {"name_zh": "紫外线", "icon": "sun"},
        "umbrella": {"name_zh": "带伞", "icon": "umbrella"},
        "tourism": {"name_zh": "旅游", "icon": "map"},
    }

    def __init__(self) -> None:
        self._weather_service = WeatherService()

    async def get_lifestyle_indices(self, latitude: float, longitude: float, language: str = "zh") -> dict:
        """获取生活指数"""
        # Fetch weather data
        weather = await self._weather_service.get_current_weather(latitude, longitude)

        # Generate indices via rules (LLM path can be added later)
        indices = self._get_rule_based_indices(weather, language)

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": weather.get("timezone"),
            "language": language,
            "indices": indices,
            "generated_by": "rules",
        }

    def _get_rule_based_indices(self, weather: dict, language: str) -> list[dict]:
        """规则引擎生成生活指数"""
        temp = weather.get("temperature") or 25
        humidity = weather.get("humidity") or 50
        precipitation = weather.get("precipitation") or 0
        wind_speed = weather.get("wind_speed") or 0
        weather_code = weather.get("weather_code") or 0

        indices = []

        # Clothing
        indices.append(self._clothing_index(temp, wind_speed, precipitation))
        # Car wash
        indices.append(self._car_wash_index(precipitation, weather_code))
        # Exercise
        indices.append(self._exercise_index(temp, precipitation, humidity))
        # UV
        indices.append(self._uv_index(weather_code))
        # Umbrella
        indices.append(self._umbrella_index(precipitation, weather_code))
        # Tourism
        indices.append(self._tourism_index(temp, precipitation, wind_speed))

        return indices

    def _clothing_index(self, temp, wind, precip):
        if temp >= 35:
            level, level_zh, desc = "very_hot", "极热", "气温超过35°C，建议穿最轻薄的短袖短裤，注意防暑。"
        elif temp >= 28:
            level, level_zh, desc = "light", "轻薄", "气温较高，建议穿短袖、短裤等轻薄透气衣物。"
        elif temp >= 20:
            level, level_zh, desc = "comfortable", "舒适", "气温适宜，建议穿长袖或薄外套。"
        elif temp >= 10:
            level, level_zh, desc = "warm", "保暖", "气温偏低，建议穿毛衣、夹克等保暖衣物。"
        else:
            level, level_zh, desc = "cold", "寒冷", "气温较低，建议穿厚外套、羽绒服等御寒衣物。"
        return {
            "name": "clothing",
            "name_zh": "穿衣",
            "level": level,
            "level_zh": level_zh,
            "description": desc,
            "icon": "shirt",
        }

    def _car_wash_index(self, precip, weather_code):
        if precip > 1 or weather_code >= 61:
            level, level_zh, desc = "not_recommended", "不宜", "当前有降水，不建议洗车。"
        elif weather_code >= 45:
            level, level_zh, desc = "not_recommended", "不宜", "有雾天气，不建议洗车。"
        else:
            level, level_zh, desc = "suitable", "适宜", "天气晴好，适合洗车。"
        return {
            "name": "car_wash",
            "name_zh": "洗车",
            "level": level,
            "level_zh": level_zh,
            "description": desc,
            "icon": "car",
        }

    def _exercise_index(self, temp, precip, humidity):
        if precip > 0 or temp > 38:
            level, level_zh, desc = "not_recommended", "不宜", "有降水或极端高温，不建议户外运动。"
        elif temp >= 15 and temp <= 30:
            level, level_zh, desc = "suitable", "适宜", "天气条件适合户外运动。"
        else:
            level, level_zh, desc = "acceptable", "一般", "天气条件一般，建议适当调整运动强度。"
        return {
            "name": "exercise",
            "name_zh": "运动",
            "level": level,
            "level_zh": level_zh,
            "description": desc,
            "icon": "run",
        }

    def _uv_index(self, weather_code):
        if weather_code <= 2:
            level, level_zh, desc = "high", "强", "晴朗天气，紫外线较强，建议涂防晒。"
        elif weather_code <= 3:
            level, level_zh, desc = "moderate", "中等", "多云天气，紫外线中等。"
        else:
            level, level_zh, desc = "low", "弱", "阴天或有降水，紫外线较弱。"
        return {
            "name": "uv",
            "name_zh": "紫外线",
            "level": level,
            "level_zh": level_zh,
            "description": desc,
            "icon": "sun",
        }

    def _umbrella_index(self, precip, weather_code):
        if precip > 0 or weather_code >= 51:
            level, level_zh, desc = "needed", "需要", "有降水或降水概率较高，建议携带雨伞。"
        elif weather_code >= 45:
            level, level_zh, desc = "recommended", "建议", "有雾天气，建议备伞。"
        else:
            level, level_zh, desc = "not_needed", "不需要", "无降水，无需带伞。"
        return {
            "name": "umbrella",
            "name_zh": "带伞",
            "level": level,
            "level_zh": level_zh,
            "description": desc,
            "icon": "umbrella",
        }

    def _tourism_index(self, temp, precip, wind):
        if precip > 1 or wind > 50:
            level, level_zh, desc = "not_recommended", "不宜", "天气条件较差，不建议出游。"
        elif 15 <= temp <= 30 and precip == 0:
            level, level_zh, desc = "suitable", "适宜", "天气晴好，温度适宜，非常适合出游。"
        else:
            level, level_zh, desc = "acceptable", "一般", "天气条件一般，可适当安排户外活动。"
        return {
            "name": "tourism",
            "name_zh": "旅游",
            "level": level,
            "level_zh": level_zh,
            "description": desc,
            "icon": "map",
        }
