from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.agent.ports import IntakeAgent
from app.agent.schemas import ProjectBrief
from app.application.contracts import (
    AgentRunView,
    CreateProjectCommand,
    ProjectView,
    SubmitClarificationCommand,
)
from app.application.ports import ProjectAnalysisStore
from app.core.errors import ResourceNotFoundError


class ProjectAnalysisService:
    def __init__(self, store: ProjectAnalysisStore, agent: IntakeAgent) -> None:
        self._store = store
        self._agent = agent

    async def create_project(self, command: CreateProjectCommand) -> ProjectView:
        project_id = uuid4()
        run_id = uuid4()
        now = datetime.now(UTC)
        brief = ProjectBrief.model_validate(command.model_dump())
        state = await self._agent.analyze(run_id, project_id, brief)
        run = AgentRunView(
            id=run_id,
            project_id=project_id,
            status=state.status,
            current_step=state.current_step,
            state=state,
        )
        project = ProjectView(
            id=project_id,
            name=command.name,
            client_request=command.client_request,
            service_type=command.service_type,
            budget=command.budget,
            deadline=command.deadline,
            hourly_rate=command.hourly_rate,
            created_at=now,
            updated_at=now,
            run=run,
        )
        await self._store.save_project(project)
        return project

    async def get_run(self, run_id: UUID) -> AgentRunView:
        run = await self._store.get_run(run_id)
        if run is None:
            raise ResourceNotFoundError("Agent运行记录不存在")
        return run

    async def list_projects(self) -> tuple[ProjectView, ...]:
        return tuple(await self._store.list_projects())

    async def submit_answers(self, command: SubmitClarificationCommand) -> AgentRunView:
        run = await self.get_run(command.run_id)
        state = await self._agent.submit_answers(run.state, command.answers)
        updated = run.model_copy(
            update={
                "status": state.status,
                "current_step": state.current_step,
                "state": state,
            }
        )
        await self._store.save_run(updated)
        return updated
