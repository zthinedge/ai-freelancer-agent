from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.agent.contracts import AgentState
from app.agent.schemas import Money, PositiveMoney
from app.domain.enums import AgentRunStatus, QuoteTier, ServiceType, WorkflowStep


class ApplicationContract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CreateProjectCommand(ApplicationContract):
    schema_version: Literal["1.0.0"] = "1.0.0"
    name: str = Field(min_length=2, max_length=100)
    client_request: str = Field(min_length=10, max_length=5000)
    service_type: ServiceType = ServiceType.AUTO_DETECT
    budget: Money | None = None
    deadline: str | None = Field(default=None, max_length=80)
    hourly_rate: PositiveMoney


class SubmitClarificationCommand(ApplicationContract):
    schema_version: Literal["1.0.0"] = "1.0.0"
    run_id: UUID
    answers: dict[str, str] = Field(min_length=1)


class ApproveQuoteCommand(ApplicationContract):
    schema_version: Literal["1.0.0"] = "1.0.0"
    run_id: UUID
    approved: bool
    selected_tier: QuoteTier | None = None
    note: str | None = Field(default=None, max_length=500)


class AgentRunView(ApplicationContract):
    schema_version: Literal["1.0.0"] = "1.0.0"
    id: UUID
    project_id: UUID
    status: AgentRunStatus
    current_step: WorkflowStep | None
    state: AgentState


class ProjectView(ApplicationContract):
    schema_version: Literal["1.0.0"] = "1.0.0"
    id: UUID
    name: str
    client_request: str
    service_type: ServiceType
    budget: Money | None = None
    deadline: str | None = None
    hourly_rate: PositiveMoney
    created_at: datetime
    updated_at: datetime
    run: AgentRunView | None = None
