"""
通知订阅模型
"""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class NotificationSubscription(TimestampMixin, Base):
    """通知订阅表 — 用户订阅天气播报频道"""

    __tablename__ = "notification_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)  # telegram/whatsapp/email
    recipient: Mapped[str] = mapped_column(String(128), nullable=False)  # chat_id / phone / email
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    city_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False, default="zh")
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    broadcast_time: Mapped[str] = mapped_column(String(8), nullable=False, default="07:00")  # HH:MM
