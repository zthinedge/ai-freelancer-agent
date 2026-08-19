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


class ServiceType(StrEnum):
    AUTO_DETECT = "auto_detect"
    WEBSITE = "website"
    AI_APPLICATION = "ai_application"
    ECOMMERCE = "ecommerce"
    PRESENTATION = "presentation"
    CONTENT = "content"
    DESIGN = "design"
    DATA_ANALYSIS = "data_analysis"
    VIDEO = "video"
    OTHER = "other"


class FactSource(StrEnum):
    CLIENT_REQUEST = "client_request"
    CLARIFICATION_ANSWER = "clarification_answer"
    SYSTEM = "system"


class QuestionPriority(StrEnum):
    CRITICAL = "critical"
    IMPORTANT = "important"
    OPTIONAL = "optional"


class RiskSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class QuoteTier(StrEnum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
