from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.bootstrap.container import ApplicationContainer, build_container
from app.core.config import Settings, get_settings
from app.core.errors import ConflictError, ResourceNotFoundError
from app.infrastructure.mcp import build_mcp_server
from app.presentation.http.contracts import ErrorResponse
from app.presentation.http.router import api_router


def create_app(
    settings: Settings | None = None,
    container: ApplicationContainer | None = None,
) -> FastAPI:
    runtime_settings = settings or get_settings()
    runtime_container = container or build_container(runtime_settings)
    mcp_server = None
    mcp_application = None
    if runtime_settings.mcp_enabled:
        mcp_server = build_mcp_server(
            runtime_container.project_store,
            runtime_container.context_memory,
        )
        mcp_application = mcp_server.streamable_http_app(
            streamable_http_path="/",
            stateless_http=True,
            json_response=True,
        )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if mcp_server is None:
            yield
            return
        async with mcp_server.session_manager.run():
            yield

    application = FastAPI(
        title=runtime_settings.name,
        description="AI Native自由职业接单助手的模块化单体API。",
        version=runtime_settings.version,
        lifespan=lifespan,
    )
    application.state.settings = runtime_settings
    application.state.container = runtime_container
    application.state.mcp_server = mcp_server
    application.add_middleware(
        CORSMiddleware,
        allow_origins=runtime_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Mcp-Session-Id"],
    )

    @application.exception_handler(ResourceNotFoundError)
    async def handle_not_found(request: Request, error: ResourceNotFoundError) -> JSONResponse:
        response = ErrorResponse(
            error_code="resource_not_found",
            message=str(error),
            trace_id=request.headers.get("x-trace-id", "not-provided"),
        )
        return JSONResponse(status_code=404, content=response.model_dump(mode="json"))

    @application.exception_handler(ConflictError)
    async def handle_conflict(request: Request, error: ConflictError) -> JSONResponse:
        response = ErrorResponse(
            error_code="invalid_state",
            message=str(error),
            trace_id=request.headers.get("x-trace-id", "not-provided"),
        )
        return JSONResponse(status_code=409, content=response.model_dump(mode="json"))

    @application.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        first_error = error.errors()[0]
        location = ".".join(str(part) for part in first_error["loc"])
        response = ErrorResponse(
            error_code="invalid_request",
            message=f"请求参数校验失败：{location} {first_error['msg']}",
            trace_id=request.headers.get("x-trace-id", "not-provided"),
        )
        return JSONResponse(status_code=422, content=response.model_dump(mode="json"))

    application.include_router(api_router)
    if mcp_application is not None:
        application.mount("/mcp", mcp_application)
    return application
