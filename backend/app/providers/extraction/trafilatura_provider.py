# app/providers/extraction/trafilatura_provider.py
import asyncio
import logging
import httpx
import trafilatura

from app.providers.extraction.base import ExtractionProvider, ExtractionResult

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 200  


class TrafilaturaExtractionProvider(ExtractionProvider):
    def __init__(self):
        self._http_client = httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (research-agent-bot)"},
        )

    async def extract(self, *, url: str, timeout_seconds: float) -> ExtractionResult:
        try:
            html = await asyncio.wait_for(
                self._fetch_html(url), timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            return ExtractionResult(success=False, error="fetch timed out")
        except Exception as e:
            return ExtractionResult(success=False, error=f"fetch failed: {e}")

        if not html:
            return ExtractionResult(success=False, error="empty response body")

        # trafilatura's extract() is CPU-bound and synchronous — run off the
        # event loop so it doesn't block other concurrent extractions.
        text = await asyncio.to_thread(
            trafilatura.extract, html, favor_precision=True
        )

        if not text or len(text) < MIN_TEXT_LENGTH:
            return ExtractionResult(success=False, error="no meaningful content extracted")

        return ExtractionResult(success=True, text=text)

    async def _fetch_html(self, url: str) -> str:
        response = await self._http_client.get(url)
        response.raise_for_status()
        return response.text

    async def aclose(self):
        await self._http_client.aclose()