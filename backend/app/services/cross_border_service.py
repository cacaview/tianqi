"""
跨境灾害协同预警服务
整合多国灾害预警数据，进行关联分析
"""

from __future__ import annotations

import structlog

from app.services.disaster_service import DisasterAlertService
from app.services.earthquake_service import EarthquakeService
from app.services.weather_service import WeatherService

logger = structlog.get_logger("services.cross_border")

# 东盟国家坐标范围
ASEAN_REGIONS: dict[str, dict] = {
    "guangxi": {"lat": 23.5, "lon": 108.3},
    "vietnam": {"lat": 16.0, "lon": 108.0},
    "thailand": {"lat": 13.8, "lon": 100.5},
    "indonesia": {"lat": -6.2, "lon": 106.8},
    "philippines": {"lat": 14.6, "lon": 121.0},
    "myanmar": {"lat": 16.9, "lon": 96.2},
    "malaysia": {"lat": 3.1, "lon": 101.7},
    "singapore": {"lat": 1.4, "lon": 103.8},
    "cambodia": {"lat": 11.6, "lon": 104.9},
    "laos": {"lat": 18.0, "lon": 102.6},
}


class CrossBorderService:
    """跨境灾害协同预警服务"""

    def __init__(self) -> None:
        self._disaster_service = DisasterAlertService()
        self._earthquake_service = EarthquakeService()
        self._weather_service = WeatherService()

    async def correlate_events(self, time_window_hours: int = 48, language: str = "zh") -> dict:
        """关联分析 — 跨国灾害事件关联"""
        # 获取多国预警
        all_alerts = {}
        for region, _coords in list(ASEAN_REGIONS.items())[:5]:  # 限制5个区域避免过多请求
            try:
                alerts = await self._disaster_service.get_alerts(region)
                if alerts.get("alerts"):
                    all_alerts[region] = alerts["alerts"]
            except Exception:
                logger.warning("failed_to_fetch_alerts", region=region)

        # 获取地震信息
        try:
            earthquakes = await self._earthquake_service.get_earthquakes("usgs")
        except Exception:
            earthquakes = {"earthquakes": []}

        # 构建关联分析
        correlations = []
        regions_with_alerts = list(all_alerts.keys())

        if len(regions_with_alerts) >= 2:
            correlations.append(
                {
                    "type": "multi_region_alert",
                    "type_zh": "多国同步预警",
                    "regions": regions_with_alerts,
                    "severity": "moderate",
                    "description": f"{len(regions_with_alerts)}个区域同时存在灾害预警",
                }
            )

        if earthquakes.get("earthquakes"):
            eq = earthquakes["earthquakes"][0] if earthquakes["earthquakes"] else {}
            correlations.append(
                {
                    "type": "earthquake",
                    "type_zh": "地震事件",
                    "magnitude": eq.get("magnitude", 0),
                    "location": eq.get("hypocenter", ""),
                    "severity": "high" if (eq.get("magnitude", 0) or 0) >= 6.0 else "moderate",
                }
            )

        logger.info("cross_border_correlated", regions=len(all_alerts), correlations=len(correlations))

        return {
            "time_window_hours": time_window_hours,
            "regions_with_alerts": regions_with_alerts,
            "total_alerts": sum(len(v) for v in all_alerts.values()),
            "correlations": correlations,
            "earthquake_count": len(earthquakes.get("earthquakes", [])),
            "language": language,
        }

    async def impact_chain(self, disaster_type: str = "typhoon", language: str = "zh") -> dict:
        """灾害影响传播链"""
        chains = {
            "typhoon": [
                {"stage": 1, "event": "台风生成", "impact": "海事预警"},
                {"stage": 2, "event": "台风登陆", "impact": "暴雨+大风"},
                {"stage": 3, "event": "持续降水", "impact": "洪涝灾害"},
                {"stage": 4, "event": "洪水蔓延", "impact": "农业损失+交通中断"},
            ],
            "earthquake": [
                {"stage": 1, "event": "地震发生", "impact": "建筑损坏"},
                {"stage": 2, "event": "余震序列", "impact": "二次破坏风险"},
                {"stage": 3, "event": "海啸预警", "impact": "沿海疏散"},
            ],
            "haze": [
                {"stage": 1, "event": "森林火灾", "impact": "火点扩散"},
                {"stage": 2, "event": "烟雾扩散", "impact": "跨境空气质量恶化"},
                {"stage": 3, "event": "持续烟霾", "impact": "公共卫生危机"},
            ],
        }

        chain = chains.get(disaster_type, chains["typhoon"])

        return {
            "disaster_type": disaster_type,
            "impact_chain": chain,
            "language": language,
        }
