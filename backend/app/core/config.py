"""
Central configuration, loaded from environment variables.
Never hard-code secrets or API keys here -- see .env.example.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"

    database_url: str = "sqlite:///./migration_orchestrator.db"

    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-6"
    llm_api_key: str = ""

    max_repair_attempts: int = 3

    docker_network_disabled: bool = True  # sandbox containers run with --network=none

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
