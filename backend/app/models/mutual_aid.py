"""
天气应急互助圈模型
"""

from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class MutualAidRequest(TimestampMixin, Base):
    """互助请求表 — 极端天气期间的社区互助"""

    __tablename__ = "mutual_aid_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    request_type: Mapped[str] = mapped_column(String(32), nullable=False)  # help/offer
    category: Mapped[str] = mapped_column(String(32), nullable=False)  # food/water/shelter/medical/transport/other
    description: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False, default="zh")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")  # open/matched/resolved/closed
    matched_with: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 匹配的请求ID
    disaster_event: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 关联的灾害事件
