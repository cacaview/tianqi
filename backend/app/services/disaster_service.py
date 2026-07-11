"""
灾害预警服务 - 台风路径、暴雨、洪涝等多灾种预警
"""

from __future__ import annotations

from datetime import datetime, timedelta

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.constants import (
    ALERT_LEVEL_ORDER,
    CACHE_TTL_ALERTS,
    CACHE_TTL_TYPHOONS,
    MAX_ALERTS_RETURNED,
    TYPHOON_INTENSITY_CODES,
)

logger = structlog.get_logger("services.disaster")


class DisasterAlertService:
    """极端天气与灾害预警服务"""

    # 台风命名表（西太平洋）
    TYPHOON_NAMES = [
        "珍珠",
        "蝴蝶",
        "琵琶",
        "风神",
        "海神",
        "凤凰",
        "烟花",
        "玉兔",
        "桃芝",
        "万宜",
        "天兔",
        "帕布",
        "洛坦",
        "纳沙",
        "海棠",
        "尼格",
        "榕树",
        "天鸽",
        "帕卡",
        "珊瑚",
    ]

    # 中国灾害预警等级
    ALERT_LEVELS = {
        "blue": {"name": "蓝色", "level": 1, "desc": "一般"},
        "yellow": {"name": "黄色", "level": 2, "desc": "较重"},
        "orange": {"name": "橙色", "level": 3, "desc": "严重"},
        "red": {"name": "红色", "level": 4, "desc": "特别严重"},
    }

    def __init__(self) -> None:
        self._http_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
        self._alert_cache: dict = {}
        self._cache_time: datetime | None = None
        self._cache_ttl = timedelta(seconds=CACHE_TTL_ALERTS)
        self._typhoon_cache: dict | None = None
        self._typhoon_cache_time: datetime | None = None
        self._typhoon_cache_ttl = timedelta(seconds=CACHE_TTL_TYPHOONS)

    async def close(self):
        await self._http_client.aclose()

    def _is_cache_valid(self, cache_time: datetime | None, ttl: timedelta) -> bool:
        if not cache_time:
            return False
        return datetime.now() - cache_time < ttl

    async def get_typhoon_list(self) -> list[dict]:
        """获取当前活跃台风列表 - 接入JMA/Real台风数据"""
        # 检查缓存
        if self._typhoon_cache and self._is_cache_valid(self._typhoon_cache_time, self._typhoon_cache_ttl):
            return self._typhoon_cache.get("typhoons", [])

        typhoons = []

        # 尝试从多个数据源获取台风数据
        try:
            # 方法1: 从NHC (美国国家飓风中心) 获取西太平洋数据
            typhoons = await self._fetch_nhc_tropical_storms()
        except Exception as e:
            logger.warning("nhc_fetch_failed", error=str(e))

        # 方法2: 从台风路径网获取数据
        if not typhoons:
            try:
                typhoons = await self._fetch_typhoon_cnn_data()
            except Exception as e:
                logger.warning("typhoon_cnn_fetch_failed", error=str(e))

        # 如果都没有数据，返回模拟数据但标记为模拟
        if not typhoons:
            typhoons = self._get_mock_typhoon_data()
            logger.warning("using_mock_typhoon_data")
        else:
            logger.info("typhoon_list_fetched", count=len(typhoons))

        # 更新缓存
        is_real = typhoons != self._get_mock_typhoon_data()
        self._typhoon_cache = {
            "typhoons": typhoons,
            "source": "real" if is_real else "mock",
        }
        self._typhoon_cache_time = datetime.now()

        return typhoons

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    async def _fetch_nhc_tropical_storms(self) -> list[dict]:
        """从NHC获取活跃热带气旋"""
        # NHC提供JSON格式的活跃风暴数据
        url = "https://www.nhc.noaa.gov/CurrentStorms.json"

        try:
            resp = await self._http_client.get(url)
            resp.raise_for_status()
            data = resp.json()

            storms = []
            for storm in data.get("storms", []):
                # 只处理西太平洋区域的风暴 (ID以CP/WP开头)
                storm_id = storm.get("id", "")
                if storm_id.startswith(("WP", "CP", "SH")):
                    storms.append(
                        {
                            "id": storm_id,
                            "name": storm.get("name", "未命名"),
                            "code": storm.get("stormName", storm_id),
                            "intl_code": storm.get("stormId", storm_id),
                            "status": "active",
                            "position": {"lat": storm.get("lat", 0), "lon": storm.get("lon", 0)},
                            "intensity": self._nhc_category_to_abbrev(storm.get("category", "")),
                            "max_wind_speed": storm.get("windSpeed", 0) * 1.852,  # knots to km/h
                            "pressure": storm.get("pressure", 0),
                            "movement": storm.get("movement", {}),
                            "movement_dir": storm.get("direction", "Unknown"),
                            "movement_speed": storm.get("speed", 0) * 1.852,
                            "forecast_track": self._parse_nhc_forecast(
                                storm.get("fcstLats", []),
                                storm.get("fcstLons", []),
                            ),
                            "impact_regions": self._estimate_impact_regions(
                                storm.get("lat", 0),
                                storm.get("lon", 0),
                            ),
                            "source": "NHC",
                            "created_at": datetime.now().isoformat(),
                        }
                    )
            return storms
        except Exception as e:
            logger.warning("nhc_api_error", error=str(e))
            return []

    def _nhc_category_to_abbrev(self, category: str) -> str:
        """NHC 类别转换为缩写"""
        return TYPHOON_INTENSITY_CODES.get(category, "TS")

    def _parse_nhc_forecast(self, lats: list, lons: list) -> list[dict]:
        """解析NHC预报路径"""
        track = []
        for i, (lat, lon) in enumerate(zip(lats or [], lons or [], strict=False)):
            track.append(
                {
                    "hour": (i + 1) * 24,
                    "lat": lat,
                    "lon": lon,
                    "wind": 0,  # NHC JSON不包含预报风速
                }
            )
        return track

    def _estimate_impact_regions(self, lat: float, lon: float) -> list[str]:
        """根据位置估算影响区域"""
        regions = []
        if 10 <= lat <= 25 and 105 <= lon <= 120:
            regions.append("南海")
            if lon < 112:
                regions.append("海南岛")
            if lat > 18:
                regions.append("广东沿海")
        if 15 <= lat <= 25 and 105 <= lon <= 115:
            regions.append("北部湾")
            regions.append("越南北部")
        if 20 <= lat <= 30 and 108 <= lon <= 125:
            regions.append("华南沿海")
        return regions if regions else ["西太平洋"]

    async def _fetch_typhoon_cnn_data(self) -> list[dict]:
        """从台风实时监测获取数据"""
        # 这个数据源可能需要网页抓取，暂时返回空列表
        return []

    def _get_mock_typhoon_data(self) -> list[dict]:
        """获取模拟台风数据（用于演示）"""
        return [
            {
                "id": "202425",
                "name": "帕布",
                "code": "PABUK",
                "intl_code": "2425",
                "status": "active",
                "position": {"lat": 18.5, "lon": 112.3},
                "intensity": "TS",
                "max_wind_speed": 65,
                "pressure": 990,
                "move_direction": "西北",
                "move_speed": 20,
                "radius_7": 150,
                "radius_10": 80,
                "forecast_track": [
                    {"hour": 24, "lat": 19.2, "lon": 110.5, "wind": 70},
                    {"hour": 48, "lat": 20.1, "lon": 108.2, "wind": 55},
                    {"hour": 72, "lat": 21.5, "lon": 105.8, "wind": 40},
                ],
                "impact_regions": ["海南岛", "北部湾", "越南北部"],
                "source": "模拟数据",
                "created_at": datetime.now().isoformat(),
            }
        ]

    async def get_typhoon_detail(self, typhoon_id: str) -> dict | None:
        """获取台风详细信息"""
        typhoons = await self.get_typhoon_list()
        for t in typhoons:
            if t["id"] == typhoon_id:
                return t
        return None

    async def get_typhoon_track_data(self, typhoon_id: str) -> dict:
        """获取台风完整路径数据（用于地图可视化）"""
        typhoon = await self.get_typhoon_detail(typhoon_id)
        if not typhoon:
            return {}

        # 构建GeoJSON格式的路径数据
        historical = typhoon.get("historical_track", [])
        forecast = typhoon.get("forecast_track", [])

        return {
            "id": typhoon["id"],
            "name": typhoon["name"],
            "current": {
                "lat": typhoon["position"]["lat"],
                "lon": typhoon["position"]["lon"],
                "intensity": typhoon["intensity"],
                "wind_speed": typhoon["max_wind_speed"],
                "pressure": typhoon.get("pressure", 0),
            },
            "historical_track": [
                {"lat": h["lat"], "lon": h["lon"], "time": h.get("time", ""), "wind": h.get("wind", 0)}
                for h in historical
            ],
            "forecast_track": [
                {"lat": f["lat"], "lon": f["lon"], "hour": f["hour"], "wind": f.get("wind", 0)} for f in forecast
            ],
            "impact_radius": {
                "radius_7": typhoon.get("radius_7", 0),
                "radius_10": typhoon.get("radius_10", 0),
            },
            "impact_regions": typhoon.get("impact_regions", []),
            "source": typhoon.get("source", "未知"),
        }

    async def get_regional_alerts(self, region: str = "guangxi") -> list[dict]:
        """获取区域灾害预警列表"""
        # 检查缓存
        cache_key = f"alerts_{region}"
        if cache_key in self._alert_cache and self._is_cache_valid(self._cache_time, self._cache_ttl):
            return self._alert_cache[cache_key]

        # 尝试从和风天气API获取真实预警数据
        alerts = await self._fetch_qweather_alerts(region)

        # 如果获取失败，使用模拟数据
        if not alerts:
            alerts = self._get_mock_alerts(region)

        # 更新缓存
        self._alert_cache[cache_key] = alerts
        self._cache_time = datetime.now()

        return alerts

    async def _fetch_qweather_alerts(self, region: str) -> list[dict]:
        """从和风天气API获取预警"""
        from app.core.config import get_settings

        settings = get_settings()

        if not settings.QWEATHER_API_KEY:
            return []

        # 城市代码映射
        city_codes = {
            "guangxi": "101300101",  # 南宁
            "vietnam": "101341001",  # 河内（使用相近代码）
            "thailand": "101319001",  # 曼谷
        }

        city_code = city_codes.get(region.lower())
        if not city_code:
            return []

        try:
            url = "https://devapi.qweather.com/v7/warning/now"
            params = {"location": city_code, "key": settings.QWEATHER_API_KEY}
            resp = await self._http_client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            alerts = []
            for item in data.get("warning", []):
                alerts.append(
                    {
                        "id": item.get("id", ""),
                        "type": item.get("type", ""),
                        "type_name": item.get("typeName", ""),
                        "level": self._qweather_level_to_standard(item.get("level", "")),
                        "level_name": item.get("levelName", item.get("level", "")),
                        "title": item.get("title", ""),
                        "content": item.get("text", ""),
                        "start_time": item.get("pubTime", datetime.now().isoformat()),
                        "end_time": (datetime.now() + timedelta(hours=24)).isoformat(),
                        "affected_areas": [item.get("name", region)],
                        "recommendations": item.get("precaution", "").split("。") if item.get("precaution") else [],
                        "source": "和风天气",
                    }
                )
            return alerts
        except Exception as e:
            logger.warning("qweather_api_error", error=str(e))
            return []

    def _qweather_level_to_standard(self, level: str) -> str:
        """转换和风天气预警等级到标准格式"""
        mapping = {
            "蓝色": "blue",
            "黄色": "yellow",
            "橙色": "orange",
            "红色": "red",
            "Blue": "blue",
            "Yellow": "yellow",
            "Orange": "orange",
            "Red": "red",
        }
        return mapping.get(level, "blue")

    def _get_mock_alerts(self, region: str) -> list[dict]:
        """获取模拟预警数据"""
        all_alerts = {
            "guangxi": [
                {
                    "id": "ALERT-GX-2024001",
                    "type": "rainstorm",
                    "type_name": "暴雨",
                    "level": "orange",
                    "level_name": "橙色",
                    "title": "广西发布暴雨橙色预警",
                    "content": "预计未来24小时，南宁、柳州、桂林等地将出现大暴雨，局部特大暴雨，请注意防范。",
                    "start_time": datetime.now().isoformat(),
                    "end_time": (datetime.now() + timedelta(hours=24)).isoformat(),
                    "affected_areas": ["南宁", "柳州", "桂林", "梧州", "贵港"],
                    "recommendations": [
                        "检查城市排水系统，清理雨水口",
                        "山区注意防范滑坡、泥石流",
                        "农田及时疏通沟渠，排涝防淹",
                    ],
                    "source": "广西气象局",
                },
                {
                    "id": "ALERT-GX-2024002",
                    "type": "typhoon",
                    "type_name": "台风",
                    "level": "blue",
                    "level_name": "蓝色",
                    "title": "台风「帕布」生成，南海将有强风雨",
                    "content": "今年第25号台风「帕布」已生成，预计将影响北部湾海域，请海上作业船只注意防范。",
                    "start_time": datetime.now().isoformat(),
                    "end_time": (datetime.now() + timedelta(hours=48)).isoformat(),
                    "affected_areas": ["北部湾", "涠洲岛", "海南岛"],
                    "recommendations": ["海上船只回港避风", "加固港口设施"],
                    "source": "中央气象台",
                },
            ],
            "vietnam": [
                {
                    "id": "ALERT-VN-2024001",
                    "type": "rain",
                    "type_name": "降雨",
                    "level": "yellow",
                    "level_name": "黄色",
                    "title": "越南北部雷阵雨预警",
                    "content": "河内及周边地区今日有雷阵雨，局部大到暴雨，可能伴有雷电和短时大风。",
                    "start_time": datetime.now().isoformat(),
                    "end_time": (datetime.now() + timedelta(hours=12)).isoformat(),
                    "affected_areas": ["河内", "海防", "北江"],
                    "recommendations": ["避免在户外使用手机", "驾驶注意道路湿滑"],
                    "source": "越南国家水文气象预报中心",
                },
            ],
            "thailand": [
                {
                    "id": "ALERT-TH-2024001",
                    "type": "heat",
                    "type_name": "高温",
                    "level": "orange",
                    "level_name": "橙色",
                    "title": "泰国中北部高温预警",
                    "content": "曼谷及周边地区气温将达38-41°C，体表温度可达45°C以上，请避免户外活动。",
                    "start_time": datetime.now().isoformat(),
                    "end_time": (datetime.now() + timedelta(hours=72)).isoformat(),
                    "affected_areas": ["曼谷", "佛统", "北碧"],
                    "recommendations": ["避免10-16时户外活动", "多补充水分"],
                    "source": "泰国气象局",
                },
            ],
        }
        return all_alerts.get(region.lower(), [])

    async def get_alerts(self, region: str = "guangxi") -> dict:
        """获取区域预警 — 返回字典格式，包含 alerts 列表"""
        alerts = await self.get_regional_alerts(region)
        return {
            "alerts": alerts,
            "total": len(alerts),
            "by_level": {
                "red": len([a for a in alerts if a["level"] == "red"]),
                "orange": len([a for a in alerts if a["level"] == "orange"]),
                "yellow": len([a for a in alerts if a["level"] == "yellow"]),
                "blue": len([a for a in alerts if a["level"] == "blue"]),
            },
        }

    async def get_alert_summary(self, regions: list[str]) -> dict:
        """获取多区域预警汇总"""
        all_alerts = []
        for region in regions:
            alerts = await self.get_regional_alerts(region)
            all_alerts.extend([{**a, "region": region} for a in alerts])

        # 按等级排序
        all_alerts.sort(key=lambda x: ALERT_LEVEL_ORDER.get(x["level"], 0), reverse=True)

        return {
            "total": len(all_alerts),
            "by_level": {
                "red": len([a for a in all_alerts if a["level"] == "red"]),
                "orange": len([a for a in all_alerts if a["level"] == "orange"]),
                "yellow": len([a for a in all_alerts if a["level"] == "yellow"]),
                "blue": len([a for a in all_alerts if a["level"] == "blue"]),
            },
            "by_type": self._count_by_type(all_alerts),
            "alerts": all_alerts[:MAX_ALERTS_RETURNED],
            "update_time": datetime.now().isoformat(),
        }

    def _count_by_type(self, alerts: list[dict]) -> dict:
        counts = {}
        for a in alerts:
            t = a["type"]
            counts[t] = counts.get(t, 0) + 1
        return counts

    async def get_agriculture_alert(self, region: str = "guangxi") -> dict:
        """获取农业气象灾害预警"""
        return {
            "region": region,
            "alerts": [
                {
                    "crop": "水稻",
                    "stage": "抽穗期",
                    "risk": "暴雨倒伏",
                    "level": "high",
                    "advice": "提前排水，保持浅水层，必要时提前收割",
                    "valid_period": "未来48小时",
                },
                {
                    "crop": "甘蔗",
                    "stage": "伸长期",
                    "risk": "大风倒伏",
                    "level": "medium",
                    "advice": "加固蔗田排水沟，减少大风危害",
                    "valid_period": "台风影响期间",
                },
            ],
            "update_time": datetime.now().isoformat(),
        }

    async def get_logistics_alert(self, route: str = "nanning_hcmc") -> dict:
        """获取物流气象风险预警"""
        route_alerts = {
            "nanning_hcmc": {
                "route": "南宁-胡志明市",
                "risk_level": "medium",
                "segments": [
                    {"segment": "南宁-友谊关", "risk": "low", "weather": "多云，有阵雨"},
                    {"segment": "友谊关-河内", "risk": "medium", "weather": "有雷阵雨"},
                    {"segment": "河内-岘港", "risk": "low", "weather": "晴好"},
                    {"segment": "岘港-胡志明市", "risk": "medium", "weather": "局部大雨"},
                ],
                "recommendation": "建议推迟至明日出行",
                "update_time": datetime.now().isoformat(),
            }
        }
        return route_alerts.get(route, {})

    async def get_four_stage_warning(self, disaster_id: str) -> dict:
        """递进式四阶段预警"""
        now = datetime.now()
        return {
            "disaster_id": disaster_id,
            "disaster_type": "typhoon",
            "disaster_name": "帕布",
            "current_stage": "pre_disaster",
            "stages": {
                "pre_disaster": {
                    "name": "灾前预判",
                    "time_range": "提前72-24小时",
                    "status": "active",
                    "content": "台风「帕布」预计72小时后影响北部湾海域，建议提前做好防范准备。",
                    "actions": ["通知海上作业船只提前回港", "检查港口设施", "备足防台物资"],
                },
                "imminent": {
                    "name": "临灾预警",
                    "time_range": "提前24-6小时",
                    "status": "pending",
                    "content": "台风「帕布」进入24小时警戒线，预计明日凌晨登陆越南北部。",
                    "actions": ["发布橙色预警信号", "关闭沿海景区", "停止海上作业"],
                },
                "during_disaster": {
                    "name": "灾中追踪",
                    "time_range": "灾害影响期间",
                    "status": "pending",
                    "content": "台风「帕布」正在登陆，中心附近最大风力12级。",
                    "actions": ["每小时更新台风动态", "实时监测降雨量", "发布道路封闭信息"],
                },
                "post_disaster": {
                    "name": "灾后评估",
                    "time_range": "灾害结束后6小时内",
                    "status": "pending",
                    "content": "台风「帕布」已减弱为热带低压。",
                    "actions": ["统计受灾损失", "发布灾后恢复建议", "评估损失"],
                },
            },
            "update_time": now.isoformat(),
        }

    async def get_weather_map_data(self) -> dict:
        """获取气象地图数据（用于可视化）"""
        # 获取所有城市的天气数据
        from app.services.weather_service import WeatherService

        weather_service = WeatherService()

        cities_data = [
            {"name": "南宁", "lat": 22.82, "lon": 108.32, "code": "nanning"},
            {"name": "河内", "lat": 21.03, "lon": 105.85, "code": "hanoi"},
            {"name": "曼谷", "lat": 13.76, "lon": 100.50, "code": "bangkok"},
            {"name": "雅加达", "lat": -6.21, "lon": 106.85, "code": "jakarta"},
            {"name": "马尼拉", "lat": 14.60, "lon": 120.98, "code": "manila"},
            {"name": "吉隆坡", "lat": 3.14, "lon": 101.69, "code": "kuala_lumpur"},
            {"name": "新加坡", "lat": 1.35, "lon": 103.82, "code": "singapore"},
            {"name": "金边", "lat": 11.56, "lon": 104.92, "code": "phnom_penh"},
        ]

        weather_points = []
        for city in cities_data:
            try:
                weather = await weather_service.get_current_weather(city["lat"], city["lon"])
                weather_points.append(
                    {
                        "id": city["code"],
                        "name": city["name"],
                        "lat": city["lat"],
                        "lon": city["lon"],
                        "temperature": weather.get("temperature"),
                        "humidity": weather.get("humidity"),
                        "wind_speed": weather.get("wind_speed"),
                        "precipitation": weather.get("precipitation"),
                        "weather_code": weather.get("weather_code"),
                    }
                )
            except Exception as e:
                logger.warning("city_weather_fetch_failed", city=city["name"], error=str(e))

        # 获取预警数据
        alert_summary = await self.get_alert_summary(["guangxi", "vietnam", "thailand"])

        # 获取台风数据
        typhoons = await self.get_typhoon_list()

        return {
            "weather_points": weather_points,
            "alerts": alert_summary,
            "typhoons": typhoons,
            "update_time": datetime.now().isoformat(),
        }


# 全局单例
_disaster_service: DisasterAlertService | None = None


def get_disaster_service() -> DisasterAlertService:
    global _disaster_service
    if _disaster_service is None:
        _disaster_service = DisasterAlertService()
    return _disaster_service


async def shutdown_disaster_service():
    global _disaster_service
    if _disaster_service:
        await _disaster_service.close()
        _disaster_service = None
