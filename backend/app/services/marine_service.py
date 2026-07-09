"""
海洋气象数据服务 — 封装 Open-Meteo Marine Weather API
提供浪高、浪向、海流、海面温度等海洋气象数据
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


class MarineService:
    """海洋气象数据服务"""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取复用的 httpx 客户端"""
        if self._client is None or self._client.is_closed:
            settings = get_settings()
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.OPEN_METEO_MARINE_TIMEOUT),
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
    async def get_marine_forecast(self, latitude: float, longitude: float, days: int = 7) -> dict:
        """获取海洋气象预报 — 浪高/浪向/浪周期/海流/海面温度"""
        settings = get_settings()
        url = f"{settings.OPEN_METEO_MARINE_BASE_URL}/marine"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ",".join(
                [
                    "wave_height_max",
                    "wave_direction_dominant",
                    "wave_period_max",
                    "wind_wave_height_max",
                    "swell_wave_height_max",
                ]
            ),
            "current": ",".join(
                [
                    "wave_height",
                    "wave_direction",
                    "wave_period",
                    "wind_wave_height",
                ]
            ),
            "timezone": "auto",
            "forecast_days": min(days, 16),
        }

        client = await self._get_client()
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        # 当前海洋状态
        current = data.get("current", {})
        current_data = {
            "wave_height": current.get("wave_height"),
            "wave_direction": current.get("wave_direction"),
            "wave_period": current.get("wave_period"),
            "wind_wave_height": current.get("wind_wave_height"),
        }

        # 每日预报
        daily = data.get("daily", {})
        daily_forecast = []
        times = daily.get("time", [])
        for i in range(len(times)):
            daily_forecast.append(
                {
                    "date": times[i],
                    "wave_height_max": daily.get("wave_height_max", [None])[i],
                    "wave_direction_dominant": daily.get("wave_direction_dominant", [None])[i],
                    "wave_period_max": daily.get("wave_period_max", [None])[i],
                    "wind_wave_height_max": daily.get("wind_wave_height_max", [None])[i],
                    "swell_wave_height_max": daily.get("swell_wave_height_max", [None])[i],
                }
            )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data.get("timezone"),
            "current": current_data,
            "daily": daily_forecast,
        }

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def get_marine_current(self, latitude: float, longitude: float) -> dict:
        """获取当前海洋状态（实时数据）"""
        settings = get_settings()
        url = f"{settings.OPEN_METEO_MARINE_BASE_URL}/marine"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(
                [
                    "wave_height",
                    "wave_direction",
                    "wave_period",
                    "wind_wave_height",
                    "wind_wave_direction",
                    "wind_wave_period",
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
            "wave_height": current.get("wave_height"),
            "wave_direction": current.get("wave_direction"),
            "wave_period": current.get("wave_period"),
            "wind_wave_height": current.get("wind_wave_height"),
            "wind_wave_direction": current.get("wind_wave_direction"),
            "wind_wave_period": current.get("wind_wave_period"),
        }
