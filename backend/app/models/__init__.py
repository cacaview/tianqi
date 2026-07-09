"""
ORM 模型汇总 — 导入所有模型以确保 Alembic 能发现它们
"""

from app.models.api_key import ApiKey
from app.models.base import Base, TimestampMixin
from app.models.journal import JournalEntry
from app.models.mutual_aid import MutualAidRequest
from app.models.notification import NotificationSubscription
from app.models.observation import Observation
from app.models.user import User

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Observation",
    "JournalEntry",
    "NotificationSubscription",
    "ApiKey",
    "MutualAidRequest",
]
