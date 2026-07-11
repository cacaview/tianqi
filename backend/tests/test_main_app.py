"""
主应用测试 — lifespan 和根端点
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """测试根路径"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "name" in data
    assert "version" in data
    assert "slogan" in data
    assert "supported_languages" in data
    assert "zh" in data["supported_languages"]


@pytest.mark.asyncio
async def test_health_endpoint():
    """测试健康检查端点"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_lifespan():
    """测试应用生命周期 — 导入检查"""
    from app.main import lifespan, app

    # lifespan 存在
    assert lifespan is not None
    assert app is not None
