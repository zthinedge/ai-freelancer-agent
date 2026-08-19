from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.agent.schemas import ContractModel, NonEmptyText, ProjectBrief, SchemaVersion
from app.domain.enums import WorkflowStep


class ExpectedFact(ContractModel):
    field: NonEmptyText
    value_contains: tuple[NonEmptyText, ...] = Field(min_length=1)


class RequiredQuestionExpectation(ContractModel):
    field: NonEmptyText
    intent: NonEmptyText


class ExpectedRoute(ContractModel):
    stop_after: WorkflowStep
    requires_human_input: bool


class PassCriteria(ContractModel):
    machine: tuple[NonEmptyText, ...] = Field(min_length=1)
    human: tuple[NonEmptyText, ...] = Field(min_length=1)
    minimum_score: Decimal = Field(ge=0, le=1, decimal_places=2)


class EvaluationCase(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    case_version: Literal["1.0.0"] = "1.0.0"
    case_id: str = Field(pattern=r"^EVAL-\d{3}$")
    title: NonEmptyText
    input: ProjectBrief
    expected_known_facts: tuple[ExpectedFact, ...] = Field(min_length=1)
    expected_missing_fields: tuple[NonEmptyText, ...]
    required_questions: tuple[RequiredQuestionExpectation, ...]
    forbidden_behaviors: tuple[NonEmptyText, ...] = Field(min_length=1)
    expected_route: ExpectedRoute
    pass_criteria: PassCriteria
    tags: tuple[NonEmptyText, ...] = Field(min_length=1)
