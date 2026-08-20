from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field

from app.domain.enums import AgentRunStatus, QuoteTier, WorkflowStep

from .schemas import (
    ClarificationPlannerInput,
    ClarificationPlannerOutput,
    ClarificationQuestion,
    ConfirmedFact,
    ContractModel,
    PricingToolInput,
    PricingToolOutput,
    ProposalWriterInput,
    ProposalWriterOutput,
    RequirementIntakeInput,
    RequirementIntakeOutput,
    RetrievedContext,
    RiskReviewerInput,
    RiskReviewerOutput,
    ScopeDesignerInput,
    ScopeDesignerOutput,
    TaskEstimatorInput,
    TaskEstimatorOutput,
)


class AgentState(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    run_id: UUID
    project_id: UUID
    status: AgentRunStatus
    current_step: WorkflowStep | None = None
    confirmed_facts: tuple[ConfirmedFact, ...] = ()
    pending_questions: tuple[ClarificationQuestion, ...] = ()
    intake: RequirementIntakeOutput | None = None
    clarification: ClarificationPlannerOutput | None = None
    scope: ScopeDesignerOutput | None = None
    estimate: TaskEstimatorOutput | None = None
    risk_review: RiskReviewerOutput | None = None
    pricing: PricingToolOutput | None = None
    proposal: ProposalWriterOutput | None = None
    clarification_approved: bool = False
    quote_approved: bool = False
    selected_quote_tier: QuoteTier | None = None
    retrieved_context: tuple[RetrievedContext, ...] = ()
    execution_mode: Literal["model", "rule_fallback"] = "rule_fallback"
    model_name: str | None = None
    fallback_reason: str | None = None
    model_input_tokens: int | None = Field(default=None, ge=0)
    model_output_tokens: int | None = Field(default=None, ge=0)
    model_latency_ms: int | None = Field(default=None, ge=0)


class SkillRequestBase(ContractModel):
    run_id: UUID
    state: AgentState


class RequirementIntakeRequest(SkillRequestBase):
    skill_name: Literal["requirement_intake"]
    input_payload: RequirementIntakeInput


class ClarificationPlannerRequest(SkillRequestBase):
    skill_name: Literal["clarification_planner"]
    input_payload: ClarificationPlannerInput


class ScopeDesignerRequest(SkillRequestBase):
    skill_name: Literal["scope_designer"]
    input_payload: ScopeDesignerInput


class TaskEstimatorRequest(SkillRequestBase):
    skill_name: Literal["task_estimator"]
    input_payload: TaskEstimatorInput


class RiskReviewerRequest(SkillRequestBase):
    skill_name: Literal["risk_reviewer"]
    input_payload: RiskReviewerInput


class ProposalWriterRequest(SkillRequestBase):
    skill_name: Literal["proposal_writer"]
    input_payload: ProposalWriterInput


SkillRequest = Annotated[
    RequirementIntakeRequest
    | ClarificationPlannerRequest
    | ScopeDesignerRequest
    | TaskEstimatorRequest
    | RiskReviewerRequest
    | ProposalWriterRequest,
    Field(discriminator="skill_name"),
]


class SkillResult(ContractModel):
    skill_name: Literal[
        "requirement_intake",
        "clarification_planner",
        "scope_designer",
        "task_estimator",
        "risk_reviewer",
        "proposal_writer",
    ]
    skill_version: str
    prompt_version: str
    output: (
        RequirementIntakeOutput
        | ClarificationPlannerOutput
        | ScopeDesignerOutput
        | TaskEstimatorOutput
        | RiskReviewerOutput
        | ProposalWriterOutput
    )
    next_step: WorkflowStep | None = None
    requires_human_input: bool = False


class ModelMessage(ContractModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ModelRequest(ContractModel):
    messages: list[ModelMessage]
    output_schema: dict[str, object]
    temperature: float = 0.0


class ModelResponse(ContractModel):
    content: dict[str, object]
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = Field(default=None, ge=0)


class ToolRequest(ContractModel):
    tool_name: Literal["pricing_calculator"]
    arguments: PricingToolInput
    idempotency_key: str


class ToolResult(ContractModel):
    tool_name: Literal["pricing_calculator"]
    output: PricingToolOutput
