"""
API 密钥管理模型
"""

from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ApiKey(TimestampMixin, Base):
    """API 密钥表 — 企业 APIaaS 认证"""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)  # 用途描述
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    rate_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=100)  # 每分钟请求上限
    total_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    allowed_endpoints: Mapped[str | None] = mapped_column(String(512), nullable=True)  # 逗号分隔
