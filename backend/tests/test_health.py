import pytest
from app.bootstrap.app_factory import create_app
from app.core.config import Settings
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_health_exposes_architecture_baseline(tmp_path):
    settings = Settings(
        environment="test",
        version="0.5.0",
        cors_origins=[],
        ai_api_key=None,
        database_url=f"sqlite:///{(tmp_path / 'health.db').as_posix()}",
        mcp_enabled=False,
    )
    transport = ASGITransport(app=create_app(settings))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "0.5.0",
        "environment": "test",
        "architecture": "modular-monolith",
        "ai_mode": "rule_fallback",
        "ai_model": "deepseek-v4-flash",
        "memory_backend": "sqlite",
        "rag_enabled": True,
        "mcp_enabled": False,
    }


@pytest.mark.anyio
async def test_health_reports_model_mode_without_exposing_api_key(tmp_path):
    settings = Settings(
        environment="test",
        cors_origins=[],
        ai_api_key="super-secret",
        ai_model="deepseek-v4-pro",
        database_url=f"sqlite:///{(tmp_path / 'model-health.db').as_posix()}",
        mcp_enabled=False,
    )
    transport = ASGITransport(app=create_app(settings))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["ai_mode"] == "model"
    assert response.json()["ai_model"] == "deepseek-v4-pro"
    assert "secret" not in response.text
