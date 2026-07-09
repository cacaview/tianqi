"""
众包天气观测模型
"""

from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Observation(TimestampMixin, Base):
    """众包天气观测表 — 用户提交的实时天气报告"""

    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    weather_type: Mapped[str] = mapped_column(String(32), nullable=False)  # sunny/rainy/stormy/foggy/...
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False, default="zh")
    verified: Mapped[bool] = mapped_column(nullable=False, default=False)
