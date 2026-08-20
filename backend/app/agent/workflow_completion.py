from decimal import ROUND_HALF_UP, Decimal

from app.agent.contracts import AgentState
from app.agent.pricing import calculate_contingency_rate, calculate_pricing
from app.agent.schemas import (
    ConfirmedFact,
    EstimatedTask,
    PricingToolInput,
    PricingToolOutput,
    ProposalWriterOutput,
    RiskItem,
    RiskReviewerOutput,
    ScopeDesignerOutput,
    ScopeItem,
    TaskEstimatorOutput,
)
from app.domain.enums import (
    AgentRunStatus,
    FactSource,
    RiskSeverity,
    ServiceType,
    WorkflowStep,
)

_HALF_HOUR = Decimal("0.5")
_DEFAULT_RATE = Decimal("150.00")
_BASE_HOURS: dict[ServiceType, tuple[Decimal, Decimal]] = {
    ServiceType.AUTO_DETECT: (Decimal("20"), Decimal("32")),
    ServiceType.WEBSITE: (Decimal("32"), Decimal("52")),
    ServiceType.AI_APPLICATION: (Decimal("40"), Decimal("68")),
    ServiceType.ECOMMERCE: (Decimal("48"), Decimal("80")),
    ServiceType.PRESENTATION: (Decimal("12"), Decimal("22")),
    ServiceType.CONTENT: (Decimal("14"), Decimal("26")),
    ServiceType.DESIGN: (Decimal("20"), Decimal("36")),
    ServiceType.DATA_ANALYSIS: (Decimal("28"), Decimal("48")),
    ServiceType.VIDEO: (Decimal("24"), Decimal("44")),
    ServiceType.OTHER: (Decimal("24"), Decimal("40")),
}


def complete_clarification_workflow(
    state: AgentState,
    answers: dict[str, str],
) -> AgentState:
    """把澄清节点推进到可人工确认的确定性报价草案。"""
    resolved_answers = _resolve_answers(state, answers)
    answer_facts = tuple(
        ConfirmedFact(
            field=field,
            value=value,
            source=FactSource.CLARIFICATION_ANSWER,
            evidence=f"用户回答：{value}",
        )
        for field, value in resolved_answers
    )
    all_facts = (*state.confirmed_facts, *answer_facts)
    scope = _build_scope(state, resolved_answers)
    estimate = _build_estimate(state, resolved_answers)
    risk_review = _build_risk_review(state)
    pricing = _build_pricing(state, estimate, risk_review)
    proposal = _build_proposal(state, scope, estimate, risk_review, pricing)
    return state.model_copy(
        update={
            "status": AgentRunStatus.WAITING_APPROVAL,
            "current_step": WorkflowStep.PROPOSAL,
            "confirmed_facts": all_facts,
            "pending_questions": (),
            "scope": scope,
            "estimate": estimate,
            "risk_review": risk_review,
            "pricing": pricing,
            "proposal": proposal,
            "clarification_approved": True,
            "quote_approved": False,
        }
    )


def _resolve_answers(state: AgentState, answers: dict[str, str]) -> tuple[tuple[str, str], ...]:
    resolved: list[tuple[str, str]] = []
    for question in state.pending_questions:
        value = answers.get(question.question_id, answers.get(question.field, "")).strip()
        if value:
            resolved.append((question.field, value))
    if resolved:
        return tuple(resolved)
    return tuple((field, value.strip()) for field, value in answers.items() if value.strip())


def _build_scope(
    state: AgentState,
    answers: tuple[tuple[str, str], ...],
) -> ScopeDesignerOutput:
    goal = _fact_value(state, "client_goal") or "完成客户已描述的核心交付目标"
    must = [
        ScopeItem(
            item_id="SCOPE-MUST-01",
            title="核心成果交付",
            description=goal,
            rationale="来自客户原始需求与需求提取结果",
        )
    ]
    for index, (field, value) in enumerate(answers, 2):
        must.append(
            ScopeItem(
                item_id=f"SCOPE-MUST-{index:02d}",
                title=_humanize_field(field),
                description=value,
                rationale="来自本轮人工澄清答案",
            )
        )
    return ScopeDesignerOutput(
        prompt_version="0.1.0",
        must=tuple(must),
        should=(
            ScopeItem(
                item_id="SCOPE-SHOULD-01",
                title="交付说明",
                description="提供必要的使用、维护或交接说明",
                rationale="降低交付后的沟通和维护成本",
            ),
        ),
        could=(),
        wont=(
            ScopeItem(
                item_id="SCOPE-WONT-01",
                title="未确认的新增需求",
                description="本次报价不包含确认范围之外的临时增项",
                rationale="新增内容需要单独评估工时与价格",
            ),
            ScopeItem(
                item_id="SCOPE-WONT-02",
                title="第三方费用",
                description="域名、服务器、模型、素材和平台服务费不含在开发报价内",
                rationale="第三方费用由实际供应商和用量决定",
            ),
        ),
        blocked_by_missing_information=False,
    )


def _build_estimate(
    state: AgentState,
    answers: tuple[tuple[str, str], ...],
) -> TaskEstimatorOutput:
    project_type = state.intake.project_type if state.intake else ServiceType.AUTO_DETECT
    min_total, max_total = _BASE_HOURS[project_type]
    acceptance = next((value for field, value in answers if field == "acceptance"), None)
    acceptance_criteria = (acceptance or "按已确认范围逐项演示并完成交付验收",)
    tasks = (
        _task(
            "TASK-01",
            "方案与范围确认",
            min_total,
            max_total,
            Decimal("0.2"),
            acceptance_criteria,
        ),
        _task("TASK-02", "核心成果制作", min_total, max_total, Decimal("0.6"), acceptance_criteria),
        _task(
            "TASK-03",
            "测试、修改与交付",
            min_total,
            max_total,
            Decimal("0.2"),
            acceptance_criteria,
        ),
    )
    return TaskEstimatorOutput(
        prompt_version="0.1.0",
        tasks=tasks,
        buffer_hours=_round_half(max_total * Decimal("0.15")),
        uncertainty_notes=("当前为AI生成的首版估算，范围或素材变化会触发重新报价",),
    )


def _task(
    task_id: str,
    title: str,
    min_total: Decimal,
    max_total: Decimal,
    ratio: Decimal,
    acceptance_criteria: tuple[str, ...],
) -> EstimatedTask:
    return EstimatedTask(
        task_id=task_id,
        title=title,
        description=f"完成{title}所需工作并保留可核验交付记录",
        dependencies=() if task_id == "TASK-01" else (f"TASK-{int(task_id[-2:]) - 1:02d}",),
        min_hours=_round_half(min_total * ratio),
        max_hours=_round_half(max_total * ratio),
        estimate_basis="按服务类型基准工时、澄清范围和15%不确定性缓冲估算",
        acceptance_criteria=acceptance_criteria,
    )


def _build_risk_review(state: AgentState) -> RiskReviewerOutput:
    risks = [
        RiskItem(
            risk_id="RISK-01",
            category="requirement",
            severity=RiskSeverity.MEDIUM,
            cause="后续新增需求或修改已确认边界",
            impact="工时、排期和报价可能增加",
            mitigation="以当前范围为基线，增项先评估再执行",
            requires_human_decision=True,
        )
    ]
    if _fact_value(state, "deadline"):
        risks.append(
            RiskItem(
                risk_id="RISK-02",
                category="schedule",
                severity=RiskSeverity.MEDIUM,
                cause="项目存在明确期限且可能依赖客户反馈",
                impact="资料或反馈延迟会压缩制作和测试时间",
                mitigation="约定资料提供与阶段反馈截止时间",
                requires_human_decision=True,
            )
        )
    return RiskReviewerOutput(
        prompt_version="0.1.0",
        risks=tuple(risks),
        human_decisions=("确认范围、排期与三级报价后再对外承诺",),
    )


def _build_pricing(
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


def _build_proposal(
    state: AgentState,
    scope: ScopeDesignerOutput,
    estimate: TaskEstimatorOutput,
    risk_review: RiskReviewerOutput,
    pricing: PricingToolOutput,
) -> ProposalWriterOutput:
    project_name = _fact_value(state, "project_name") or "当前项目"
    return ProposalWriterOutput(
        prompt_version="0.1.0",
        project_summary=f"{project_name}已完成需求澄清，并形成可人工确认的范围与报价草案。",
        deliverables=tuple(item.title for item in (*scope.must, *scope.should)),
        exclusions=tuple(item.title for item in scope.wont),
        acceptance_criteria=estimate.tasks[-1].acceptance_criteria,
        quote_options=pricing.options,
        disclaimers=(
            "本方案为AI辅助生成的报价草案，人工确认前不构成对客户的正式承诺。",
            "超出已确认范围的需求、第三方费用和税费需要另行评估。",
        ),
    )


def _fact_value(state: AgentState, field: str) -> str | None:
    return next((fact.value for fact in state.confirmed_facts if fact.field == field), None)


def _hourly_rate(state: AgentState) -> Decimal:
    raw = _fact_value(state, "hourly_rate")
    if raw is None:
        return _DEFAULT_RATE
    try:
        return Decimal(raw.split()[0])
    except (IndexError, ArithmeticError):
        return _DEFAULT_RATE


def _round_half(value: Decimal) -> Decimal:
    return (value / _HALF_HOUR).quantize(Decimal("1"), ROUND_HALF_UP) * _HALF_HOUR


def _humanize_field(field: str) -> str:
    labels = {
        "target_users": "目标用户与场景",
        "must_have": "首版核心范围",
        "acceptance": "验收标准",
        "deadline": "交付期限",
        "content_owner": "内容与素材责任",
        "cms": "内容管理需求",
        "deployment": "部署责任",
        "data_source": "数据来源",
        "privacy": "隐私与数据边界",
        "quality": "质量标准",
        "revisions": "修改轮次",
    }
    return labels.get(field, field.replace("_", " ").title())
