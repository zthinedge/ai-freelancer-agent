from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import AgentRunStatus, WorkflowStep


class AgentState(BaseModel):
    run_id: UUID
    project_id: UUID
    status: AgentRunStatus
    current_step: WorkflowStep | None = None
    confirmed_facts: dict[str, Any] = Field(default_factory=dict)
    pending_questions: list[str] = Field(default_factory=list)
    skill_outputs: dict[str, dict[str, Any]] = Field(default_factory=dict)
    approvals: dict[str, bool] = Field(default_factory=dict)


class SkillRequest(BaseModel):
    run_id: UUID
    skill_name: str
    state: AgentState
    input_payload: dict[str, Any] = Field(default_factory=dict)


class SkillResult(BaseModel):
    skill_name: str
    skill_version: str
    output: dict[str, Any]
    next_step: WorkflowStep | None = None
    requires_human_input: bool = False


class ModelMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ModelRequest(BaseModel):
    messages: list[ModelMessage]
    output_schema: dict[str, Any]
    temperature: float = 0.0


class ModelResponse(BaseModel):
    content: dict[str, Any]
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class ToolRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    idempotency_key: str


class ToolResult(BaseModel):
    tool_name: str
    output: dict[str, Any]
