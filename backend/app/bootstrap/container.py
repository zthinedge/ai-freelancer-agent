from dataclasses import dataclass
from typing import Protocol

from app.agent.ports import AgentOrchestrator, ModelGateway, SkillRegistry, ToolRegistry
from app.application.ports import TraceSink, UnitOfWork


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    """应用依赖容器；具体实例只允许在Composition Root创建。"""

    unit_of_work: UnitOfWork
    model_gateway: ModelGateway
    skill_registry: SkillRegistry
    tool_registry: ToolRegistry
    orchestrator: AgentOrchestrator
    trace_sink: TraceSink


class ContainerFactory(Protocol):
    def build(self) -> ApplicationContainer: ...
