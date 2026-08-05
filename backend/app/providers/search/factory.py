from functools import lru_cache
from app.core.config import get_settings
from app.providers.search.base import SearchProvider
from app.providers.search.tavily import TavilySearchProvider


@lru_cache
def get_search_provider() -> SearchProvider:
    return TavilySearchProvider(settings=get_settings())