from dataclasses import dataclass

from app.application.services import ProjectAnalysisService
from app.infrastructure.ai.rule_based_intake import RuleBasedIntakeAgent
from app.infrastructure.persistence.in_memory import InMemoryProjectAnalysisStore


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    """只在Composition Root中装配当前阶段已经实现的依赖。"""

    project_analysis: ProjectAnalysisService


def build_container() -> ApplicationContainer:
    store = InMemoryProjectAnalysisStore()
    agent = RuleBasedIntakeAgent()
    return ApplicationContainer(project_analysis=ProjectAnalysisService(store, agent))
