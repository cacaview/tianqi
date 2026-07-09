"""
洪水预警数据服务 — 封装 Open-Meteo GloFAS Flood API
提供河流流量模拟数据，92天预报，1940年至今历史数据
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


class FloodService:
    """洪水预警数据服务 — Open-Meteo GloFAS"""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取复用的 httpx 客户端"""
        if self._client is None or self._client.is_closed:
            settings = get_settings()
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.OPEN_METEO_FLOOD_TIMEOUT),
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
    async def get_river_discharge(self, latitude: float, longitude: float) -> dict:
        """
        获取河流流量预报 — GloFAS 系统
        返回：river_discharge, river_discharge_mean, river_discharge_max, river_discharge_min
        预报范围：92天（GloFAS系统）
        """
        settings = get_settings()
        url = f"{settings.OPEN_METEO_FLOOD_BASE_URL}/flood"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ",".join(
                [
                    "river_discharge",
                    "river_discharge_mean",
                    "river_discharge_max",
                    "river_discharge_min",
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
        forecast = []
        for i in range(len(times)):
            forecast.append(
                {
                    "date": times[i],
                    "river_discharge": daily.get("river_discharge", [None])[i],
                    "river_discharge_mean": daily.get("river_discharge_mean", [None])[i],
                    "river_discharge_max": daily.get("river_discharge_max", [None])[i],
                    "river_discharge_min": daily.get("river_discharge_min", [None])[i],
                }
            )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data.get("timezone"),
            "forecast_days": len(times),
            "daily": forecast,
        }

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def get_flood_risk(self, latitude: float, longitude: float) -> dict:
        """
        获取洪水风险评估 — 基于 GloFAS 数据的简化评估
        返回当前风险等级和近期趋势
        """
        discharge_data = await self.get_river_discharge(latitude, longitude)
        daily = discharge_data.get("daily", [])

        if not daily:
            return {
                "latitude": latitude,
                "longitude": longitude,
                "risk_level": "unknown",
                "message": "无法获取河流流量数据",
            }

        # 分析最近7天数据
        recent = daily[:7]
        discharges = [d["river_discharge"] for d in recent if d.get("river_discharge") is not None]

        if not discharges:
            return {
                "latitude": latitude,
                "longitude": longitude,
                "risk_level": "unknown",
                "message": "河流流量数据不足",
            }

        avg_discharge = sum(discharges) / len(discharges)
        max_discharge = max(discharges)
        trend = "rising" if len(discharges) >= 2 and discharges[-1] > discharges[0] else "stable"

        # 简单风险评估（基于相对值）
        if max_discharge > avg_discharge * 2:
            risk_level = "high"
        elif max_discharge > avg_discharge * 1.5:
            risk_level = "moderate"
        else:
            risk_level = "low"

        return {
            "latitude": latitude,
            "longitude": longitude,
            "risk_level": risk_level,
            "avg_discharge_7d": round(avg_discharge, 2),
            "max_discharge_7d": round(max_discharge, 2),
            "trend": trend,
            "forecast_days": discharge_data.get("forecast_days", 0),
        }
