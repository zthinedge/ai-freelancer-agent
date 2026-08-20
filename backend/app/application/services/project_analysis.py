import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.agent.ports import ContextMemory, IntakeAgent
from app.agent.schemas import ConfirmedFact, ProjectBrief
from app.application.contracts import (
    AgentRunView,
    ApproveQuoteCommand,
    CreateProjectCommand,
    ProjectView,
    SubmitClarificationCommand,
)
from app.application.ports import ProjectAnalysisStore
from app.core.errors import ConflictError, ResourceNotFoundError
from app.domain.enums import AgentRunStatus, FactSource, WorkflowStep


class ProjectAnalysisService:
    def __init__(
        self,
        store: ProjectAnalysisStore,
        agent: IntakeAgent,
        context_memory: ContextMemory | None = None,
        context_limit: int = 3,
    ) -> None:
        self._store = store
        self._agent = agent
        self._context_memory = context_memory
        self._context_limit = context_limit
        self._run_locks: dict[UUID, asyncio.Lock] = {}

    async def create_project(self, command: CreateProjectCommand) -> ProjectView:
        project_id = uuid4()
        run_id = uuid4()
        now = datetime.now(UTC)
        brief = ProjectBrief.model_validate(command.model_dump())
        if self._context_memory is not None:
            retrieved_context = await self._context_memory.search(
                f"{command.name} {command.service_type.value} {command.client_request}",
                limit=self._context_limit,
            )
            brief = brief.model_copy(update={"retrieved_context": retrieved_context})
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
        async with self._lock_for(command.run_id):
            run = await self.get_run(command.run_id)
            if run.status is not AgentRunStatus.WAITING_USER:
                raise ConflictError("当前运行不在等待澄清状态，不能重复提交答案")
            if not run.state.pending_questions:
                raise ConflictError("当前运行没有待回答的澄清问题")
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

    async def approve_quote(self, command: ApproveQuoteCommand) -> AgentRunView:
        async with self._lock_for(command.run_id):
            run = await self.get_run(command.run_id)
            if run.status is not AgentRunStatus.WAITING_APPROVAL:
                raise ConflictError("当前运行不在报价确认状态，不能执行人工确认")
            if run.state.fallback_reason is not None:
                raise ConflictError("AI分析未完整成功，当前结果不可批准，请重新分析")
            if run.state.scope is not None and run.state.scope.blocked_by_missing_information:
                raise ConflictError("需求仍缺少关键信息，当前结果不可批准")
            if run.state.pricing is None or run.state.proposal is None:
                raise ConflictError("报价草案尚未生成，不能执行人工确认")
            if command.approved and command.selected_tier is None:
                raise ConflictError("确认报价时必须选择一个报价方案")
            review_fact = ()
            if command.note:
                review_fact = (
                    ConfirmedFact(
                        field="quote_review_note",
                        value=command.note,
                        source=FactSource.SYSTEM,
                        evidence="用户在报价人工确认节点填写的备注",
                    ),
                )
            state = run.state.model_copy(
                update={
                    "status": (
                        AgentRunStatus.COMPLETED
                        if command.approved
                        else AgentRunStatus.WAITING_APPROVAL
                    ),
                    "current_step": WorkflowStep.PROPOSAL,
                    "quote_approved": command.approved,
                    "selected_quote_tier": command.selected_tier if command.approved else None,
                    "confirmed_facts": (*run.state.confirmed_facts, *review_fact),
                }
            )
            updated = run.model_copy(
                update={
                    "status": state.status,
                    "current_step": state.current_step,
                    "state": state,
                }
            )
            await self._store.save_run(updated)
            if command.approved and self._context_memory is not None:
                project = await self._store.get_project(run.project_id)
                if project is not None:
                    await self._context_memory.remember(
                        source_id=f"project:{project.id}",
                        title=f"已确认项目：{project.name}",
                        content=_project_memory_document(project),
                        metadata={
                            "kind": "approved_project",
                            "service_type": project.service_type.value,
                            "project_id": str(project.id),
                        },
                    )
            return updated

    def _lock_for(self, run_id: UUID) -> asyncio.Lock:
        """Serialize mutations for one run so duplicate requests cannot overwrite state."""
        return self._run_locks.setdefault(run_id, asyncio.Lock())


def _project_memory_document(project: ProjectView) -> str:
    if project.run is None:
        raise ValueError("approved project must include an Agent run")
    agent_state = project.run.state
    lines = [
        f"项目名称：{project.name}",
        f"服务类型：{project.service_type.value}",
        f"客户需求：{project.client_request}",
        f"时薪：{project.hourly_rate.amount} {project.hourly_rate.currency}",
    ]
    if agent_state.scope is not None:
        lines.append("确认范围：" + "；".join(item.title for item in agent_state.scope.must))
        lines.append("排除范围：" + "；".join(item.title for item in agent_state.scope.wont))
    if agent_state.estimate is not None:
        lines.append(
            "任务估算："
            + "；".join(
                f"{task.title} {task.min_hours}-{task.max_hours}小时"
                for task in agent_state.estimate.tasks
            )
        )
    if agent_state.risk_review is not None:
        lines.append(
            "主要风险："
            + "；".join(
                f"{risk.category}/{risk.severity.value}：{risk.cause}，措施：{risk.mitigation}"
                for risk in agent_state.risk_review.risks
            )
        )
    if agent_state.pricing is not None and agent_state.selected_quote_tier is not None:
        option = next(
            item
            for item in agent_state.pricing.options
            if item.tier is agent_state.selected_quote_tier
        )
        lines.append(
            f"确认报价：{option.tier.value}，{option.amount.amount} {option.amount.currency}，"
            f"包含{option.included_hours}小时"
        )
    return "\n".join(lines)
