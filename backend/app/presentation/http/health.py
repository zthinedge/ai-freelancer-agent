from fastapi import APIRouter, Request

from app.core.config import Settings

from .contracts import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    settings: Settings = request.app.state.settings
    return HealthResponse(
        status="ok",
        version=settings.version,
        environment=settings.environment,
        ai_mode="model" if settings.ai_is_configured else "rule_fallback",
        ai_model=settings.ai_model,
        rag_enabled=settings.rag_enabled,
        mcp_enabled=settings.mcp_enabled,
    )
