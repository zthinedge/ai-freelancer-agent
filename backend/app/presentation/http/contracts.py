from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import QuoteTier


class HttpContract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class HealthResponse(HttpContract):
    status: Literal["ok"]
    version: str
    environment: str
    architecture: Literal["modular-monolith"] = "modular-monolith"
    ai_mode: Literal["model", "rule_fallback"]
    ai_model: str
    memory_backend: Literal["sqlite"] = "sqlite"
    rag_enabled: bool
    mcp_enabled: bool


class ErrorResponse(HttpContract):
    schema_version: Literal["1.0.0"] = "1.0.0"
    error_code: str
    message: str
    trace_id: str


class SubmitClarificationRequest(HttpContract):
    schema_version: Literal["1.0.0"] = "1.0.0"
    answers: dict[str, str] = Field(min_length=1)


class ApproveQuoteRequest(HttpContract):
    schema_version: Literal["1.0.0"] = "1.0.0"
    approved: bool
    selected_tier: QuoteTier | None = None
    note: str | None = Field(default=None, max_length=500)
