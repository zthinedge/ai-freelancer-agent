from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import AgentRunStatus, WorkflowStep


class CreateProjectCommand(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    client_request: str = Field(min_length=10, max_length=5000)
    service_type: str = Field(default="自动识别", max_length=40)
    budget: Decimal | None = Field(default=None, ge=0)
    deadline: str | None = Field(default=None, max_length=40)
    hourly_rate: Decimal = Field(gt=0)


class SubmitClarificationCommand(BaseModel):
    run_id: UUID
    answers: dict[str, str] = Field(min_length=1)


class ApproveQuoteCommand(BaseModel):
    run_id: UUID
    approved: bool
    note: str | None = Field(default=None, max_length=500)


class AgentRunView(BaseModel):
    id: UUID
    project_id: UUID
    status: AgentRunStatus
    current_step: WorkflowStep | None
    state: dict[str, Any]


class ProjectView(BaseModel):
    id: UUID
    name: str
    run: AgentRunView | None = None
