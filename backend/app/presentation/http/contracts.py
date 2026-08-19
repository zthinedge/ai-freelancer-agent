from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HttpContract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class HealthResponse(HttpContract):
    status: Literal["ok"]
    version: str
    environment: str
    architecture: Literal["modular-monolith"] = "modular-monolith"


class ErrorResponse(HttpContract):
    schema_version: Literal["1.0.0"] = "1.0.0"
    error_code: str
    message: str
    trace_id: str


class SubmitClarificationRequest(HttpContract):
    schema_version: Literal["1.0.0"] = "1.0.0"
    answers: dict[str, str] = Field(min_length=1)
