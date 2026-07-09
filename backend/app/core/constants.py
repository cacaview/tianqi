"""
常量定义 — 消除魔法数字和硬编码字符串
"""

from __future__ import annotations

# ── HTTP 外部调用超时（秒） ──
HTTP_TIMEOUT_OPEN_METEO: float = 10.0
HTTP_TIMEOUT_QWEATHER: float = 15.0
HTTP_TIMEOUT_NHC: float = 15.0
HTTP_TIMEOUT_WOLFX: float = 15.0
HTTP_TIMEOUT_AQ: float = 10.0
HTTP_TIMEOUT_MARINE: float = 10.0
HTTP_TIMEOUT_FLOOD: float = 10.0
HTTP_TIMEOUT_HISTORICAL: float = 15.0

# ── 缓存 TTL（秒） ──
CACHE_TTL_ALERTS: int = 900  # 15 分钟
CACHE_TTL_TYPHOONS: int = 1800  # 30 分钟
CACHE_TTL_EARTHQUAKE: int = 300  # 5 分钟（地震数据时效性强）
CACHE_TTL_AQ: int = 1800  # 30 分钟

# ── 业务限制 ──
MAX_ALERTS_RETURNED: int = 20
MAX_CHAT_MESSAGE_LENGTH: int = 2000
MAX_FORECAST_DAYS: int = 16

# ── 台风强度等级 ──
TYPHOON_INTENSITY_CODES: dict[str, str] = {
    "Low": "TD",  # 热带低压
    "Depression": "TD",
    "Storm": "TS",  # 热带风暴
    "Typhoon": "TY",  # 台风
    "Super Typhoon": "STY",  # 超强台风
}

# ── 灾害预警等级 ──
ALERT_LEVEL_ORDER: dict[str, int] = {
    "red": 4,
    "orange": 3,
    "yellow": 2,
    "blue": 1,
}

# ── 天气编码描述（WMO 天气编码） ──
WMO_WEATHER_CODES: dict[int, str] = {
    0: "晴",
    1: "大部晴朗",
    2: "局部多云",
    3: "多云",
    45: "雾",
    48: "沉积雾凇",
    51: "小毛毛雨",
    53: "中毛毛雨",
    55: "大毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    80: "小阵雨",
    81: "中阵雨",
    82: "大阵雨",
    95: "雷暴",
    96: "雷暴伴小冰雹",
    99: "雷暴伴大冰雹",
}

# ── 允许的语言代码 ──
VALID_LANGUAGE_CODES: set[str] = {"zh", "en", "vi", "th", "id", "my", "lo"}

# ── 数据库 ──
DB_POOL_SIZE: int = 20
DB_MAX_OVERFLOW: int = 10
