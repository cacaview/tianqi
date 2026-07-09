"""
空气质量数据服务 — 封装 Open-Meteo Air Quality API
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


class AirQualityService:
    """空气质量数据服务"""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取复用的 httpx 客户端"""
        if self._client is None or self._client.is_closed:
            settings = get_settings()
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.OPEN_METEO_AQ_TIMEOUT),
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
    async def get_current(self, latitude: float, longitude: float) -> dict:
        """获取当前空气质量（Open-Meteo Air Quality API）"""
        settings = get_settings()
        url = f"{settings.OPEN_METEO_AQ_BASE_URL}/air-quality"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(
                [
                    "pm10",
                    "pm2_5",
                    "carbon_monoxide",
                    "nitrogen_dioxide",
                    "sulphur_dioxide",
                    "ozone",
                    "us_aqi",
                    "european_aqi",
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
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data.get("timezone"),
            "current": {
                "pm10": current.get("pm10"),
                "pm2_5": current.get("pm2_5"),
                "co": current.get("carbon_monoxide"),
                "no2": current.get("nitrogen_dioxide"),
                "so2": current.get("sulphur_dioxide"),
                "o3": current.get("ozone"),
                "us_aqi": current.get("us_aqi"),
                "european_aqi": current.get("european_aqi"),
            },
        }

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def get_forecast(self, latitude: float, longitude: float, days: int = 3) -> dict:
        """获取空气质量预报（Open-Meteo Air Quality API）"""
        settings = get_settings()
        url = f"{settings.OPEN_METEO_AQ_BASE_URL}/air-quality"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ",".join(
                [
                    "pm10",
                    "pm2_5",
                    "carbon_monoxide",
                    "nitrogen_dioxide",
                    "sulphur_dioxide",
                    "ozone",
                    "us_aqi",
                ]
            ),
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
                    "pm10": daily["pm10"][i],
                    "pm2_5": daily["pm2_5"][i],
                    "o3": daily["ozone"][i],
                    "us_aqi": daily["us_aqi"][i],
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
    async def get_hourly_forecast(self, latitude: float, longitude: float, hours: int = 24) -> dict:
        """获取逐小时空气质量预报 — PM2.5/PM10/CO/NO2/SO2/O3"""
        settings = get_settings()
        url = f"{settings.OPEN_METEO_AQ_BASE_URL}/air-quality"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(
                [
                    "pm2_5",
                    "pm10",
                    "carbon_monoxide",
                    "nitrogen_dioxide",
                    "sulphur_dioxide",
                    "ozone",
                    "us_aqi",
                ]
            ),
            "timezone": "auto",
            "forecast_hours": hours,
        }

        client = await self._get_client()
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        forecast = []
        for i in range(min(len(times), hours)):
            forecast.append(
                {
                    "time": times[i],
                    "pm2_5": hourly.get("pm2_5", [None])[i],
                    "pm10": hourly.get("pm10", [None])[i],
                    "co": hourly.get("carbon_monoxide", [None])[i],
                    "no2": hourly.get("nitrogen_dioxide", [None])[i],
                    "so2": hourly.get("sulphur_dioxide", [None])[i],
                    "o3": hourly.get("ozone", [None])[i],
                    "us_aqi": hourly.get("us_aqi", [None])[i],
                }
            )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data.get("timezone"),
            "hourly": forecast,
        }
