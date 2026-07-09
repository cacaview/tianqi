"""
可再生能源发电预测服务
基于Open-Meteo太阳能辐射和风速数据预测发电量
"""

from __future__ import annotations

import structlog

from app.services.weather_service import WeatherService

logger = structlog.get_logger("services.energy_forecast")

# 光伏效率参数
DEFAULT_SOLAR_EFFICIENCY: float = 0.17  # 15%-20% typical
TEMPERATURE_COEFFICIENT: float = -0.004  # 每°C功率变化率（25°C以上）

# 风电功率曲线参数
DEFAULT_CUT_IN_SPEED: float = 3.0  # m/s
DEFAULT_RATED_SPEED: float = 12.0  # m/s
DEFAULT_CUT_OUT_SPEED: float = 25.0  # m/s


class EnergyForecastService:
    """可再生能源发电预测服务"""

    def __init__(self) -> None:
        self._weather_service = WeatherService()

    async def solar_forecast(
        self,
        latitude: float,
        longitude: float,
        capacity_kw: float = 10.0,
        days: int = 3,
    ) -> dict:
        """太阳能发电预测 — 基于辐射数据计算逐时发电量"""
        forecast = await self._weather_service.get_forecast(latitude, longitude, days)
        daily = forecast.get("forecast", [])

        # 使用天气代码推断日照状况估算发电量
        results = []
        for day in daily:
            code = day.get("weather_code", 0) or 0
            temp_max = day.get("temp_max", 25) or 25

            # 基于天气代码估算日辐射强度（W/m²）
            radiation = _estimate_radiation(code)

            # 温度修正
            temp_factor = 1.0
            if temp_max > 25:
                temp_factor = 1.0 + TEMPERATURE_COEFFICIENT * (temp_max - 25)

            # 日发电量 (kWh) = 辐射 × 装机 × 效率 × 温度修正 / 1000
            daily_output = radiation * capacity_kw * DEFAULT_SOLAR_EFFICIENCY * temp_factor * 6 / 1000

            results.append({
                "date": day.get("date"),
                "estimated_radiation_wm2": radiation,
                "temperature_factor": round(temp_factor, 3),
                "daily_output_kwh": round(daily_output, 2),
                "weather_code": code,
            })

        return {
            "latitude": latitude,
            "longitude": longitude,
            "capacity_kw": capacity_kw,
            "efficiency": DEFAULT_SOLAR_EFFICIENCY,
            "forecast": results,
        }

    async def wind_power_forecast(
        self,
        latitude: float,
        longitude: float,
        rated_power_kw: float = 100.0,
        days: int = 3,
    ) -> dict:
        """风力发电预测 — 基于风速功率曲线计算发电量"""
        forecast = await self._weather_service.get_forecast(latitude, longitude, days)
        daily = forecast.get("forecast", [])

        results = []
        for day in daily:
            wind_speed = day.get("wind_speed_max", 0) or 0
            wind_ms = wind_speed / 3.6  # km/h → m/s

            # 功率曲线
            power_ratio = _wind_power_ratio(wind_ms)
            daily_output = rated_power_kw * power_ratio * 24  # kWh

            results.append({
                "date": day.get("date"),
                "wind_speed_kmh": wind_speed,
                "power_ratio": round(power_ratio, 3),
                "daily_output_kwh": round(daily_output, 2),
            })

        return {
            "latitude": latitude,
            "longitude": longitude,
            "rated_power_kw": rated_power_kw,
            "forecast": results,
        }


def _estimate_radiation(weather_code: int) -> float:
    """基于天气代码估算日照辐射（W/m²日均值）"""
    if weather_code in (0,):
        return 800.0  # 晴天
    if weather_code in (1,):
        return 600.0  # 大部晴朗
    if weather_code in (2, 3):
        return 400.0  # 多云
    if weather_code in (45, 48):
        return 200.0  # 雾
    if weather_code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return 100.0  # 雨
    if weather_code in (71, 73, 75):
        return 150.0  # 雪
    if weather_code in (95, 96, 99):
        return 50.0  # 雷暴
    return 400.0


def _wind_power_ratio(wind_ms: float) -> float:
    """风速功率比 — 标准化功率曲线"""
    if wind_ms < DEFAULT_CUT_IN_SPEED:
        return 0.0
    if wind_ms >= DEFAULT_CUT_OUT_SPEED:
        return 0.0  # 切出
    if wind_ms >= DEFAULT_RATED_SPEED:
        return 1.0  # 额定
    # 线性插值
    return (wind_ms - DEFAULT_CUT_IN_SPEED) / (DEFAULT_RATED_SPEED - DEFAULT_CUT_IN_SPEED)
