from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.domain.enums import FactSource, QuestionPriority, QuoteTier, RiskSeverity, ServiceType

SchemaVersion = Literal["1.0.0"]
PromptVersion = Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
SkillVersion = Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Hours = Annotated[
    Decimal,
    Field(ge=Decimal("0"), max_digits=7, decimal_places=1, multiple_of=Decimal("0.5")),
]
PositiveHours = Annotated[
    Decimal,
    Field(gt=Decimal("0"), max_digits=7, decimal_places=1, multiple_of=Decimal("0.5")),
]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class Money(ContractModel):
    amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    currency: Literal["CNY"] = "CNY"


class PositiveMoney(Money):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class RetrievedContext(ContractModel):
    source_id: NonEmptyText
    title: NonEmptyText
    excerpt: str = Field(min_length=1, max_length=1200)
    score: float = Field(ge=0, le=1)


class ProjectBrief(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    name: str = Field(min_length=2, max_length=100)
    client_request: str = Field(min_length=10, max_length=5000)
    service_type: ServiceType = ServiceType.AUTO_DETECT
    budget: Money | None = None
    deadline: str | None = Field(default=None, max_length=80)
    hourly_rate: PositiveMoney
    retrieved_context: tuple[RetrievedContext, ...] = Field(default=(), max_length=5)


class ConfirmedFact(ContractModel):
    field: NonEmptyText
    value: NonEmptyText
    source: FactSource
    evidence: NonEmptyText


class UncertainAssumption(ContractModel):
    field: NonEmptyText
    proposed_value: NonEmptyText
    reason: NonEmptyText


class RequirementIntakeInput(ProjectBrief):
    pass


class RequirementIntakeOutput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    prompt_version: PromptVersion
    project_type: ServiceType
    goals: tuple[NonEmptyText, ...] = Field(min_length=1)
    target_users: tuple[NonEmptyText, ...] = ()
    confirmed_facts: tuple[ConfirmedFact, ...] = Field(min_length=1)
    missing_fields: tuple[NonEmptyText, ...]
    assumptions: tuple[UncertainAssumption, ...] = ()


class ClarificationPlannerInput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    project_type: ServiceType
    confirmed_facts: tuple[ConfirmedFact, ...]
    missing_fields: tuple[NonEmptyText, ...] = Field(min_length=1)
    client_constraints: tuple[NonEmptyText, ...] = ()


class ClarificationQuestion(ContractModel):
    question_id: NonEmptyText
    field: NonEmptyText
    question: NonEmptyText
    reason: NonEmptyText
    priority: QuestionPriority


class ClarificationPlannerOutput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    prompt_version: PromptVersion
    questions: tuple[ClarificationQuestion, ...] = Field(min_length=3, max_length=6)
    requires_human_input: Literal[True] = True


class ScopeDesignerInput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    confirmed_facts: tuple[ConfirmedFact, ...] = Field(min_length=1)
    clarification_answers: dict[str, NonEmptyText] = Field(min_length=1)


class ScopeItem(ContractModel):
    item_id: NonEmptyText
    title: NonEmptyText
    description: NonEmptyText
    rationale: NonEmptyText


class ScopeDesignerOutput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    prompt_version: PromptVersion
    must: tuple[ScopeItem, ...] = Field(min_length=1)
    should: tuple[ScopeItem, ...] = ()
    could: tuple[ScopeItem, ...] = ()
    wont: tuple[ScopeItem, ...] = Field(min_length=2)
    blocked_by_missing_information: bool = False


class TaskEstimatorInput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    scope: ScopeDesignerOutput
    acceptance_standards: tuple[NonEmptyText, ...] = Field(min_length=1)
    deadline: str | None = Field(default=None, max_length=80)
    external_constraints: tuple[NonEmptyText, ...] = ()


class EstimatedTask(ContractModel):
    task_id: NonEmptyText
    title: NonEmptyText
    description: NonEmptyText
    dependencies: tuple[NonEmptyText, ...] = ()
    min_hours: PositiveHours
    max_hours: PositiveHours
    estimate_basis: NonEmptyText
    acceptance_criteria: tuple[NonEmptyText, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_hour_range(self) -> "EstimatedTask":
        if self.max_hours < self.min_hours:
            raise ValueError("max_hours must be greater than or equal to min_hours")
        return self


class TaskEstimatorOutput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    prompt_version: PromptVersion
    tasks: tuple[EstimatedTask, ...] = Field(min_length=3, max_length=12)
    buffer_hours: Hours
    uncertainty_notes: tuple[NonEmptyText, ...] = Field(default=(), max_length=8)


class RiskReviewerInput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    scope: ScopeDesignerOutput
    estimate: TaskEstimatorOutput
    client_constraints: tuple[NonEmptyText, ...] = ()
    external_dependencies: tuple[NonEmptyText, ...] = ()


class RiskItem(ContractModel):
    risk_id: NonEmptyText
    category: Literal["requirement", "technical", "schedule", "privacy", "commercial"]
    severity: RiskSeverity
    cause: NonEmptyText
    impact: NonEmptyText
    mitigation: NonEmptyText
    requires_human_decision: bool


class RiskReviewerOutput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    prompt_version: PromptVersion
    risks: tuple[RiskItem, ...] = Field(max_length=10)
    human_decisions: tuple[NonEmptyText, ...] = Field(default=(), max_length=10)


class PricingToolInput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    min_hours: PositiveHours
    max_hours: PositiveHours
    hourly_rate: PositiveMoney
    contingency_rate: Decimal = Field(ge=0, le=Decimal("0.5"), decimal_places=2)


class QuoteOption(ContractModel):
    tier: QuoteTier
    amount: Money
    included_hours: PositiveHours
    calculation_summary: NonEmptyText


class PricingToolOutput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    policy_version: PromptVersion
    options: tuple[QuoteOption, QuoteOption, QuoteOption]

    @model_validator(mode="after")
    def validate_tiers(self) -> "PricingToolOutput":
        actual = {option.tier for option in self.options}
        expected = {QuoteTier.BASIC, QuoteTier.STANDARD, QuoteTier.PREMIUM}
        if actual != expected:
            raise ValueError("pricing options must contain basic, standard, and premium once each")
        return self


class ProposalWriterInput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    project_name: NonEmptyText
    scope: ScopeDesignerOutput
    estimate: TaskEstimatorOutput
    risk_review: RiskReviewerOutput
    pricing: PricingToolOutput


class ProposalWriterOutput(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    prompt_version: PromptVersion
    document_status: Literal["ai_draft"] = "ai_draft"
    project_summary: NonEmptyText
    deliverables: tuple[NonEmptyText, ...] = Field(min_length=1)
    exclusions: tuple[NonEmptyText, ...] = Field(min_length=2)
    acceptance_criteria: tuple[NonEmptyText, ...] = Field(min_length=1)
    quote_options: tuple[QuoteOption, QuoteOption, QuoteOption]
    disclaimers: tuple[NonEmptyText, ...] = Field(min_length=1)
    requires_human_approval: Literal[True] = True


SkillInput = (
    RequirementIntakeInput
    | ClarificationPlannerInput
    | ScopeDesignerInput
    | TaskEstimatorInput
    | RiskReviewerInput
    | ProposalWriterInput
)
SkillOutput = (
    RequirementIntakeOutput
    | ClarificationPlannerOutput
    | ScopeDesignerOutput
    | TaskEstimatorOutput
    | RiskReviewerOutput
    | ProposalWriterOutput
)
