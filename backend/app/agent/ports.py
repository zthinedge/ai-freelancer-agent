from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from .contracts import (
    AgentState,
    ModelRequest,
    ModelResponse,
    SkillRequest,
    SkillResult,
    ToolRequest,
    ToolResult,
)
from .schemas import ProjectBrief


class IntakeAgent(Protocol):
    async def analyze(self, run_id: UUID, project_id: UUID, brief: ProjectBrief) -> AgentState: ...

    async def submit_answers(self, state: AgentState, answers: dict[str, str]) -> AgentState: ...


class ModelGateway(Protocol):
    async def complete(self, request: ModelRequest) -> ModelResponse: ...


class Skill(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    async def execute(self, request: SkillRequest) -> SkillResult: ...


class SkillRegistry(Protocol):
    def get(self, skill_name: str) -> Skill: ...

    def list(self) -> Sequence[Skill]: ...


class Tool(Protocol):
    @property
    def name(self) -> str: ...

    async def execute(self, request: ToolRequest) -> ToolResult: ...


class ToolRegistry(Protocol):
    def get(self, tool_name: str) -> Tool: ...


class AgentOrchestrator(Protocol):
    async def start(self, state: AgentState) -> AgentState: ...

    async def resume(self, state: AgentState) -> AgentState: ...
