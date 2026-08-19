import asyncio
from collections.abc import Sequence
from uuid import UUID

from app.application.contracts import AgentRunView, ProjectView
from app.application.ports import ProjectAnalysisStore


class InMemoryProjectAnalysisStore(ProjectAnalysisStore):
    def __init__(self) -> None:
        self._projects: dict[UUID, ProjectView] = {}
        self._runs: dict[UUID, AgentRunView] = {}
        self._project_by_run: dict[UUID, UUID] = {}
        self._lock = asyncio.Lock()

    async def save_project(self, project: ProjectView) -> None:
        async with self._lock:
            self._projects[project.id] = project
            if project.run is not None:
                self._runs[project.run.id] = project.run
                self._project_by_run[project.run.id] = project.id

    async def save_run(self, run: AgentRunView) -> None:
        async with self._lock:
            self._runs[run.id] = run
            project_id = self._project_by_run[run.id]
            project = self._projects[project_id]
            self._projects[project_id] = project.model_copy(update={"run": run})

    async def get_run(self, run_id: UUID) -> AgentRunView | None:
        async with self._lock:
            return self._runs.get(run_id)

    async def list_projects(self) -> Sequence[ProjectView]:
        async with self._lock:
            return tuple(
                sorted(
                    self._projects.values(), key=lambda project: project.created_at, reverse=True
                )
            )
