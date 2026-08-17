from collections.abc import Sequence
from typing import Protocol

from .contracts import (
    AgentState,
    ModelRequest,
    ModelResponse,
    SkillRequest,
    SkillResult,
    ToolRequest,
    ToolResult,
)


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
