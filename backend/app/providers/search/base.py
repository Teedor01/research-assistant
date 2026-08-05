from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    published_date: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class SearchProvider(ABC):
    """Interface for web search. Concrete implementations (Tavily, and anything
    swapped in later) implement this. Nodes depend only on this interface."""

    @abstractmethod
    async def search(self, *, query: str, max_results: int = 5) -> SearchResponse:
        ...