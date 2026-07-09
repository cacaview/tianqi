"""
历史气象数据服务 — 封装 Open-Meteo Historical Weather API
提供1940年至今的历史气象数据，用于气候基准分析和保险指数计算
"""

from __future__ import annotations

from datetime import date, timedelta

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings


class HistoricalService:
    """历史气象数据服务"""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取复用的 httpx 客户端"""
        if self._client is None or self._client.is_closed:
            settings = get_settings()
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.OPEN_METEO_HISTORICAL_TIMEOUT),
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
    async def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
    ) -> dict:
        """
        获取历史气象数据 — Open-Meteo Historical API
        数据范围：1940年至今
        参数：
            start_date: 开始日期 "YYYY-MM-DD"
            end_date: 结束日期 "YYYY-MM-DD"
        """
        settings = get_settings()
        url = f"{settings.OPEN_METEO_HISTORICAL_BASE_URL}/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ",".join(
                [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "temperature_2m_mean",
                    "precipitation_sum",
                    "wind_speed_10m_max",
                    "weather_code",
                ]
            ),
            "timezone": "auto",
        }

        client = await self._get_client()
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        daily = data.get("daily", {})
        times = daily.get("time", [])
        records = []
        for i in range(len(times)):
            records.append(
                {
                    "date": times[i],
                    "temperature_max": daily.get("temperature_2m_max", [None])[i],
                    "temperature_min": daily.get("temperature_2m_min", [None])[i],
                    "temperature_mean": daily.get("temperature_2m_mean", [None])[i],
                    "precipitation": daily.get("precipitation_sum", [None])[i],
                    "wind_speed_max": daily.get("wind_speed_10m_max", [None])[i],
                    "weather_code": daily.get("weather_code", [None])[i],
                }
            )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data.get("timezone"),
            "start_date": start_date,
            "end_date": end_date,
            "daily": records,
        }

    async def get_climate_baseline(
        self,
        latitude: float,
        longitude: float,
        reference_years: int = 5,
    ) -> dict:
        """
        获取气候基准 — 基于近N年同期数据的统计基准
        用于保险指数计算和异常检测
        """
        today = date.today()
        # 取近N年同月数据
        start = today.replace(year=today.year - reference_years)
        end = today - timedelta(days=1)

        data = await self.get_historical_weather(
            latitude, longitude,
            start.isoformat(), end.isoformat(),
        )

        daily = data.get("daily", [])
        if not daily:
            return {
                "latitude": latitude,
                "longitude": longitude,
                "reference_years": reference_years,
                "baseline": None,
            }

        # 计算统计基准
        temps_max = [d["temperature_max"] for d in daily if d.get("temperature_max") is not None]
        temps_min = [d["temperature_min"] for d in daily if d.get("temperature_min") is not None]
        precipitations = [d["precipitation"] for d in daily if d.get("precipitation") is not None]
        wind_speeds = [d["wind_speed_max"] for d in daily if d.get("wind_speed_max") is not None]

        def _stats(values: list[float]) -> dict:
            if not values:
                return {"mean": None, "std": None, "min": None, "max": None}
            n = len(values)
            mean = sum(values) / n
            variance = sum((x - mean) ** 2 for x in values) / n if n > 1 else 0
            return {
                "mean": round(mean, 2),
                "std": round(variance**0.5, 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
            }

        return {
            "latitude": latitude,
            "longitude": longitude,
            "reference_years": reference_years,
            "data_points": len(daily),
            "baseline": {
                "temperature_max": _stats(temps_max),
                "temperature_min": _stats(temps_min),
                "precipitation": _stats(precipitations),
                "wind_speed_max": _stats(wind_speeds),
            },
        }
