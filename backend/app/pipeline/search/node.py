import asyncio
import hashlib
import logging
from urllib.parse import urlparse

from app.providers.search.base import SearchProvider
from app.models.state import ResearchState
from app.models.source import SourceDocument
from app.core.config import Settings
from app.core.observability import observed_node

logger = logging.getLogger(__name__)


def _source_id(url: str) -> str:
    """Deterministic ID from URL so the same page maps to the same
    SourceDocument.id across search rounds — makes cross-round dedup a
    simple ID-set lookup instead of another similarity check."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def _domain_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return ""


@observed_node("search")
async def run_search(
    state: ResearchState, *, search_provider: SearchProvider, settings: Settings
) -> ResearchState:
    intent = state["intent"]
    queries = state["sub_queries"]

    max_results = (
        settings.search_default_results_broad
        if intent and intent["is_broad"]
        else settings.search_default_results_narrow
    )

    responses = await asyncio.gather(
        *(search_provider.search(query=q, max_results=max_results) for q in queries),
        return_exceptions=True,  
    )

    existing_ids = {s["id"] for s in state["sources"]}
    new_sources: list[SourceDocument] = []
    seen_urls_this_round: set[str] = set()

    for response in responses:
        if isinstance(response, Exception):
            logger.error("Search sub-task raised unexpectedly: %s", response)
            continue

        for result in response.results:
            if not result.url or result.url in seen_urls_this_round:
                continue
            seen_urls_this_round.add(result.url)

            source_id = _source_id(result.url)
            if source_id in existing_ids:
                continue  

            new_sources.append({
                "id": source_id,
                "url": result.url,
                "domain": _domain_from_url(result.url),
                "title": result.title,
                "published_date": result.published_date,
                "extracted_text": None,
                "domain_score": 0.0,       
                "content_score": None,      
                "credibility_score": None,  
                "status": "pending",
                "discard_reason": None,
            })

    state["sources"].extend(new_sources)
    state["metrics"]["search"]["search_results"] = len(new_sources)

    if state["research_log"]:
        state["research_log"][-1]["sources_found"] = len(new_sources)

    return state