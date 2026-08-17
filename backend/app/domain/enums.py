from enum import StrEnum


class AgentRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_USER = "waiting_user"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStep(StrEnum):
    INTAKE = "requirement_intake"
    CLARIFICATION = "clarification_planner"
    SCOPE = "scope_designer"
    ESTIMATION = "task_estimator"
    RISK = "risk_reviewer"
    PRICING = "pricing_calculator"
    PROPOSAL = "proposal_writer"


class SkillExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    FALLBACK = "fallback"


class ApprovalType(StrEnum):
    CLARIFICATION = "clarification"
    QUOTE = "quote"
