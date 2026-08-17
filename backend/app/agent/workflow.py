from app.domain.enums import WorkflowStep

WORKFLOW_ORDER: tuple[WorkflowStep, ...] = (
    WorkflowStep.INTAKE,
    WorkflowStep.CLARIFICATION,
    WorkflowStep.SCOPE,
    WorkflowStep.ESTIMATION,
    WorkflowStep.RISK,
    WorkflowStep.PRICING,
    WorkflowStep.PROPOSAL,
)

HUMAN_CHECKPOINTS: frozenset[WorkflowStep] = frozenset(
    {
        WorkflowStep.CLARIFICATION,
        WorkflowStep.PROPOSAL,
    }
)

SKILL_NAMES: tuple[str, ...] = (
    "requirement_intake",
    "clarification_planner",
    "scope_designer",
    "task_estimator",
    "risk_reviewer",
    "proposal_writer",
)

TOOL_NAMES: tuple[str, ...] = ("pricing_calculator",)
