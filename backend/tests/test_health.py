import pytest
from app.bootstrap.app_factory import create_app
from app.core.config import Settings
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_health_exposes_architecture_baseline():
    settings = Settings(environment="test", cors_origins=[])
    transport = ASGITransport(app=create_app(settings))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "0.2.0",
        "environment": "test",
        "architecture": "modular-monolith",
    }
