from collections.abc import Sequence
from types import TracebackType
from typing import Protocol, Self
from uuid import UUID

from app.domain.models import AgentRun, Project, SkillExecution

from .contracts import AgentRunView, ProjectView


class ProjectAnalysisStore(Protocol):
    async def save_project(self, project: ProjectView) -> None: ...

    async def save_run(self, run: AgentRunView) -> None: ...

    async def get_run(self, run_id: UUID) -> AgentRunView | None: ...

    async def get_project(self, project_id: UUID) -> ProjectView | None: ...

    async def list_projects(self) -> Sequence[ProjectView]: ...


class ProjectRepository(Protocol):
    async def add(self, project: Project) -> None: ...

    async def get(self, project_id: UUID) -> Project | None: ...

    async def list(self) -> Sequence[Project]: ...


class AgentRunRepository(Protocol):
    async def add(self, run: AgentRun) -> None: ...

    async def get(self, run_id: UUID) -> AgentRun | None: ...

    async def save(self, run: AgentRun) -> None: ...


class SkillExecutionRepository(Protocol):
    async def add(self, execution: SkillExecution) -> None: ...

    async def list_by_run(self, run_id: UUID) -> Sequence[SkillExecution]: ...


class UnitOfWork(Protocol):
    projects: ProjectRepository
    agent_runs: AgentRunRepository
    skill_executions: SkillExecutionRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


class TraceSink(Protocol):
    async def record(self, event_name: str, payload: dict[str, object]) -> None: ...
