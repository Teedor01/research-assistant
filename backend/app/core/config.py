
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    
    requesty_api_key: str
    requesty_base_url: str = "https://router.requesty.ai/v1"

    
    llm_model_fast: str = "openai/gpt-4o-mini"         
    llm_model_reasoning: str = "openai/gpt-4o-mini"

    llm_max_retries: int = 3
    llm_retry_base_delay_seconds: float = 1.0
    llm_request_timeout_seconds: float = 60.0

    
    search_provider: str = "tavily"
    tavily_api_key: str | None = None
    search_default_results_narrow: int = 3
    search_default_results_broad: int = 4

    
    extraction_timeout_seconds: float = 15.0

    
    research_max_rounds: int = 1
    research_max_sources: int = 20
    research_time_budget_seconds: float = 45.0

   
    database_url: str

    
    log_level: str = "INFO"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    """Cached singleton, settings are read once, not re-parsed per request."""
    return Settings()