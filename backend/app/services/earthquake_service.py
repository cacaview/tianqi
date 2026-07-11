"""
地震预警服务 — 封装 Wolfx 防灾 API
"""

from __future__ import annotations

from datetime import datetime

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings

logger = structlog.get_logger("services.earthquake")

# Wolfx API 地震信息列表端点 (per official docs v20260512)
_SOURCE_ENDPOINTS: dict[str, str] = {
    "cenc": "cenc_eqlist.json",  # 中国地震台网
    "jma": "jma_eqlist.json",  # 日本気象庁
}

# Wolfx API 地震预警端点
_EEW_ENDPOINTS: dict[str, str] = {
    "cenc": "cenc_eew.json",  # 中国地震台网
    "jma": "jma_eew.json",  # 日本気象庁
    "sc": "sc_eew.json",  # 四川省地震局
    "fj": "fj_eew.json",  # 福建省地震局
    "cq": "cq_eew.json",  # 重庆市地震局
}


class EarthquakeService:
    """地震预警服务 — 封装 Wolfx 防灾 API"""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._cache: dict | None = None
        self._cache_time: datetime | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取复用的 httpx 客户端"""
        if self._client is None or self._client.is_closed:
            settings = get_settings()
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(getattr(settings, "WOLFX_TIMEOUT", 15.0)),
            )
        return self._client

    async def close(self) -> None:
        """关闭 HTTP 客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _is_cache_valid(self, ttl_seconds: int = 300) -> bool:
        """检查缓存是否在 TTL 内"""
        if self._cache is None or self._cache_time is None:
            return False
        return (datetime.now() - self._cache_time).total_seconds() < ttl_seconds

    # ------------------------------------------------------------------
    #  内部: 从 Wolfx 响应中提取 No1..No50 条目列表
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_no_entries(data: dict) -> list[dict]:
        """将 Wolfx 响应中 No1, No2, … 键值提取为列表"""
        entries: list[dict] = []
        for key in sorted(data.keys()):
            if key.startswith("No") and isinstance(data[key], dict):
                entries.append(data[key])
        return entries

    # ------------------------------------------------------------------
    #  地震信息列表
    # ------------------------------------------------------------------

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    async def get_earthquakes(self, source: str = "cenc") -> dict:
        """获取地震列表 — 别名方法，支持 usgs 等来源映射"""
        source_map = {"usgs": "cenc", "cenc": "cenc", "jma": "jma"}
        mapped_source = source_map.get(source.lower(), "cenc")
        return await self.get_recent_earthquakes(mapped_source)

    async def get_recent_earthquakes(self, source: str = "cenc") -> dict:
        """
        获取近期地震列表。

        Wolfx API 端点 (正确):
          - CENC: https://api.wolfx.jp/cenc_eqlist.json
          - JMA:  https://api.wolfx.jp/jma_eqlist.json
        source: cenc(中国地震台网) / jma(日本气象厅)
        """
        settings = get_settings()
        base_url = getattr(settings, "WOLFX_BASE_URL", "https://api.wolfx.jp")

        endpoint = _SOURCE_ENDPOINTS.get(source.lower())
        if not endpoint:
            logger.warning("unknown_earthquake_source", source=source)
            endpoint = _SOURCE_ENDPOINTS["cenc"]

        url = f"{base_url}/{endpoint}"
        client = await self._get_client()

        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.NetworkError) as exc:
            logger.warning("wolfx_api_failed", source=source, error=str(exc))
            # 返回模拟数据兜底
            return self._get_mock_earthquakes(source)

        raw_entries = self._extract_no_entries(data)
        earthquakes: list[dict] = []

        for item in raw_entries:
            earthquakes.append(self._normalize_earthquake(item, source))

        return {
            "earthquakes": earthquakes,
            "total": len(earthquakes),
            "update_time": data.get("time", datetime.now().isoformat()),
            "source": source,
            "is_mock": False,
        }

    # ------------------------------------------------------------------
    #  地震预警 (EEW)
    # ------------------------------------------------------------------

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    async def get_eew_alerts(self, source: str = "cenc") -> list[dict]:
        """
        获取地震预警 (EEW) 列表。

        Wolfx API 端点 (正确):
          - CENC: https://api.wolfx.jp/cenc_eew.json
          - JMA:  https://api.wolfx.jp/jma_eew.json
        source: cenc / jma / sc / fj / cq
        """
        settings = get_settings()
        base_url = getattr(settings, "WOLFX_BASE_URL", "https://api.wolfx.jp")

        endpoint = _EEW_ENDPOINTS.get(source.lower())
        if not endpoint:
            logger.warning("unknown_eew_source", source=source)
            endpoint = _EEW_ENDPOINTS["cenc"]

        url = f"{base_url}/{endpoint}"
        client = await self._get_client()

        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.NetworkError) as exc:
            logger.warning("wolfx_eew_api_failed", source=source, error=str(exc))
            return []

        # EEW 数据可能是单条 dict (无 No 键) 或列表
        raw_entries: list[dict] = []
        if isinstance(data, dict):
            if "EventID" in data:
                raw_entries.append(data)
            else:
                raw_entries = self._extract_no_entries(data)

        alerts: list[dict] = []
        for item in raw_entries:
            alerts.append(
                {
                    "id": str(item.get("ID", item.get("EventID", ""))),
                    "event_id": item.get("EventID", ""),
                    "source": source,
                    "hypocenter": item.get("Hypocenter", item.get("HypoCenter", "")),
                    "magnitude": float(item.get("Magnitude", item.get("Magunitude", 0)) or 0),
                    "expected_max_intensity": item.get("MaxIntensity"),
                    "latitude": float(item.get("Latitude", 0) or 0),
                    "longitude": float(item.get("Longitude", 0) or 0),
                    "depth_km": item.get("Depth"),
                    "alert_time": item.get("ReportTime", item.get("AnnouncedTime", "")),
                    "origin_time": item.get("OriginTime", ""),
                    "is_cancelled": bool(item.get("isCancel", item.get("is_cancelled", False))),
                }
            )

        return alerts

    # ------------------------------------------------------------------
    #  格式化工具
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_earthquake(item: dict, source: str = "cenc") -> dict:
        """将不同来源的地震条目归一化为统一格式"""
        if source.lower() == "jma":
            return {
                "id": str(item.get("EventID", "")),
                "source": source,
                "type": item.get("Title", ""),
                "hypocenter": item.get("location", ""),
                "magnitude": float(item.get("magnitude", 0) or 0),
                "max_intensity": item.get("shindo"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "depth_km": item.get("depth", "").replace("km", ""),
                "occurred_at": item.get("time", ""),
                "info": item.get("info", ""),
                "url": None,
            }
        # CENC / default
        return {
            "id": str(item.get("EventID", "")),
            "source": source,
            "type": item.get("type", ""),
            "hypocenter": item.get("location", item.get("placeName", "")),
            "magnitude": float(item.get("magnitude", 0) or 0),
            "max_intensity": item.get("intensity"),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "depth_km": item.get("depth"),
            "occurred_at": item.get("time", ""),
            "report_time": item.get("ReportTime", ""),
            "url": None,
        }

    # ------------------------------------------------------------------
    #  模拟数据兜底
    # ------------------------------------------------------------------

    def _get_mock_earthquakes(self, source: str = "cenc") -> dict:
        """
        当 Wolfx API 不可用时返回模拟地震数据。
        数据模拟中国-东盟区域的真实地震分布。
        """
        now = datetime.now()
        mock_earthquakes = [
            {
                "id": "MOCK-001",
                "source": source,
                "type": "reviewed",
                "hypocenter": "四川宜宾市高县",
                "magnitude": 4.2,
                "max_intensity": "5",
                "latitude": "28.52",
                "longitude": "104.68",
                "depth_km": "8",
                "occurred_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "report_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "url": None,
                "_is_mock": True,
            },
            {
                "id": "MOCK-002",
                "source": source,
                "type": "reviewed",
                "hypocenter": "云南大理州宾川县",
                "magnitude": 3.5,
                "max_intensity": "5",
                "latitude": "25.94",
                "longitude": "100.57",
                "depth_km": "10",
                "occurred_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "report_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "url": None,
                "_is_mock": True,
            },
            {
                "id": "MOCK-003",
                "source": source,
                "type": "reviewed",
                "hypocenter": "印尼苏拉威西岛附近海域",
                "magnitude": 5.1,
                "max_intensity": "6",
                "latitude": "-1.20",
                "longitude": "121.50",
                "depth_km": "35",
                "occurred_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "report_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "url": None,
                "_is_mock": True,
            },
            {
                "id": "MOCK-004",
                "source": source,
                "type": "reviewed",
                "hypocenter": "广西柳州市柳南区",
                "magnitude": 3.1,
                "max_intensity": "4",
                "latitude": "24.41",
                "longitude": "109.25",
                "depth_km": "5",
                "occurred_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "report_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "url": None,
                "_is_mock": True,
            },
            {
                "id": "MOCK-005",
                "source": source,
                "type": "reviewed",
                "hypocenter": "台湾宜兰县海域",
                "magnitude": 4.5,
                "max_intensity": "5",
                "latitude": "24.60",
                "longitude": "122.60",
                "depth_km": "90",
                "occurred_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "report_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "url": None,
                "_is_mock": True,
            },
        ]

        logger.warning("using_mock_earthquake_data", source=source)

        return {
            "earthquakes": mock_earthquakes,
            "total": len(mock_earthquakes),
            "update_time": now.isoformat(),
            "source": source,
            "is_mock": True,
        }
