# app/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Requesty / LLM ---
    requesty_api_key: str
    requesty_base_url: str = "https://router.requesty.ai/v1"

    # Model selection is config-driven, never hardcoded in node code.
    # "fast" = intent classification, gap detection (cheap, deterministic tasks)
    # "reasoning" = synthesis, writing (needs more capability)
    llm_model_fast: str = "openai/gpt-4o-mini"        # placeholder — swap to a free Requesty model
    llm_model_reasoning: str = "openai/gpt-4o-mini"

    llm_max_retries: int = 3
    llm_retry_base_delay_seconds: float = 1.0
    llm_request_timeout_seconds: float = 60.0

    # --- Search ---
    search_provider: str = "tavily"
    tavily_api_key: str | None = None
    search_default_results_narrow: int = 4
    search_default_results_broad: int = 6

    # --- Extraction ---
    extraction_timeout_seconds: float = 15.0

    # --- Research loop bounds ---
    research_max_rounds: int = 3
    research_max_sources: int = 20
    research_time_budget_seconds: float = 45.0

   
    database_url: str

    
    log_level: str = "INFO"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    """Cached singleton — settings are read once, not re-parsed per request."""
    return Settings()