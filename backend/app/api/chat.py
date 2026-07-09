"""
智能对话 API 路由
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Request

from app.api.deps import AgentServiceDep
from app.api.schemas import ChatRequest, ChatResponse

router = APIRouter()

# 简易内存限流器：每个 IP 每分钟最多 30 次请求
_rate_limits: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_MAX = 30
_RATE_LIMIT_WINDOW = 60.0  # 秒


def _check_rate_limit(client_ip: str) -> None:
    """检查速率限制，超限抛出 429"""
    now = time.time()
    # 清除过期记录
    _rate_limits[client_ip] = [t for t in _rate_limits[client_ip] if now - t < _RATE_LIMIT_WINDOW]
    if len(_rate_limits[client_ip]) >= _RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=429,
            detail="请求过于频繁，请稍后再试",
        )
    _rate_limits[client_ip].append(now)


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: Request,
    chat_request: ChatRequest,
    agent_service: AgentServiceDep,
) -> ChatResponse:
    """发送消息给 AI 助手"""
    # 限流检查
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    result = await agent_service.chat(
        message=chat_request.message,
        language=chat_request.language,
        latitude=chat_request.latitude,
        longitude=chat_request.longitude,
        session_id=chat_request.session_id,
    )
    return ChatResponse(**result)
