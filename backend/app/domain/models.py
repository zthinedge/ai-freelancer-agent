from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from .enums import AgentRunStatus, SkillExecutionStatus, WorkflowStep


@dataclass(frozen=True, slots=True)
class Project:
    id: UUID
    name: str
    client_request: str
    service_type: str
    budget: Decimal | None
    deadline: str | None
    hourly_rate: Decimal
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class AgentRun:
    id: UUID
    project_id: UUID
    status: AgentRunStatus
    current_step: WorkflowStep | None
    state_snapshot: Mapping[str, object] = field(default_factory=dict)
    model_name: str | None = None
    total_tokens: int | None = None
    estimated_cost: Decimal | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class SkillExecution:
    id: UUID
    run_id: UUID
    skill_name: str
    skill_version: str
    status: SkillExecutionStatus
    input_summary: Mapping[str, object] = field(default_factory=dict)
    output: Mapping[str, object] = field(default_factory=dict)
    duration_ms: int | None = None
    error_code: str | None = None
