"""
农业气象保险指数服务
基于历史气象数据计算参数化保险触发条件
"""

from __future__ import annotations

import structlog

from app.services.historical_service import HistoricalService

logger = structlog.get_logger("services.insurance_index")


class InsuranceIndexService:
    """农业气象保险指数服务"""

    def __init__(self) -> None:
        self._historical_service = HistoricalService()

    async def calculate_trigger(
        self,
        latitude: float,
        longitude: float,
        crop_type: str = "rice",
        policy_period_days: int = 90,
        language: str = "zh",
    ) -> dict:
        """计算参数化保险触发条件 — 基于历史同期数据"""
        baseline = await self._historical_service.get_climate_baseline(latitude, longitude, reference_years=5)
        baseline_data = baseline.get("baseline", {})

        precip_stats = baseline_data.get("precipitation", {})
        temp_stats = baseline_data.get("temperature_max", {})

        # 触发条件（基于标准差）
        precip_mean = precip_stats.get("mean", 0) or 0
        precip_std = precip_stats.get("std", 0) or 0
        temp_mean = temp_stats.get("mean", 0) or 0
        temp_std = temp_stats.get("std", 0) or 0

        triggers = []
        # 干旱触发：降水量低于均值2个标准差
        if precip_std > 0:
            triggers.append(
                {
                    "type": "drought",
                    "type_zh": "干旱",
                    "threshold": round(precip_mean - 2 * precip_std, 2),
                    "metric": "precipitation_sum",
                    "operator": "lt",
                    "description": f"降水量低于 {round(precip_mean - 2 * precip_std, 2)}mm",
                }
            )

        # 洪涝触发
        if precip_std > 0:
            triggers.append(
                {
                    "type": "flood",
                    "type_zh": "洪涝",
                    "threshold": round(precip_mean + 2 * precip_std, 2),
                    "metric": "precipitation_sum",
                    "operator": "gt",
                    "description": f"降水量高于 {round(precip_mean + 2 * precip_std, 2)}mm",
                }
            )

        # 热害触发
        if temp_std > 0:
            triggers.append(
                {
                    "type": "heat_stress",
                    "type_zh": "热害",
                    "threshold": round(temp_mean + 2 * temp_std, 2),
                    "metric": "temperature_max",
                    "operator": "gt",
                    "description": f"最高温度高于 {round(temp_mean + 2 * temp_std, 2)}°C",
                }
            )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "crop_type": crop_type,
            "policy_period_days": policy_period_days,
            "triggers": triggers,
            "baseline": baseline_data,
            "language": language,
        }

    async def historical_risk_profile(
        self,
        latitude: float,
        longitude: float,
        crop_type: str = "rice",
        language: str = "zh",
    ) -> dict:
        """历史风险画像 — 5年灾害频率统计"""
        baseline = await self._historical_service.get_climate_baseline(latitude, longitude, reference_years=5)

        return {
            "latitude": latitude,
            "longitude": longitude,
            "crop_type": crop_type,
            "risk_profile": baseline,
            "language": language,
        }
