"""
JournalService 单元测试
使用 unittest.mock 模拟外部服务
"""

from __future__ import annotations

import httpx
import pytest
import respx
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.journal_service import JournalService


@pytest.fixture
def journal_service() -> JournalService:
    """创建 JournalService 实例"""
    return JournalService()


@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_create_entry_success(journal_service: JournalService, mock_db) -> None:
    """测试创建日记条目 — 成功"""
    mock_weather = {
        "temperature": 25.0,
        "humidity": 60,
        "wind_speed": 10.0,
        "precipitation": 0.0,
        "weather_code": 0,
        "timezone": "Asia/Shanghai",
        "latitude": 22.82,
        "longitude": 108.32,
    }

    with patch.object(journal_service._weather_service, "get_current_weather", new_callable=AsyncMock, return_value=mock_weather):
        result = await journal_service.create_entry(mock_db, 1, 22.82, 108.32, "舒适", "happy", "zh")

    assert "id" in result
    assert result["user_id"] == 1
    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["temperature"] == 25.0
    assert result["humidity"] == 60
    assert result["feelings"] == "舒适"
    assert result["mood"] == "happy"
    assert result["language"] == "zh"
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_create_entry_without_optional(journal_service: JournalService, mock_db) -> None:
    """测试创建日记条目 — 无可选字段"""
    mock_weather = {
        "temperature": 28.0,
        "humidity": 70,
        "wind_speed": 15.0,
        "precipitation": 5.0,
        "weather_code": 61,
        "timezone": "Asia/Shanghai",
        "latitude": 22.82,
        "longitude": 108.32,
    }

    with patch.object(journal_service._weather_service, "get_current_weather", new_callable=AsyncMock, return_value=mock_weather):
        result = await journal_service.create_entry(mock_db, 1, 22.82, 108.32)

    assert result["temperature"] == 28.0
    assert result["precipitation"] == 5.0
    assert result["feelings"] is None
    assert result["mood"] is None


@pytest.mark.asyncio
async def test_create_entry_http_error(journal_service: JournalService, mock_db) -> None:
    """测试创建日记条目 — HTTP错误"""
    with patch.object(
        journal_service._weather_service, "get_current_weather",
        new_callable=AsyncMock, side_effect=httpx.HTTPStatusError("500", request=MagicMock(), response=MagicMock(status_code=500))
    ):
        with pytest.raises(httpx.HTTPStatusError):
            await journal_service.create_entry(mock_db, 1, 22.82, 108.32)


@pytest.mark.asyncio
async def test_get_entries_success(journal_service: JournalService, mock_db) -> None:
    """测试获取日记条目 — 成功"""
    from datetime import datetime

    mock_entries = [
        MagicMock(
            id=1,
            latitude=22.82,
            longitude=108.32,
            temperature=25.0,
            humidity=60,
            weather_code=0,
            feelings="舒适",
            mood="happy",
            language="zh",
            created_at=datetime(2024, 1, 1),
        ),
        MagicMock(
            id=2,
            latitude=22.82,
            longitude=108.32,
            temperature=28.0,
            humidity=70,
            weather_code=61,
            feelings="闷热",
            mood="neutral",
            language="zh",
            created_at=datetime(2024, 1, 2),
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_entries
    mock_db.execute.return_value = mock_result

    result = await journal_service.get_entries(mock_db, 1, limit=20, offset=0)

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["temperature"] == 25.0
    assert result[1]["id"] == 2
    assert result[1]["temperature"] == 28.0


@pytest.mark.asyncio
async def test_get_entries_empty(journal_service: JournalService, mock_db) -> None:
    """测试获取日记条目 — 空结果"""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await journal_service.get_entries(mock_db, 1, limit=20, offset=0)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_review_success(journal_service: JournalService, mock_db) -> None:
    """测试生成气候回顾 — 成功"""
    mock_row = MagicMock()
    mock_row.__getitem__ = lambda self, key: [10, 25.0, 30.0, 20.0, 50.0][key]
    mock_result = MagicMock()
    mock_result.one.return_value = mock_row
    mock_db.execute.return_value = mock_result

    result = await journal_service.get_review(mock_db, 1, 22.82, 108.32, "monthly", "zh")

    assert "review" in result
    assert "stats" in result
    assert result["language"] == "zh"
    assert result["period"] == "monthly"
    assert len(result["review"]) > 0


@pytest.mark.asyncio
async def test_get_review_english(journal_service: JournalService, mock_db) -> None:
    """测试生成气候回顾 — 英文"""
    mock_row = MagicMock()
    mock_row.__getitem__ = lambda self, key: [5, 25.0, 28.0, 22.0, 15.0][key]
    mock_result = MagicMock()
    mock_result.one.return_value = mock_row
    mock_db.execute.return_value = mock_result

    result = await journal_service.get_review(mock_db, 1, 22.82, 108.32, "monthly", "en")

    assert result["language"] == "en"
    assert len(result["review"]) > 0


@pytest.mark.asyncio
async def test_get_review_empty(journal_service: JournalService, mock_db) -> None:
    """测试生成气候回顾 — 空数据"""
    mock_row = MagicMock()
    mock_row.__getitem__ = lambda self, key: [0, None, None, None, None][key]
    mock_result = MagicMock()
    mock_result.one.return_value = mock_row
    mock_db.execute.return_value = mock_result

    result = await journal_service.get_review(mock_db, 1, 22.82, 108.32, "monthly", "zh")

    assert result["stats"] is None
    assert "暂无" in result["message"]
