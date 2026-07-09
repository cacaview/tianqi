"""
海事气象决策引擎
为航运/渔船/海洋旅游提供航线级气象风险评估
"""

from __future__ import annotations

import structlog

from app.services.marine_service import MarineService
from app.services.weather_service import WeatherService

logger = structlog.get_logger("services.marine_decision")

# 海况阈值
WAVE_HEIGHT_NO_GO: float = 2.5  # m
WAVE_HEIGHT_CAUTION: float = 1.5  # m
WIND_SPEED_NO_GO: float = 50.0  # km/h
WIND_SPEED_CAUTION: float = 30.0  # km/h


class MarineDecisionService:
    """海事气象决策引擎"""

    def __init__(self) -> None:
        self._marine_service = MarineService()
        self._weather_service = WeatherService()

    async def assess_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        language: str = "zh",
    ) -> dict:
        """评估航线风险 — 沿途检查点海洋条件"""
        # 获取起终点的海洋数据
        origin_marine = await self._marine_service.get_marine_current(origin_lat, origin_lon)
        dest_marine = await self._marine_service.get_marine_current(dest_lat, dest_lon)

        # 获取航线中点的海洋数据（简化：取3个检查点）
        mid_lat = (origin_lat + dest_lat) / 2
        mid_lon = (origin_lon + dest_lon) / 2
        mid_marine = await self._marine_service.get_marine_current(mid_lat, mid_lon)

        checkpoints = []
        worst_decision = "go"

        for name, data in [("origin", origin_marine), ("midpoint", mid_marine), ("destination", dest_marine)]:
            wave = data.get("wave_height", 0) or 0
            wind = data.get("wind_wave_height", 0) or 0

            decision = "go"
            if wave >= WAVE_HEIGHT_NO_GO or wind >= WIND_SPEED_NO_GO:
                decision = "no_go"
            elif wave >= WAVE_HEIGHT_CAUTION or wind >= WIND_SPEED_CAUTION:
                decision = "caution"

            checkpoints.append({
                "name": name,
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "wave_height": wave,
                "decision": decision,
            })

            if decision == "no_go" or (decision == "caution" and worst_decision == "go"):
                worst_decision = decision

        logger.info(
            "route_assessed",
            origin=f"{origin_lat},{origin_lon}",
            dest=f"{dest_lat},{dest_lon}",
            decision=worst_decision,
        )

        return {
            "overall_decision": worst_decision,
            "origin": {"latitude": origin_lat, "longitude": origin_lon},
            "destination": {"latitude": dest_lat, "longitude": dest_lon},
            "checkpoints": checkpoints,
            "language": language,
        }

    async def get_current_condition(self, latitude: float, longitude: float) -> dict:
        """获取当前位置海况"""
        marine = await self._marine_service.get_marine_current(latitude, longitude)
        return marine
