"""
气象工具链 - 供LangChain Agent调用
Phase 2: 扩展灾害预警和行业决策工具
"""
import asyncio
from typing import List
from langchain_core.tools import tool
from app.services.weather_service import WeatherService
from app.services.disaster_service import get_disaster_service

_weather_service = WeatherService()


@tool
def get_current_weather(latitude: float, longitude: float) -> str:
    """获取指定经纬度的当前天气信息，包括温度、湿度、风速、降水等。经纬度为必填参数。"""
    result = asyncio.run(_weather_service.get_current_weather(latitude, longitude))
    return str(result)


@tool
def get_weather_forecast(latitude: float, longitude: float, days: int = 3) -> str:
    """获取指定经纬度的未来多天天气预报。参数：纬度、经度、预报天数(1-16)。"""
    result = asyncio.run(_weather_service.get_forecast(latitude, longitude, days))
    return str(result)


@tool
def get_city_weather(city_name: str) -> str:
    """根据城市名称获取天气。支持城市：nanning(南宁), hanoi(河内), bangkok(曼谷), jakarta(雅加达), manila(马尼拉), kuala_lumpur(吉隆坡), singapore(新加坡), phnom_penh(金边), vientiane(万象), yangon(仰光)等东盟主要城市。"""
    cities = _weather_service.get_asean_cities()
    city_key = city_name.lower().replace(" ", "_")

    if city_key not in cities:
        available = ", ".join(cities.keys())
        return f"未找到城市 '{city_name}'。可用城市: {available}"

    city = cities[city_key]
    result = asyncio.run(_weather_service.get_current_weather(city["lat"], city["lon"]))
    return f"{city['name']}({city['name_en']}): {result}"


@tool
def get_disaster_alert(region: str = "guangxi") -> str:
    """获取指定区域的极端天气和灾害预警信息。region可选：guangxi(广西), vietnam, thailand, indonesia, philippines, myanmar, malaysia, singapore, cambodia, laos。"""
    service = get_disaster_service()
    alerts = asyncio.run(service.get_regional_alerts(region))
    if not alerts:
        return f"暂无{region}区域的预警信息。"

    lines = [f"【{region.upper()} 灾害预警】共{len(alerts)}条："]
    for alert in alerts:
        lines.append(f"\n⚠️ {alert['level_name']}级 {alert['type_name']}预警: {alert['title']}")
        lines.append(f"   {alert['content']}")
        lines.append(f"   影响区域: {', '.join(alert['affected_areas'])}")
    return "\n".join(lines)


@tool
def get_typhoon_info() -> str:
    """获取当前西太平洋区域的台风信息，包括台风名称、位置、强度、移动方向和预报路径。"""
    service = get_disaster_service()
    typhoons = asyncio.run(service.get_typhoon_list())

    if not typhoons:
        return "当前西太平洋区域没有活跃台风。"

    lines = ["【当前活跃台风】"]
    for t in typhoons:
        lines.append(f"\n🌀 台风 {t['name']} ({t['code']})")
        lines.append(f"   状态: {t['status']}")
        lines.append(f"   位置: 北纬{t['position']['lat']}°, 东经{t['position']['lon']}°")
        lines.append(f"   强度: {t['intensity']}, 最大风速 {t['max_wind_speed']} km/h")
        lines.append(f"   移动: {t['move_direction']} {t['move_speed']} km/h")
        lines.append(f"   影响区域: {', '.join(t['impact_regions'])}")
    return "\n".join(lines)


@tool
def get_agriculture_advice(region: str = "guangxi") -> str:
    """获取农业气象建议，包括灌溉、施药、收割时机等农事活动建议。"""
    service = get_disaster_service()
    agri = asyncio.run(service.get_agriculture_alert(region))

    lines = [f"【{region.upper()} 农业气象建议】"]
    for alert in agri.get("alerts", []):
        lines.append(f"\n🌾 {alert['crop']} ({alert['stage']})")
        lines.append(f"   风险: {alert['risk']} (等级: {alert['level']})")
        lines.append(f"   建议: {alert['advice']}")
        lines.append(f"   有效期: {alert['valid_period']}")
    return "\n".join(lines)


@tool
def get_travel_advice(city: str = "bangkok") -> str:
    """获取旅游气象建议，包括天气舒适度、最佳出行时段、景点注意事项等。"""
    travel_advice = {
        "bangkok": {
            "city": "曼谷",
            "best_time": "11月-次年2月（凉季）",
            "current_advice": "近期高温，建议早晨或傍晚出行，避开10-14时户外活动。",
            "tips": ["带遮阳帽和防晒霜", "多补充水分", "准备雨具（雨季5-10月）"],
        },
        "hanoi": {
            "city": "河内",
            "best_time": "10月-次年3月（旱季）",
            "current_advice": "近期多阵雨，建议携带雨具，早晚气温适宜出行。",
            "tips": ["关注实时天气预报", "雨季注意防滑", "冬季早晚温差大"],
        },
        "singapore": {
            "city": "新加坡",
            "best_time": "全年适宜（室内活动为主）",
            "current_advice": "近期晴热，室内冷气充足，注意冷热交替。",
            "tips": ["全年有雨，随身带伞", "室内外温差大", "注意防晒"],
        },
        "nanning": {
            "city": "南宁",
            "best_time": "10月-次年3月",
            "current_advice": "近期气温适宜，早晚凉爽，适合户外活动。",
            "tips": ["关注台风动态（6-10月）", "夏季注意防暑", "回南天注意防潮"],
        },
    }

    advice = travel_advice.get(city.lower(), travel_advice["bangkok"])
    lines = [f"【{advice['city']} 旅游气象建议】"]
    lines.append(f"最佳旅游时间: {advice['best_time']}")
    lines.append(f"当前建议: {advice['current_advice']}")
    lines.append("注意事项:")
    for tip in advice["tips"]:
        lines.append(f"  • {tip}")
    return "\n".join(lines)


@tool
def get_logistics_advice(route: str = "nanning_hcmc") -> str:
    """获取物流运输气象建议，包括路线风险评估、最佳运输窗口等。"""
    service = get_disaster_service()
    logistics = asyncio.run(service.get_logistics_alert(route))

    if not logistics:
        return f"暂无 {route} 路线的物流气象信息。"

    lines = [f"【物流气象】{logistics.get('route', route)}"]
    lines.append(f"整体风险等级: {logistics.get('risk_level', 'unknown')}")

    for seg in logistics.get("segments", []):
        risk_emoji = {"low": "✅", "medium": "⚠️", "high": "🚨"}.get(seg["risk"], "❓")
        lines.append(f"\n{risk_emoji} {seg['segment']}: {seg['weather']} (风险: {seg['risk']})")

    lines.append(f"\n💡 建议: {logistics.get('recommendation', '暂无')}")
    return "\n".join(lines)


# 导出工具列表（扩展到7个工具）
WEATHER_TOOLS = [
    get_current_weather,
    get_weather_forecast,
    get_city_weather,
    get_disaster_alert,
    get_typhoon_info,
    get_agriculture_advice,
    get_travel_advice,
    get_logistics_advice,
]
