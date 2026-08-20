from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import __version__


class Settings(BaseSettings):
    """由环境变量注入的进程级配置，不包含业务规则。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    name: str = "接单智策 API"
    version: str = __version__
    environment: str = "development"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]
    )

    ai_api_key: SecretStr | None = None
    ai_base_url: str = "https://api.deepseek.com"
    ai_model: str = "deepseek-v4-flash"
    ai_timeout_seconds: float = 30.0
    ai_max_retries: int = Field(default=1, ge=0, le=3)
    ai_max_tokens: int = Field(default=4096, ge=256, le=32768)
    ai_thinking_enabled: bool = False

    database_url: str = "sqlite:///./data/jiedan.db"
    rag_enabled: bool = True
    rag_top_k: int = Field(default=3, ge=1, le=5)
    mcp_enabled: bool = True

    @property
    def ai_is_configured(self) -> bool:
        if self.ai_api_key is None:
            return False
        return bool(self.ai_api_key.get_secret_value().strip() and self.ai_model.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
