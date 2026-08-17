from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings, get_settings
from app.presentation.http.router import api_router


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime_settings = settings or get_settings()
    application = FastAPI(
        title=runtime_settings.name,
        description="AI Native自由职业接单助手的模块化单体API。",
        version=runtime_settings.version,
    )
    application.state.settings = runtime_settings
    application.add_middleware(
        CORSMiddleware,
        allow_origins=runtime_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)
    return application
