from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional


class ExtractionResult(BaseModel):
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None


class ExtractionProvider(ABC):
    """Interface for turning a URL into clean text. Owns both fetching and
    parsing — callers only care about the end result."""

    @abstractmethod
    async def extract(self, *, url: str, timeout_seconds: float) -> ExtractionResult:
        ...