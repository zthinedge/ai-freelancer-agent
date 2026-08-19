from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.bootstrap.container import ApplicationContainer, build_container
from app.core.config import Settings, get_settings
from app.core.errors import ResourceNotFoundError
from app.presentation.http.contracts import ErrorResponse
from app.presentation.http.router import api_router


def create_app(
    settings: Settings | None = None,
    container: ApplicationContainer | None = None,
) -> FastAPI:
    runtime_settings = settings or get_settings()
    application = FastAPI(
        title=runtime_settings.name,
        description="AI Native自由职业接单助手的模块化单体API。",
        version=runtime_settings.version,
    )
    application.state.settings = runtime_settings
    application.state.container = container or build_container()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=runtime_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(ResourceNotFoundError)
    async def handle_not_found(request: Request, error: ResourceNotFoundError) -> JSONResponse:
        response = ErrorResponse(
            error_code="resource_not_found",
            message=str(error),
            trace_id=request.headers.get("x-trace-id", "not-provided"),
        )
        return JSONResponse(status_code=404, content=response.model_dump(mode="json"))

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
    return application
