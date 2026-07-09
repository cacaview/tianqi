"""
个人气象日记 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import DbSession, JournalServiceDep, SettingsDep
from app.api.schemas import JournalCreateRequest, JournalEntryResponse, JournalListResponse, JournalReviewResponse

router = APIRouter()


@router.post("/entry", response_model=JournalEntryResponse)
async def create_journal_entry(
    request: JournalCreateRequest,
    db: DbSession = None,  # type: ignore[assignment]
    settings: SettingsDep = None,  # type: ignore[assignment]
    journal_service: JournalServiceDep = None,  # type: ignore[assignment]
) -> JournalEntryResponse:
    """创建气象日记条目 — 自动获取当日天气数据"""
    data = await journal_service.create_entry(
        db=db,
        user_id=request.user_id,
        latitude=request.latitude,
        longitude=request.longitude,
        feelings=request.feelings,
        mood=request.mood,
        language=request.language,
    )
    return JournalEntryResponse(**data)


@router.get("/list", response_model=JournalListResponse)
async def list_journal_entries(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    db: DbSession = None,  # type: ignore[assignment]
    settings: SettingsDep = None,  # type: ignore[assignment]
    journal_service: JournalServiceDep = None,  # type: ignore[assignment]
) -> JournalListResponse:
    """获取用户日记列表"""
    entries = await journal_service.get_entries(db=db, user_id=user_id, limit=limit, offset=offset)
    return JournalListResponse(entries=entries, total=len(entries))


@router.get("/review", response_model=JournalReviewResponse)
async def get_journal_review(
    user_id: int,
    latitude: float,
    longitude: float,
    period: str = "monthly",
    language: str = "zh",
    db: DbSession = None,  # type: ignore[assignment]
    settings: SettingsDep = None,  # type: ignore[assignment]
    journal_service: JournalServiceDep = None,  # type: ignore[assignment]
) -> JournalReviewResponse:
    """生成气候回顾 — 统计分析 + 历史对比"""
    data = await journal_service.get_review(
        db=db,
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        period=period,
        language=language,
    )
    return JournalReviewResponse(**data)
