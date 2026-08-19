from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from .contracts import (
    AgentRunView,
    ApproveQuoteCommand,
    CreateProjectCommand,
    ProjectView,
    SubmitClarificationCommand,
)


class CreateProjectUseCase(Protocol):
    async def execute(self, command: CreateProjectCommand) -> ProjectView: ...


class SubmitClarificationUseCase(Protocol):
    async def execute(self, command: SubmitClarificationCommand) -> AgentRunView: ...


class ApproveQuoteUseCase(Protocol):
    async def execute(self, command: ApproveQuoteCommand) -> AgentRunView: ...


class GetAgentRunUseCase(Protocol):
    async def execute(self, run_id: UUID) -> AgentRunView: ...


class ListProjectsUseCase(Protocol):
    async def execute(self) -> Sequence[ProjectView]: ...
