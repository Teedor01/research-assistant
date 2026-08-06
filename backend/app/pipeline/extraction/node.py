import asyncio
import logging

from app.providers.extraction.base import ExtractionProvider
from app.models.state import ResearchState
from app.core.config import Settings
from app.core.observability import observed_node

logger = logging.getLogger(__name__)


async def _extract_one(source: dict, provider: ExtractionProvider, timeout: float) -> None:
    """Mutates the source dict in place — called concurrently per source."""
    result = await provider.extract(url=source["url"], timeout_seconds=timeout)

    if result.success:
        source["extracted_text"] = result.text
        source["status"] = "extracted"
    else:
        source["status"] = "failed"
        source["discard_reason"] = result.error


@observed_node("extraction")
async def run_extraction(
    state: ResearchState, *, extraction_provider: ExtractionProvider, settings: Settings
) -> ResearchState:
    pending = [s for s in state["sources"] if s["status"] == "pending"]

    if not pending:
        return state

    await asyncio.gather(
        *(
            _extract_one(source, extraction_provider, settings.extraction_timeout_seconds)
            for source in pending
        ),
        return_exceptions=False,  
    )

    extracted_count = sum(1 for s in pending if s["status"] == "extracted")
    failed_count = sum(1 for s in pending if s["status"] == "failed")

    state["metrics"]["extraction"]["pages_extracted"] = extracted_count
    state["metrics"]["extraction"]["pages_failed"] = failed_count
    logger.info("Extraction: %d succeeded, %d failed", extracted_count, failed_count)

    return state