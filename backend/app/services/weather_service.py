"""
气象数据服务 — 封装 Open-Meteo API
添加了：httpx 客户端复用、超时控制、重试机制
"""

from __future__ import annotations

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings


class WeatherService:
    """气象数据服务"""

    # 东盟主要城市坐标
    ASEAN_CITIES: dict[str, dict] = {
        # 中国 - 广西
        "nanning": {"name": "南宁", "name_en": "Nanning", "lat": 22.82, "lon": 108.32, "country": "CN"},
        "guilin": {"name": "桂林", "name_en": "Guilin", "lat": 25.27, "lon": 110.29, "country": "CN"},
        # 越南
        "hanoi": {"name": "河内", "name_en": "Hanoi", "lat": 21.03, "lon": 105.85, "country": "VN"},
        "hcmc": {"name": "胡志明市", "name_en": "Ho Chi Minh City", "lat": 10.82, "lon": 106.63, "country": "VN"},
        # 泰国
        "bangkok": {"name": "曼谷", "name_en": "Bangkok", "lat": 13.76, "lon": 100.50, "country": "TH"},
        "chiangmai": {"name": "清迈", "name_en": "Chiang Mai", "lat": 18.79, "lon": 98.98, "country": "TH"},
        # 印尼
        "jakarta": {"name": "雅加达", "name_en": "Jakarta", "lat": -6.21, "lon": 106.85, "country": "ID"},
        "bali": {"name": "巴厘岛", "name_en": "Bali", "lat": -8.65, "lon": 115.22, "country": "ID"},
        # 菲律宾
        "manila": {"name": "马尼拉", "name_en": "Manila", "lat": 14.60, "lon": 120.98, "country": "PH"},
        # 马来西亚
        "kuala_lumpur": {"name": "吉隆坡", "name_en": "Kuala Lumpur", "lat": 3.14, "lon": 101.69, "country": "MY"},
        # 新加坡
        "singapore": {"name": "新加坡", "name_en": "Singapore", "lat": 1.35, "lon": 103.82, "country": "SG"},
        # 柬埔寨
        "phnom_penh": {"name": "金边", "name_en": "Phnom Penh", "lat": 11.56, "lon": 104.92, "country": "KH"},
        # 老挝
        "vientiane": {"name": "万象", "name_en": "Vientiane", "lat": 17.97, "lon": 102.63, "country": "LA"},
        # 缅甸
        "yangon": {"name": "仰光", "name_en": "Yangon", "lat": 16.87, "lon": 96.20, "country": "MM"},
        # 文莱
        "bandar_seri_begawan": {
            "name": "斯里巴加湾",
            "name_en": "Bandar Seri Begawan",
            "lat": 4.93,
            "lon": 114.95,
            "country": "BN",
        },
    }

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取复用的 httpx 客户端"""
        if self._client is None or self._client.is_closed:
            settings = get_settings()
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.OPEN_METEO_TIMEOUT),
            )
        return self._client

    async def close(self) -> None:
        """关闭 HTTP 客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def get_current_weather(self, latitude: float, longitude: float) -> dict:
        """获取当前天气（Open-Meteo API）"""
        settings = get_settings()
        url = f"{settings.OPEN_METEO_BASE_URL}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_direction_10m",
                ]
            ),
            "timezone": "auto",
        }

        client = await self._get_client()
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current", {})
        return {
            "temperature": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_direction": current.get("wind_direction_10m"),
            "weather_code": current.get("weather_code"),
            "timezone": data.get("timezone"),
            "latitude": latitude,
            "longitude": longitude,
        }

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def get_forecast(self, latitude: float, longitude: float, days: int = 7) -> dict:
        """获取天气预报（Open-Meteo API）"""
        settings = get_settings()
        url = f"{settings.OPEN_METEO_BASE_URL}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ",".join(
                [
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "wind_speed_10m_max",
                ]
            ),
            "hourly": "temperature_2m,precipitation_probability,weather_code",
            "timezone": "auto",
            "forecast_days": days,
        }

        client = await self._get_client()
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        daily = data.get("daily", {})
        forecast_days = []
        for i in range(len(daily.get("time", []))):
            forecast_days.append(
                {
                    "date": daily["time"][i],
                    "weather_code": daily["weather_code"][i],
                    "temp_max": daily["temperature_2m_max"][i],
                    "temp_min": daily["temperature_2m_min"][i],
                    "precipitation": daily["precipitation_sum"][i],
                    "precipitation_probability": daily["precipitation_probability_max"][i],
                    "wind_speed_max": daily["wind_speed_10m_max"][i],
                }
            )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data.get("timezone"),
            "forecast": forecast_days,
        }

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def get_minutely_precipitation(self, latitude: float, longitude: float) -> dict:
        """获取分钟级降水预报（Open-Meteo minutely_15）"""
        settings = get_settings()
        url = f"{settings.OPEN_METEO_BASE_URL}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "minutely_15": "precipitation",
            "timezone": "auto",
        }

        client = await self._get_client()
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        minutely = data.get("minutely_15", {})
        time_list = minutely.get("time", [])
        precip_list = minutely.get("precipitation", [])
        minutely_data = [{"time": t, "precipitation_mm": p} for t, p in zip(time_list, precip_list, strict=False)]

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data.get("timezone"),
            "minutely_15": minutely_data,
        }

    def get_asean_cities(self) -> dict:
        """获取东盟主要城市列表"""
        return self.ASEAN_CITIES
