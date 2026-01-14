"""Core application configuration."""

import secrets
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/aicreate"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 50

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    api_workers: int = 4

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Security
    # WARNING: Generate a new secret key for production with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # LLM Providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    zhipuai_api_key: str = ""
    zhipuai_model: str = "glm-4"
    zhipuai_base_url: str = "https://open.bigmodel.cn/api/paas/v4/"

    # RSSHub
    # 使用本地部署的RSSHub实例
    rsshub_instance: str = "http://localhost:1200"
    rsshub_cache_ttl: int = 300
    rsshub_rate_limit_delay: float = 1.0

    # Content Filter
    filter_enabled: bool = True
    filter_strict_mode: bool = False

    # Monitoring
    prometheus_enabled: bool = True
    log_level: str = "INFO"

    # Workflow Execution
    workflow_timeout: int = 3600
    workflow_max_retries: int = 3
    workflow_retry_delay: int = 5

    # Checkpointing
    checkpoint_enabled: bool = True
    checkpoint_namespace: str = "checkpoints"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
