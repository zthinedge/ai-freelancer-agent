import json
from decimal import Decimal
from typing import TypeVar
from uuid import UUID

from pydantic import ValidationError

from app.agent.contracts import AgentState, ModelMessage, ModelRequest, ModelResponse
from app.agent.ports import IntakeAgent, ModelGateway
from app.agent.pricing import calculate_contingency_rate, calculate_pricing
from app.agent.prompts.clarification_planner import (
    PROMPT_VERSION as CLARIFICATION_PROMPT_VERSION,
)
from app.agent.prompts.clarification_planner import SYSTEM_PROMPT as CLARIFICATION_SYSTEM_PROMPT
from app.agent.prompts.proposal_writer import PROMPT_VERSION as PROPOSAL_PROMPT_VERSION
from app.agent.prompts.proposal_writer import SYSTEM_PROMPT as PROPOSAL_SYSTEM_PROMPT
from app.agent.prompts.requirement_intake import PROMPT_VERSION as INTAKE_PROMPT_VERSION
from app.agent.prompts.requirement_intake import SYSTEM_PROMPT as INTAKE_SYSTEM_PROMPT
from app.agent.prompts.risk_reviewer import PROMPT_VERSION as RISK_PROMPT_VERSION
from app.agent.prompts.risk_reviewer import SYSTEM_PROMPT as RISK_SYSTEM_PROMPT
from app.agent.prompts.scope_designer import PROMPT_VERSION as SCOPE_PROMPT_VERSION
from app.agent.prompts.scope_designer import SYSTEM_PROMPT as SCOPE_SYSTEM_PROMPT
from app.agent.prompts.task_estimator import PROMPT_VERSION as ESTIMATE_PROMPT_VERSION
from app.agent.prompts.task_estimator import SYSTEM_PROMPT as ESTIMATE_SYSTEM_PROMPT
from app.agent.schemas import (
    ClarificationPlannerInput,
    ClarificationPlannerOutput,
    ConfirmedFact,
    ContractModel,
    PricingToolInput,
    PricingToolOutput,
    ProjectBrief,
    ProposalWriterInput,
    ProposalWriterOutput,
    RequirementIntakeInput,
    RequirementIntakeOutput,
    RiskReviewerInput,
    RiskReviewerOutput,
    ScopeDesignerInput,
    ScopeDesignerOutput,
    TaskEstimatorInput,
    TaskEstimatorOutput,
)
from app.domain.enums import AgentRunStatus, FactSource, WorkflowStep

from .openai_compatible import ModelGatewayError

SkillOutputT = TypeVar("SkillOutputT", bound=ContractModel)


class ModelBackedIntakeAgent(IntakeAgent):
    def __init__(
        self,
        gateway: ModelGateway,
        fallback: IntakeAgent,
        model_name: str,
    ) -> None:
        self._gateway = gateway
        self._fallback = fallback
        self._model_name = model_name

    async def analyze(self, run_id: UUID, project_id: UUID, brief: ProjectBrief) -> AgentState:
        try:
            intake, intake_response = await self._run_intake(brief)
            clarification, clarification_response = await self._run_clarification(intake)
        except (ModelGatewayError, ValidationError):
            fallback_state = await self._fallback.analyze(run_id, project_id, brief)
            return fallback_state.model_copy(
                update={
                    "model_name": self._model_name,
                    "fallback_reason": "模型输出不可用，已自动切换到规则模式",
                }
            )

        system_facts = [
            ConfirmedFact(
                field="project_name",
                value=brief.name,
                source=FactSource.SYSTEM,
                evidence="用户在项目表单中填写的项目名称",
            ),
            ConfirmedFact(
                field="hourly_rate",
                value=f"{brief.hourly_rate.amount} {brief.hourly_rate.currency}",
                source=FactSource.SYSTEM,
                evidence="用户在项目表单中填写的接单时薪",
            ),
            ConfirmedFact(
                field="service_type",
                value=brief.service_type.value,
                source=FactSource.SYSTEM,
                evidence="用户在项目表单中选择的服务类型",
            ),
        ]
        if brief.budget is not None:
            system_facts.append(
                ConfirmedFact(
                    field="budget",
                    value=f"{brief.budget.amount} {brief.budget.currency}",
                    source=FactSource.CLIENT_REQUEST,
                    evidence="用户在项目表单中填写的预算",
                )
            )
        if brief.deadline:
            system_facts.append(
                ConfirmedFact(
                    field="deadline",
                    value=brief.deadline,
                    source=FactSource.CLIENT_REQUEST,
                    evidence="用户在项目表单中填写的期限",
                )
            )
        return AgentState(
            run_id=run_id,
            project_id=project_id,
            status=AgentRunStatus.WAITING_USER,
            current_step=WorkflowStep.CLARIFICATION,
            confirmed_facts=(*intake.confirmed_facts, *system_facts),
            pending_questions=clarification.questions,
            retrieved_context=brief.retrieved_context,
            intake=intake,
            clarification=clarification,
            execution_mode="model",
            model_name=clarification_response.model or intake_response.model or self._model_name,
            model_input_tokens=_sum_optional(
                intake_response.input_tokens,
                clarification_response.input_tokens,
            ),
            model_output_tokens=_sum_optional(
                intake_response.output_tokens,
                clarification_response.output_tokens,
            ),
            model_latency_ms=_sum_optional(
                intake_response.latency_ms,
                clarification_response.latency_ms,
            ),
        )

    async def submit_answers(self, state: AgentState, answers: dict[str, str]) -> AgentState:
        resolved_answers = _resolve_answers(state, answers)
        answer_facts = tuple(
            ConfirmedFact(
                field=field,
                value=value,
                source=FactSource.CLARIFICATION_ANSWER,
                evidence=f"用户回答：{value}",
            )
            for _, field, value in resolved_answers
        )
        confirmed_facts = (*state.confirmed_facts, *answer_facts)
        answer_map = {
            f"{field}::{question_id}": value
            for question_id, field, value in resolved_answers
        }

        active_skill = "scope_designer"
        failure_reason: str | None = None
        try:
            scope, scope_response = await self._run_scope(confirmed_facts, answer_map)
            if scope.blocked_by_missing_information:
                failure_reason = "需求仍缺少关键信息，已停止估算；请补充项目描述后新建分析"
                raise ValueError("scope is blocked by missing information")
            active_skill = "task_estimator"
            estimate, estimate_response = await self._run_estimate(
                scope,
                answer_map,
                _fact_value(confirmed_facts, "deadline"),
            )
            active_skill = "risk_reviewer"
            risk_review, risk_response = await self._run_risk_review(
                scope,
                estimate,
                confirmed_facts,
                answer_map,
            )
            active_skill = "pricing_calculator"
            pricing = _calculate_state_pricing(state, estimate, risk_review)
            active_skill = "proposal_writer"
            proposal, proposal_response = await self._run_proposal(
                _fact_value(confirmed_facts, "project_name") or "当前项目",
                scope,
                estimate,
                risk_review,
                pricing,
            )
        except (ModelGatewayError, ValidationError, ValueError):
            return state.model_copy(
                update={
                    "status": AgentRunStatus.FAILED,
                    "current_step": _workflow_step_for(active_skill),
                    "confirmed_facts": confirmed_facts,
                    "pending_questions": (),
                    "scope": None,
                    "estimate": None,
                    "risk_review": None,
                    "pricing": None,
                    "proposal": None,
                    "clarification_approved": True,
                    "quote_approved": False,
                    "selected_quote_tier": None,
                    "execution_mode": "model",
                    "model_name": state.model_name or self._model_name,
                    "fallback_reason": failure_reason
                    or f"{active_skill} 调用或校验失败，已停止自动报价；请稍后新建分析重试",
                }
            )

        responses = (scope_response, estimate_response, risk_response, proposal_response)
        return state.model_copy(
            update={
                "status": AgentRunStatus.WAITING_APPROVAL,
                "current_step": WorkflowStep.PROPOSAL,
                "confirmed_facts": confirmed_facts,
                "pending_questions": (),
                "scope": scope,
                "estimate": estimate,
                "risk_review": risk_review,
                "pricing": pricing,
                "proposal": proposal,
                "clarification_approved": True,
                "quote_approved": False,
                "execution_mode": "model",
                "model_name": proposal_response.model or state.model_name or self._model_name,
                "fallback_reason": None,
                "model_input_tokens": _sum_optional(
                    state.model_input_tokens,
                    *(response.input_tokens for response in responses),
                ),
                "model_output_tokens": _sum_optional(
                    state.model_output_tokens,
                    *(response.output_tokens for response in responses),
                ),
                "model_latency_ms": _sum_optional(
                    state.model_latency_ms,
                    *(response.latency_ms for response in responses),
                ),
            }
        )

    async def _run_scope(
        self,
        confirmed_facts: tuple[ConfirmedFact, ...],
        answers: dict[str, str],
    ) -> tuple[ScopeDesignerOutput, ModelResponse]:
        input_payload = ScopeDesignerInput(
            confirmed_facts=confirmed_facts,
            clarification_answers=answers,
        )
        return await self._run_validated_skill(
            SCOPE_SYSTEM_PROMPT,
            input_payload,
            ScopeDesignerOutput,
            SCOPE_PROMPT_VERSION,
        )

    async def _run_estimate(
        self,
        scope: ScopeDesignerOutput,
        answers: dict[str, str],
        deadline: str | None,
    ) -> tuple[TaskEstimatorOutput, ModelResponse]:
        acceptance_standards = tuple(
            value for key, value in answers.items() if key.startswith("acceptance::")
        ) or ("按Must范围逐项演示并完成交付验收",)
        input_payload = TaskEstimatorInput(
            scope=scope,
            acceptance_standards=acceptance_standards,
            deadline=deadline,
            external_constraints=tuple(
                value
                for key, value in answers.items()
                if any(marker in key for marker in ("owner", "deployment", "privacy", "data"))
            ),
        )
        return await self._run_validated_skill(
            ESTIMATE_SYSTEM_PROMPT,
            input_payload,
            TaskEstimatorOutput,
            ESTIMATE_PROMPT_VERSION,
        )

    async def _run_risk_review(
        self,
        scope: ScopeDesignerOutput,
        estimate: TaskEstimatorOutput,
        confirmed_facts: tuple[ConfirmedFact, ...],
        answers: dict[str, str],
    ) -> tuple[RiskReviewerOutput, ModelResponse]:
        constraint_fields = {"budget", "deadline", "privacy", "content_owner"}
        input_payload = RiskReviewerInput(
            scope=scope,
            estimate=estimate,
            client_constraints=tuple(
                fact.value for fact in confirmed_facts if fact.field in constraint_fields
            ),
            external_dependencies=tuple(
                value
                for key, value in answers.items()
                if any(marker in key for marker in ("owner", "deployment", "platform", "data"))
            ),
        )
        return await self._run_validated_skill(
            RISK_SYSTEM_PROMPT,
            input_payload,
            RiskReviewerOutput,
            RISK_PROMPT_VERSION,
        )

    async def _run_proposal(
        self,
        project_name: str,
        scope: ScopeDesignerOutput,
        estimate: TaskEstimatorOutput,
        risk_review: RiskReviewerOutput,
        pricing: PricingToolOutput,
    ) -> tuple[ProposalWriterOutput, ModelResponse]:
        input_payload = ProposalWriterInput(
            project_name=project_name,
            scope=scope,
            estimate=estimate,
            risk_review=risk_review,
            pricing=pricing,
        )
        return await self._run_validated_skill(
            PROPOSAL_SYSTEM_PROMPT,
            input_payload,
            ProposalWriterOutput,
            PROPOSAL_PROMPT_VERSION,
            forced_fields={
                "document_status": "ai_draft",
                "quote_options": pricing.model_dump(mode="json")["options"],
                "requires_human_approval": True,
            },
        )

    async def _run_validated_skill(
        self,
        system_prompt: str,
        input_payload: ContractModel,
        output_model: type[SkillOutputT],
        prompt_version: str,
        forced_fields: dict[str, object] | None = None,
    ) -> tuple[SkillOutputT, ModelResponse]:
        original_input = input_payload.model_dump(mode="json")
        repair_context: dict[str, object] | None = None
        responses: list[ModelResponse] = []
        last_validation_error: ValidationError | None = None

        for _ in range(2):
            user_payload: object = original_input
            if repair_context is not None:
                user_payload = {
                    "original_input": original_input,
                    "repair_request": repair_context,
                }
            response = await self._gateway.complete(
                ModelRequest(
                    messages=[
                        ModelMessage(role="system", content=system_prompt),
                        ModelMessage(
                            role="user",
                            content=json.dumps(user_payload, ensure_ascii=False),
                        ),
                    ],
                    output_schema=output_model.model_json_schema(),
                )
            )
            responses.append(response)
            payload = dict(response.content)
            payload.update(schema_version="1.0.0", prompt_version=prompt_version)
            if forced_fields:
                payload.update(forced_fields)
            try:
                output = output_model.model_validate(payload)
                return output, _aggregate_responses(responses)
            except ValidationError as error:
                last_validation_error = error
                repair_context = {
                    "previous_invalid_output": payload,
                    "validation_errors": [
                        {
                            "location": ".".join(str(part) for part in item["loc"]),
                            "message": item["msg"],
                            "type": item["type"],
                        }
                        for item in error.errors(include_url=False)
                    ],
                    "instruction": "只修复这些校验错误，保持其他有效内容不变并返回完整JSON",
                }

        if last_validation_error is None:
            raise RuntimeError("structured skill validation did not run")
        raise last_validation_error

    async def _run_intake(
        self,
        brief: ProjectBrief,
    ) -> tuple[RequirementIntakeOutput, ModelResponse]:
        input_payload = RequirementIntakeInput.model_validate(brief.model_dump(mode="python"))
        response = await self._gateway.complete(
            ModelRequest(
                messages=[
                    ModelMessage(role="system", content=INTAKE_SYSTEM_PROMPT),
                    ModelMessage(
                        role="user",
                        content=json.dumps(
                            input_payload.model_dump(mode="json"), ensure_ascii=False
                        ),
                    ),
                ],
                output_schema=RequirementIntakeOutput.model_json_schema(),
            )
        )
        payload = dict(response.content)
        payload.update(schema_version="1.0.0", prompt_version=INTAKE_PROMPT_VERSION)
        return RequirementIntakeOutput.model_validate(payload), response

    async def _run_clarification(
        self,
        intake: RequirementIntakeOutput,
    ) -> tuple[ClarificationPlannerOutput, ModelResponse]:
        input_payload = ClarificationPlannerInput(
            project_type=intake.project_type,
            confirmed_facts=intake.confirmed_facts,
            missing_fields=intake.missing_fields,
        )
        response = await self._gateway.complete(
            ModelRequest(
                messages=[
                    ModelMessage(role="system", content=CLARIFICATION_SYSTEM_PROMPT),
                    ModelMessage(
                        role="user",
                        content=json.dumps(
                            input_payload.model_dump(mode="json"), ensure_ascii=False
                        ),
                    ),
                ],
                output_schema=ClarificationPlannerOutput.model_json_schema(),
            )
        )
        payload = dict(response.content)
        payload.update(schema_version="1.0.0", prompt_version=CLARIFICATION_PROMPT_VERSION)
        return ClarificationPlannerOutput.model_validate(payload), response


def _sum_optional(*values: int | None) -> int | None:
    present = [value for value in values if value is not None]
    return sum(present) if present else None


def _workflow_step_for(skill_name: str) -> WorkflowStep:
    return {
        "scope_designer": WorkflowStep.SCOPE,
        "task_estimator": WorkflowStep.ESTIMATION,
        "risk_reviewer": WorkflowStep.RISK,
        "pricing_calculator": WorkflowStep.PRICING,
        "proposal_writer": WorkflowStep.PROPOSAL,
    }[skill_name]


def _aggregate_responses(responses: list[ModelResponse]) -> ModelResponse:
    latest = responses[-1]
    return ModelResponse(
        content=latest.content,
        model=latest.model,
        input_tokens=_sum_optional(*(response.input_tokens for response in responses)),
        output_tokens=_sum_optional(*(response.output_tokens for response in responses)),
        latency_ms=_sum_optional(*(response.latency_ms for response in responses)),
    )


def _resolve_answers(
    state: AgentState,
    answers: dict[str, str],
) -> tuple[tuple[str, str, str], ...]:
    resolved: list[tuple[str, str, str]] = []
    for question in state.pending_questions:
        value = answers.get(question.question_id, answers.get(question.field, "")).strip()
        if value:
            resolved.append((question.question_id, question.field, value))
    if resolved:
        return tuple(resolved)
    return tuple((key, key, value.strip()) for key, value in answers.items() if value.strip())


def _fact_value(facts: tuple[ConfirmedFact, ...], field: str) -> str | None:
    return next((fact.value for fact in facts if fact.field == field), None)


def _hourly_rate(state: AgentState) -> Decimal:
    raw = _fact_value(state.confirmed_facts, "hourly_rate")
    if raw is None:
        return Decimal("150.00")
    try:
        return Decimal(raw.split()[0])
    except (IndexError, ArithmeticError):
        return Decimal("150.00")


def _calculate_state_pricing(
    state: AgentState,
    estimate: TaskEstimatorOutput,
    risk_review: RiskReviewerOutput,
) -> PricingToolOutput:
    min_hours = sum((task.min_hours for task in estimate.tasks), Decimal("0"))
    max_hours = (
        sum((task.max_hours for task in estimate.tasks), Decimal("0"))
        + estimate.buffer_hours
    )
    return calculate_pricing(
        PricingToolInput(
            min_hours=min_hours,
            max_hours=max_hours,
            hourly_rate={"amount": _hourly_rate(state), "currency": "CNY"},
            contingency_rate=calculate_contingency_rate(
                risk_review,
                len(estimate.uncertainty_notes),
            ),
        )
    )
