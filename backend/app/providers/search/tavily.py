# app/providers/search/tavily.py
import logging
import asyncio
from tavily import AsyncTavilyClient  

from app.providers.search.base import SearchProvider, SearchResponse, SearchResult
from app.core.config import Settings

logger = logging.getLogger(__name__)


class TavilySearchProvider(SearchProvider):
    def __init__(self, settings: Settings):
        if not settings.tavily_api_key:
            raise ValueError("TAVILY_API_KEY is required to use TavilySearchProvider")
        self._client = AsyncTavilyClient(api_key=settings.tavily_api_key)
        self._max_retries = settings.llm_max_retries  
        self._retry_base_delay = settings.llm_retry_base_delay_seconds

    async def search(self, *, query: str, max_results: int = 5) -> SearchResponse:
        last_exception: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                raw = await self._client.search(
                    query=query,
                    max_results=max_results,
                    search_depth="basic",  
                )
                results = [
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        published_date=item.get("published_date"),
                    )
                    for item in raw.get("results", [])
                ]
                return SearchResponse(query=query, results=results)

            except Exception as e:
                last_exception = e
                delay = self._retry_base_delay * (2 ** attempt)
                logger.warning(
                    "Tavily search failed for query=%r (attempt %d/%d): %s. Retrying in %.1fs",
                    query, attempt + 1, self._max_retries, e, delay,
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(delay)

        # All retries exhausted — return empty results rather than raising.
        # A single failed sub-query shouldn't kill the whole research request;
        # the Gap Identifier can potentially retry it in a later round.
        logger.error("Tavily search exhausted retries for query=%r: %s", query, last_exception)
        return SearchResponse(query=query, results=[])