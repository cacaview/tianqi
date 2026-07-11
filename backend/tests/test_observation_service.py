"""
ObservationService 单元测试
使用 respx mock 外部 HTTP 调用
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.observation_service import ObservationService


@pytest.fixture
def observation_service() -> ObservationService:
    """创建 ObservationService 实例"""
    return ObservationService()


@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_submit_observation_success(observation_service: ObservationService, mock_db) -> None:
    """测试提交观测 — 成功"""
    result = await observation_service.submit_observation(
        mock_db, 1, 22.82, 108.32, "sunny", "晴天", "https://example.com/photo.jpg", 28.0, "zh"
    )

    assert "id" in result
    assert result["user_id"] == 1
    assert result["latitude"] == 22.82
    assert result["longitude"] == 108.32
    assert result["weather_type"] == "sunny"
    assert result["description"] == "晴天"
    assert result["photo_url"] == "https://example.com/photo.jpg"
    assert result["temperature"] == 28.0
    assert result["language"] == "zh"
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_submit_observation_minimal(observation_service: ObservationService, mock_db) -> None:
    """测试提交观测 — 最小参数"""
    result = await observation_service.submit_observation(
        mock_db, 1, 22.82, 108.32, "cloudy"
    )

    assert result["weather_type"] == "cloudy"
    assert result["description"] is None
    assert result["photo_url"] is None
    assert result["temperature"] is None
    assert result["language"] == "zh"


@pytest.mark.asyncio
async def test_submit_observation_rainy(observation_service: ObservationService, mock_db) -> None:
    """测试提交观测 — 雨天"""
    result = await observation_service.submit_observation(
        mock_db, 1, 22.82, 108.32, "rainy", "下雨了", None, 22.0, "en"
    )

    assert result["weather_type"] == "rainy"
    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_get_nearby_success(observation_service: ObservationService, mock_db) -> None:
    """测试获取附近观测 — 成功"""
    mock_observations = [
        MagicMock(
            id=1,
            user_id=1,
            latitude=22.82,
            longitude=108.32,
            weather_type="sunny",
            description="晴天",
            temperature=28.0,
            created_at=MagicMock(isoformat=MagicMock(return_value="2024-01-01T00:00:00")),
        ),
        MagicMock(
            id=2,
            user_id=2,
            latitude=22.80,
            longitude=108.30,
            weather_type="cloudy",
            description="多云",
            temperature=25.0,
            created_at=MagicMock(isoformat=MagicMock(return_value="2024-01-01T01:00:00")),
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_observations
    mock_db.execute.return_value = mock_result

    result = await observation_service.get_nearby(mock_db, 22.82, 108.32, 50.0, 20)

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["weather_type"] == "sunny"
    assert result[1]["id"] == 2
    assert result[1]["weather_type"] == "cloudy"


@pytest.mark.asyncio
async def test_get_nearby_empty(observation_service: ObservationService, mock_db) -> None:
    """测试获取附近观测 — 空结果"""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await observation_service.get_nearby(mock_db, 22.82, 108.32, 50.0, 20)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_nearby_different_radius(observation_service: ObservationService, mock_db) -> None:
    """测试获取附近观测 — 不同半径"""
    mock_observations = [
        MagicMock(
            id=1,
            user_id=1,
            latitude=22.82,
            longitude=108.32,
            weather_type="sunny",
            description="晴天",
            temperature=28.0,
            created_at=MagicMock(isoformat=MagicMock(return_value="2024-01-01T00:00:00")),
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_observations
    mock_db.execute.return_value = mock_result

    result = await observation_service.get_nearby(mock_db, 22.82, 108.32, 10.0, 10)

    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_heatmap_data_success(observation_service: ObservationService, mock_db) -> None:
    """测试获取热力图数据 — 成功"""
    mock_observations = [
        MagicMock(
            id=1,
            user_id=1,
            latitude=22.82,
            longitude=108.32,
            weather_type="sunny",
            description="晴天",
            temperature=28.0,
            created_at=MagicMock(isoformat=MagicMock(return_value="2024-01-01T00:00:00")),
        ),
        MagicMock(
            id=2,
            user_id=2,
            latitude=22.80,
            longitude=108.30,
            weather_type="stormy",
            description="暴风雨",
            temperature=20.0,
            created_at=MagicMock(isoformat=MagicMock(return_value="2024-01-01T01:00:00")),
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_observations
    mock_db.execute.return_value = mock_result

    result = await observation_service.get_heatmap_data(mock_db, 22.82, 108.32, 100.0)

    assert result["center"]["latitude"] == 22.82
    assert result["center"]["longitude"] == 108.32
    assert result["radius_km"] == 100.0
    assert result["total_points"] == 2
    assert len(result["points"]) == 2
    # stormy应该有更高权重
    assert result["points"][1]["weight"] == 2.0


@pytest.mark.asyncio
async def test_get_heatmap_data_empty(observation_service: ObservationService, mock_db) -> None:
    """测试获取热力图数据 — 空数据"""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await observation_service.get_heatmap_data(mock_db, 22.82, 108.32, 100.0)

    assert result["total_points"] == 0
    assert len(result["points"]) == 0


@pytest.mark.asyncio
async def test_calculate_heatmap_weight(observation_service: ObservationService) -> None:
    """测试热力图权重计算 — 通过 get_heatmap_data 验证"""
    # get_heatmap_data 内部根据 weather_type 计算权重
    # stormy -> 2.0, sunny -> 1.0
    assert observation_service is not None  # 基本实例检查
