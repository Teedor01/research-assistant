from functools import lru_cache
from app.agent.graph import build_research_graph
from app.providers.llm.factory import get_llm_provider
from app.providers.search.factory import get_search_provider
from app.providers.extraction.factory import get_extraction_provider
from app.core.config import get_settings


@lru_cache
def get_research_graph():
    """Builds the compiled graph once with real (Requesty/Tavily/trafilatura)
    providers. Mirrors every other factory in the project — the api/ layer
    calls this, never constructs providers itself."""
    return build_research_graph(
        llm=get_llm_provider(),
        search_provider=get_search_provider(),
        extraction_provider=get_extraction_provider(),
        settings=get_settings(),
    )