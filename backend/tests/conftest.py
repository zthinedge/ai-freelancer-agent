import pytest
from app.bootstrap.app_factory import create_app
from app.core.config import Settings


@pytest.fixture()
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def app():
    return create_app(Settings(environment="test", cors_origins=[]))
