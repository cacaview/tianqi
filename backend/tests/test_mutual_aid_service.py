"""
MutualAidService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.mutual_aid_service import MutualAidService


@pytest.fixture
def mutual_aid_service() -> MutualAidService:
    """创建 MutualAidService 实例"""
    return MutualAidService()


@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_create_request_help(mutual_aid_service: MutualAidService, mock_db) -> None:
    """测试创建互助请求 — 求助"""
    result = await mutual_aid_service.create_request(
        mock_db, 1, "help", "rescue", "需要救援", 22.82, 108.32, "zh"
    )

    assert "id" in result
    assert result["user_id"] == 1
    assert result["request_type"] == "help"
    assert result["category"] == "rescue"
    assert result["description"] == "需要救援"
    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["language"] == "zh"
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_create_request_offer(mutual_aid_service: MutualAidService, mock_db) -> None:
    """测试创建互助请求 — 提供帮助"""
    result = await mutual_aid_service.create_request(
        mock_db, 2, "offer", "shelter", "可以提供避难所", 22.80, 108.30, "zh"
    )

    assert result["request_type"] == "offer"
    assert result["category"] == "shelter"
    assert result["description"] == "可以提供避难所"


@pytest.mark.asyncio
async def test_create_request_english(mutual_aid_service: MutualAidService, mock_db) -> None:
    """测试创建互助请求 — 英文"""
    result = await mutual_aid_service.create_request(
        mock_db, 1, "help", "food", "Need food supplies", 22.82, 108.32, "en"
    )

    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_get_open_requests_success(mutual_aid_service: MutualAidService, mock_db) -> None:
    """测试获取开放请求 — 成功"""
    mock_requests = [
        MagicMock(
            id=1,
            user_id=1,
            request_type="help",
            category="rescue",
            description="需要救援",
            latitude=22.82,
            longitude=108.32,
            status="open",
            language="zh",
            created_at=MagicMock(isoformat=MagicMock(return_value="2024-01-01T00:00:00")),
        ),
        MagicMock(
            id=2,
            user_id=2,
            request_type="offer",
            category="shelter",
            description="可以提供避难所",
            latitude=22.80,
            longitude=108.30,
            status="open",
            language="zh",
            created_at=MagicMock(isoformat=MagicMock(return_value="2024-01-01T01:00:00")),
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_requests
    mock_db.execute.return_value = mock_result

    result = await mutual_aid_service.get_open_requests(mock_db, 22.82, 108.32, 20)

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["request_type"] == "help"
    assert result[1]["id"] == 2
    assert result[1]["request_type"] == "offer"


@pytest.mark.asyncio
async def test_get_open_requests_empty(mutual_aid_service: MutualAidService, mock_db) -> None:
    """测试获取开放请求 — 空结果"""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await mutual_aid_service.get_open_requests(mock_db, 22.82, 108.32, 20)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_open_requests_no_location(mutual_aid_service: MutualAidService, mock_db) -> None:
    """测试获取开放请求 — 无位置过滤"""
    mock_requests = [
        MagicMock(
            id=1,
            user_id=1,
            request_type="help",
            category="rescue",
            description="需要救援",
            latitude=22.82,
            longitude=108.32,
            status="open",
            language="zh",
            created_at=MagicMock(isoformat=MagicMock(return_value="2024-01-01T00:00:00")),
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_requests
    mock_db.execute.return_value = mock_result

    result = await mutual_aid_service.get_open_requests(mock_db, limit=20)

    assert len(result) == 1


@pytest.mark.asyncio
async def test_respond_to_request(mutual_aid_service: MutualAidService, mock_db) -> None:
    """测试响应互助请求"""
    mock_request = MagicMock(
        id=1,
        user_id=1,
        request_type="help",
        category="rescue",
        description="需要救援",
        latitude=22.82,
        longitude=108.32,
        status="open",
        language="zh",
        created_at=MagicMock(isoformat=MagicMock(return_value="2024-01-01T00:00:00")),
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_request
    mock_db.execute.return_value = mock_result

    result = await mutual_aid_service.respond_to_request(mock_db, 1, 2)

    assert result["request_id"] == 1
    assert result["status"] == "matched"
    assert result["responder_id"] == 2


@pytest.mark.asyncio
async def test_respond_to_request_not_found(mutual_aid_service: MutualAidService, mock_db) -> None:
    """测试响应互助请求 — 未找到"""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await mutual_aid_service.respond_to_request(mock_db, 999, 2)

    assert "error" in result
