"""
智能对话API接口
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()


class ChatRequest(BaseModel):
    message: str
    language: str = "zh"  # zh/en/vi/th/id/my/lo
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    language: str
    tools_used: list[str] = []


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """发送消息给AI助手"""
    result = await agent_service.chat(
        message=request.message,
        language=request.language,
        latitude=request.latitude,
        longitude=request.longitude,
        session_id=request.session_id,
    )
    return result
