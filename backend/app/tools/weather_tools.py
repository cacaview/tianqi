"""
气象工具链 - 供LangChain Agent调用
Phase 2: 扩展灾害预警和行业决策工具
"""

import asyncio

from langchain_core.tools import tool

from app.services.agro_decision_service import AgroDecisionService
from app.services.air_quality_service import AirQualityService
from app.services.construction_safety_service import ConstructionSafetyService
from app.services.cross_border_service import CrossBorderService
from app.services.disaster_service import get_disaster_service
from app.services.earthquake_service import EarthquakeService
from app.services.energy_forecast_service import EnergyForecastService
from app.services.health_index_service import HealthIndexService
from app.services.insurance_index_service import InsuranceIndexService
from app.services.marine_decision_service import MarineDecisionService
from app.services.weather_service import WeatherService

_weather_service = WeatherService()
_air_quality_service = AirQualityService()
_earthquake_service = EarthquakeService()
_health_index_service = HealthIndexService()
_construction_safety_service = ConstructionSafetyService()
_marine_decision_service = MarineDecisionService()
_energy_forecast_service = EnergyForecastService()
_agro_decision_service = AgroDecisionService()
_insurance_index_service = InsuranceIndexService()
_cross_border_service = CrossBorderService()


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
    """根据城市名称获取天气。

    支持城市：nanning(南宁), hanoi(河内), bangkok(曼谷),
    jakarta(雅加达), manila(马尼拉), kuala_lumpur(吉隆坡),
    singapore(新加坡), phnom_penh(金边), vientiane(万象),
    yangon(仰光)等东盟主要城市。
    """
    cities = _weather_service.get_asean_cities()
    city_key = city_name.lower().replace(" ", "_")

    if city_key not in cities:
        available = ", ".join(cities.keys())
        return f"未找到城市 '{city_name}'。可用城市: {available}"

    city = cities[city_key]
    result = asyncio.run(_weather_service.get_current_weather(city["lat"], city["lon"]))
    return f"{city['name']}({city['name_en']}): {result}"


@tool
def get_minutely_precipitation(latitude: float, longitude: float) -> str:
    """获取分钟级降水预报数据（未来2小时，15分钟间隔）"""
    result = asyncio.run(_weather_service.get_minutely_precipitation(latitude, longitude))
    return str(result)


@tool
def get_current_air_quality(latitude: float, longitude: float) -> str:
    """获取当前位置的空气质量数据，包括PM2.5、PM10、AQI等。经纬度为必填参数。"""
    result = asyncio.run(_air_quality_service.get_current(latitude, longitude))
    return str(result)


@tool
def get_disaster_alert(region: str = "guangxi") -> str:
    """获取指定区域的极端天气和灾害预警信息。

    region可选：guangxi(广西), vietnam, thailand, indonesia,
    philippines, myanmar, malaysia, singapore, cambodia, laos。
    """
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


@tool
def get_earthquake_info(source: str = "cenc") -> str:
    """获取近期地震信息。source: cenc(中国), jma(日本), usgs(美国)"""
    result = asyncio.run(_earthquake_service.get_recent_earthquakes(source=source))
    earthquakes = result.get("earthquakes", [])

    if not earthquakes:
        return f"暂无{source}数据源的地震信息。"

    lines = [f"【近期地震信息】共{result.get('total', 0)}条："]
    for eq in earthquakes[:5]:
        lines.append(f"\n🔴 {eq['hypocenter']} - 震级 M{eq['magnitude']}")
        if eq.get("max_intensity"):
            lines.append(f"   最大烈度: {eq['max_intensity']}")
        if eq.get("latitude") and eq.get("longitude"):
            lines.append(f"   位置: 北纬{eq['latitude']}°, 东经{eq['longitude']}°")
        if eq.get("depth_km"):
            lines.append(f"   震源深度: {eq['depth_km']} km")
        if eq.get("occurred_at"):
            lines.append(f"   发震时间: {eq['occurred_at']}")
    return "\n".join(lines)


@tool
def get_lifestyle_indices(latitude: float, longitude: float, language: str = "zh") -> str:
    """获取生活气象指数，包括穿衣、洗车、运动、紫外线、带伞、旅游建议"""
    import json

    from app.services.lifestyle_service import LifestyleService

    service = LifestyleService()
    try:
        return json.dumps(asyncio.run(service.get_lifestyle_indices(latitude, longitude, language)), ensure_ascii=False)
    finally:
        asyncio.run(service._weather_service.close())


@tool
def generate_weather_report(latitude: float, longitude: float, language: str = "zh") -> str:
    """生成一段自然语言天气报告，综合当前天气、预报和灾害预警信息。
    返回结构化的多语言天气叙述报告。
    """
    import asyncio

    from app.core.constants import WMO_WEATHER_CODES
    from app.services.disaster_service import DisasterAlertService
    from app.services.weather_service import WeatherService

    ws = WeatherService()
    ds = DisasterAlertService()
    try:
        current = asyncio.run(ws.get_current_weather(latitude, longitude))
        forecast = asyncio.run(ws.get_forecast(latitude, longitude, 3))

        weather_desc = WMO_WEATHER_CODES.get(current.get("weather_code", -1), "未知")
        temp = current.get("temperature", "N/A")
        humidity = current.get("humidity", "N/A")
        wind = current.get("wind_speed", "N/A")

        # Build report based on language
        if language == "zh":
            report = "【天气报告】\n\n"
            report += f"📍 当前天气：{weather_desc}\n"
            report += f"🌡️ 气温：{temp}°C（体感 {current.get('feels_like', 'N/A')}°C）\n"
            report += f"💧 湿度：{humidity}%\n"
            report += f"🌬️ 风速：{wind} km/h\n\n"
            report += "📅 未来三天预报：\n"
            for day in forecast.get("forecast", [])[:3]:
                report += f"  {day.get('date')}: {day.get('temp_min')}~{day.get('temp_max')}°C\n"
        else:
            report = "[Weather Report]\n\n"
            report += f"Current: {weather_desc}, {temp}°C\n"
            report += f"Humidity: {humidity}%, Wind: {wind} km/h\n"
            report += "3-day forecast:\n"
            for day in forecast.get("forecast", [])[:3]:
                report += f"  {day.get('date')}: {day.get('temp_min')}~{day.get('temp_max')}°C\n"

        return report
    finally:
        asyncio.run(ws.close())
        asyncio.run(ds.close())


@tool
def get_health_index(latitude: float, longitude: float, language: str = "zh") -> str:
    """获取城市天气健康指数。综合温度舒适度、空气质量、紫外线、降水概率的0-100评分。"""
    result = asyncio.run(_health_index_service.calculate(latitude, longitude, language))
    return str(result)


@tool
def get_construction_safety(latitude: float, longitude: float, language: str = "zh") -> str:
    """建筑工地气象安全评估。基于风速、雷暴、热应力、降水四因子判断是否适合施工（Go/No-Go/Caution）。"""
    result = asyncio.run(_construction_safety_service.assess(latitude, longitude, language))
    return str(result)


@tool
def get_marine_safety(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    language: str = "zh",
) -> str:
    """海事气象决策：评估航线风险，返回Go/No-Go/Caution决策和沿途海况。"""
    result = asyncio.run(_marine_decision_service.assess_route(origin_lat, origin_lon, dest_lat, dest_lon, language))
    return str(result)


@tool
def get_solar_energy_forecast(latitude: float, longitude: float, capacity_kw: float = 10.0, days: int = 3) -> str:
    """可再生能源发电预测：基于天气数据预测太阳能逐日发电量。"""
    result = asyncio.run(_energy_forecast_service.solar_forecast(latitude, longitude, capacity_kw, days))
    return str(result)


@tool
def get_wind_energy_forecast(latitude: float, longitude: float, rated_power_kw: float = 100.0, days: int = 3) -> str:
    """风力发电预测：基于风速功率曲线预测逐日发电量。"""
    result = asyncio.run(_energy_forecast_service.wind_power_forecast(latitude, longitude, rated_power_kw, days))
    return str(result)


@tool
def get_agro_irrigation(latitude: float, longitude: float, language: str = "zh") -> str:
    """农业灌溉建议：基于土壤湿度和蒸发量判断是否需要灌溉。"""
    result = asyncio.run(_agro_decision_service.irrigation_advice(latitude, longitude, language))
    return str(result)


@tool
def get_agro_pest_risk(latitude: float, longitude: float, language: str = "zh") -> str:
    """农业病虫害风险评估：基于温度和湿度组合判断病虫害风险等级。"""
    result = asyncio.run(_agro_decision_service.pest_risk(latitude, longitude, language))
    return str(result)


@tool
def get_insurance_index(latitude: float, longitude: float, crop_type: str = "rice", language: str = "zh") -> str:
    """农业气象保险指数：基于历史数据计算参数化保险触发条件（干旱/洪涝/热害）。"""
    result = asyncio.run(_insurance_index_service.calculate_trigger(latitude, longitude, crop_type, 90, language))
    return str(result)


@tool
def get_cross_border_disaster_analysis(language: str = "zh") -> str:
    """跨境灾害协同预警：关联分析多国灾害事件，生成跨境影响链。"""
    result = asyncio.run(_cross_border_service.correlate_events(48, language))
    return str(result)


# 导出工具列表
WEATHER_TOOLS = [
    get_current_weather,
    get_weather_forecast,
    get_city_weather,
    get_minutely_precipitation,
    get_current_air_quality,
    get_disaster_alert,
    get_typhoon_info,
    get_agriculture_advice,
    get_travel_advice,
    get_logistics_advice,
    get_earthquake_info,
    get_lifestyle_indices,
    generate_weather_report,
    get_health_index,
    get_construction_safety,
    get_marine_safety,
    get_solar_energy_forecast,
    get_wind_energy_forecast,
    get_agro_irrigation,
    get_agro_pest_risk,
    get_insurance_index,
    get_cross_border_disaster_analysis,
]
