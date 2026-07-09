"""
AI天气播报频道 API
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import SettingsDep
from app.api.schemas import BroadcastResponse, SubscriptionRequest, SubscriptionResponse

router = APIRouter()


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe(
    request: SubscriptionRequest,
    settings: SettingsDep = None,  # type: ignore[assignment]
) -> SubscriptionResponse:
    """订阅天气播报频道"""
    return SubscriptionResponse(
        channel=request.channel,
        recipient=request.recipient,
        message="订阅成功" if request.language == "zh" else "Subscription successful",
    )


@router.get("/subscriptions", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    settings: SettingsDep = None,  # type: ignore[assignment]
) -> list[SubscriptionResponse]:
    """获取订阅列表"""
    return []


@router.post("/broadcast", response_model=BroadcastResponse)
async def broadcast(
    latitude: float,
    longitude: float,
    language: str = "zh",
    settings: SettingsDep = None,  # type: ignore[assignment]
) -> BroadcastResponse:
    """手动触发天气播报"""
    return BroadcastResponse(
        message="播报已发送" if language == "zh" else "Broadcast sent",
        channels=["email"],
        language=language,
    )
