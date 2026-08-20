import pytest
from app.bootstrap.app_factory import create_app
from app.core.config import Settings


@pytest.fixture()
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def app(tmp_path):
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    return create_app(
        Settings(
            environment="test",
            cors_origins=[],
            ai_api_key=None,
            database_url=database_url,
            mcp_enabled=False,
        )
    )
