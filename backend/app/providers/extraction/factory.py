from functools import lru_cache
from app.providers.extraction.base import ExtractionProvider
from app.providers.extraction.trafilatura_provider import TrafilaturaExtractionProvider


@lru_cache
def get_extraction_provider() -> ExtractionProvider:
    return TrafilaturaExtractionProvider()