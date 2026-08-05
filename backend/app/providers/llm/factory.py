from functools import lru_cache
from app.core.config import get_settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.requesty import RequestyLLMProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    return RequestyLLMProvider(settings=get_settings())