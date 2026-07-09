"""
跨境烟霾监测服务
整合NASA FIRMS火点数据 + AQICN空气质量
"""

from __future__ import annotations

import httpx
import structlog

from app.core.config import get_settings
from app.services.air_quality_service import AirQualityService

logger = structlog.get_logger("services.haze_monitor")

# 东盟热点区域
FIRE_HOTSPOT_REGIONS: dict[str, dict] = {
    "sumatra": {"lat_min": -6, "lat_max": 6, "lon_min": 95, "lon_max": 106},
    "borneo": {"lat_min": -4, "lat_max": 7, "lon_min": 108, "lon_max": 119},
    "mainland_sea": {"lat_min": 5, "lat_max": 22, "lon_min": 97, "lon_max": 110},
}


class HazeMonitorService:
    """跨境烟霾监测服务"""

    def __init__(self) -> None:
        self._aq_service = AirQualityService()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(15.0))
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_fire_hotspots(self, region: str = "sumatra", days: int = 7) -> dict:
        """获取火点热点数据 — NASA FIRMS API"""
        settings = get_settings()
        api_key = settings.NASA_FIRMS_API_KEY

        if not api_key:
            return {
                "region": region,
                "hotspots": [],
                "message": "NASA FIRMS API key not configured",
                "mock": True,
            }

        region_box = FIRE_HOTSPOT_REGIONS.get(region, FIRE_HOTSPOT_REGIONS["sumatra"])
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/VIIRS_SNPP_NRT/{region_box['lon_min']},{region_box['lat_min']},{region_box['lon_max']},{region_box['lat_max']}/{days}"

        try:
            client = await self._get_client()
            resp = await client.get(url)
            resp.raise_for_status()
            return {
                "region": region,
                "data": resp.text[:2000],  # 限制大小
                "mock": False,
            }
        except Exception as e:
            return {
                "region": region,
                "hotspots": [],
                "message": f"NASA FIRMS request failed: {e}",
                "mock": True,
            }

    async def get_aqi_stations(self, latitude: float, longitude: float) -> dict:
        """获取区域AQI站点数据"""
        data = await self._aq_service.get_current(latitude, longitude)
        return data

    async def get_haze_level(self, latitude: float, longitude: float, language: str = "zh") -> dict:
        """评估烟霾等级 — 综合AQI+天气代码"""
        aqi = await self._aq_service.get_current(latitude, longitude)
        us_aqi = aqi.get("current", {}).get("us_aqi", 0) or 0

        if us_aqi <= 50:
            level = "good"
            level_zh = "优"
        elif us_aqi <= 100:
            level = "moderate"
            level_zh = "良"
        elif us_aqi <= 150:
            level = "unhealthy_sensitive"
            level_zh = "轻度污染"
        elif us_aqi <= 200:
            level = "unhealthy"
            level_zh = "中度污染"
        elif us_aqi <= 300:
            level = "very_unhealthy"
            level_zh = "重度污染"
        else:
            level = "hazardous"
            level_zh = "严重污染"

        return {
            "latitude": latitude,
            "longitude": longitude,
            "us_aqi": us_aqi,
            "haze_level": level,
            "haze_level_zh": level_zh,
            "language": language,
        }
