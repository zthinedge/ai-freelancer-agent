from dataclasses import dataclass
from pathlib import Path

from app.agent.ports import ContextMemory
from app.application.ports import ProjectAnalysisStore
from app.application.services import ProjectAnalysisService
from app.core.config import Settings, get_settings
from app.infrastructure.ai.model_intake import ModelBackedIntakeAgent
from app.infrastructure.ai.openai_compatible import OpenAICompatibleModelGateway
from app.infrastructure.ai.rule_based_intake import RuleBasedIntakeAgent
from app.infrastructure.memory import SQLiteContextMemory
from app.infrastructure.persistence.sqlite import (
    SQLiteProjectAnalysisStore,
    sqlite_path_from_url,
)


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    """只在Composition Root中装配当前阶段已经实现的依赖。"""

    project_analysis: ProjectAnalysisService
    project_store: ProjectAnalysisStore
    context_memory: ContextMemory | None


def build_container(settings: Settings | None = None) -> ApplicationContainer:
    runtime_settings = settings or get_settings()
    database_path = sqlite_path_from_url(runtime_settings.database_url)
    store = SQLiteProjectAnalysisStore(database_path)
    knowledge_directory = Path(__file__).resolve().parents[2] / "knowledge"
    context_memory = (
        SQLiteContextMemory(database_path, knowledge_directory)
        if runtime_settings.rag_enabled
        else None
    )
    fallback = RuleBasedIntakeAgent()
    if runtime_settings.ai_is_configured:
        gateway = OpenAICompatibleModelGateway(
            base_url=runtime_settings.ai_base_url,
            api_key=runtime_settings.ai_api_key.get_secret_value(),
            model=runtime_settings.ai_model,
            timeout_seconds=runtime_settings.ai_timeout_seconds,
            max_retries=runtime_settings.ai_max_retries,
            max_tokens=runtime_settings.ai_max_tokens,
            thinking_enabled=runtime_settings.ai_thinking_enabled,
        )
        agent = ModelBackedIntakeAgent(gateway, fallback, runtime_settings.ai_model)
    else:
        agent = fallback
    return ApplicationContainer(
        project_analysis=ProjectAnalysisService(
            store,
            agent,
            context_memory,
            runtime_settings.rag_top_k,
        ),
        project_store=store,
        context_memory=context_memory,
    )
