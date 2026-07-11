"""
个人气象日记服务
自动记录天气数据 + 用户感受，支持历史对比和气候回顾
"""

from __future__ import annotations

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.journal import JournalEntry
from app.services.historical_service import HistoricalService
from app.services.weather_service import WeatherService

logger = structlog.get_logger("services.journal")

# 多语言气候回顾模板
REVIEW_TEMPLATES: dict[str, str] = {
    "zh": (
        "在{period}期间，您记录了{count}天的天气日记。"
        "平均温度{avg_temp}°C，最高温{max_temp}°C，最低温{min_temp}°C。"
        "总降水量{total_precip}mm。"
    ),
    "en": (
        "During {period}, you recorded {count} days of weather journal. "
        "Average temperature {avg_temp}°C, max {max_temp}°C, min {min_temp}°C. "
        "Total precipitation {total_precip}mm."
    ),
    "vi": (
        "Trong {period}, bạn đã ghi nhận {count} ngày nhật ký thời tiết. "
        "Nhiệt độ trung bình {avg_temp}°C, cao nhất {max_temp}°C, "
        "thấp nhất {min_temp}°C. Tổng lượng mưa {total_precip}mm."
    ),
    "th": (
        "ในช่วง {period} คุณบันทึก天气ได้ {count} วัน "
        "อุณหภูมิเฉลี่ย {avg_temp}°C สูงสุด {max_temp}°C "
        "ต่ำสุด {min_temp}°C ปริมาณฝนรวม {total_precip}mm"
    ),
    "id": (
        "Selama {period}, Anda mencatat {count} hari jurnal cuaca. "
        "Suhu rata-rata {avg_temp}°C, maks {max_temp}°C, min {min_temp}°C. "
        "Total curah hujan {total_precip}mm."
    ),
}


class JournalService:
    """个人气象日记服务"""

    def __init__(self) -> None:
        self._weather_service = WeatherService()
        self._historical_service = HistoricalService()

    async def create_entry(
        self,
        db: AsyncSession,
        user_id: int,
        latitude: float,
        longitude: float,
        feelings: str | None = None,
        mood: str | None = None,
        language: str = "zh",
    ) -> dict:
        """创建日记条目 — 自动获取当日天气数据"""
        # 获取当前天气
        weather = await self._weather_service.get_current_weather(latitude, longitude)
        current = weather  # get_current_weather returns flat dict

        # 创建条目
        entry = JournalEntry(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            temperature=current.get("temperature"),
            humidity=current.get("humidity"),
            wind_speed=current.get("wind_speed"),
            precipitation=current.get("precipitation"),
            weather_code=current.get("weather_code"),
            feelings=feelings,
            mood=mood,
            language=language,
        )
        db.add(entry)
        await db.flush()

        logger.info("journal_entry_created", user_id=user_id, entry_id=entry.id)

        return {
            "id": entry.id,
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "temperature": entry.temperature,
            "humidity": entry.humidity,
            "wind_speed": entry.wind_speed,
            "precipitation": entry.precipitation,
            "weather_code": entry.weather_code,
            "feelings": entry.feelings,
            "mood": entry.mood,
            "language": entry.language,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }

    async def get_entries(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """获取用户日记列表"""
        result = await db.execute(
            select(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .order_by(JournalEntry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        entries = result.scalars().all()

        return [
            {
                "id": e.id,
                "latitude": e.latitude,
                "longitude": e.longitude,
                "temperature": e.temperature,
                "humidity": e.humidity,
                "weather_code": e.weather_code,
                "feelings": e.feelings,
                "mood": e.mood,
                "language": e.language,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ]

    async def get_review(
        self,
        db: AsyncSession,
        user_id: int,
        latitude: float,
        longitude: float,
        period: str = "monthly",
        language: str = "zh",
    ) -> dict:
        """生成气候回顾 — 统计分析 + 历史对比"""
        # 统计日记数据
        result = await db.execute(
            select(
                func.count(JournalEntry.id),
                func.avg(JournalEntry.temperature),
                func.max(JournalEntry.temperature),
                func.min(JournalEntry.temperature),
                func.sum(JournalEntry.precipitation),
            ).where(JournalEntry.user_id == user_id)
        )
        row = result.one()
        count = row[0] or 0
        avg_temp = round(row[1] or 0, 1)
        max_temp = round(row[2] or 0, 1)
        min_temp = round(row[3] or 0, 1)
        total_precip = round(row[4] or 0, 1)

        if count == 0:
            return {
                "user_id": user_id,
                "period": period,
                "message": "暂无日记记录" if language == "zh" else "No journal entries yet",
                "stats": None,
            }

        # 生成回顾文本
        template = REVIEW_TEMPLATES.get(language, REVIEW_TEMPLATES["en"])
        review_text = template.format(
            period=period,
            count=count,
            avg_temp=avg_temp,
            max_temp=max_temp,
            min_temp=min_temp,
            total_precip=total_precip,
        )

        return {
            "user_id": user_id,
            "period": period,
            "review": review_text,
            "stats": {
                "total_entries": count,
                "avg_temperature": avg_temp,
                "max_temperature": max_temp,
                "min_temperature": min_temp,
                "total_precipitation": total_precip,
            },
            "language": language,
        }
