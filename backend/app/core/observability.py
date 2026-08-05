import time
import logging
import functools
from typing import Callable, Awaitable
from app.models.state import ResearchState, NodeMetrics

logger = logging.getLogger(__name__)


def observed_node(name: str):
    """Wraps a LangGraph node to record timing automatically into
    state["metrics"][name]. Node-specific counters (tokens_used, pages_extracted,
    etc.) are the node's own responsibility to set on the same dict — this
    decorator only guarantees the entry exists and duration is recorded."""

    def decorator(
        fn: Callable[..., Awaitable[ResearchState]]
    ) -> Callable[..., Awaitable[ResearchState]]:

        @functools.wraps(fn)
        async def wrapper(state: ResearchState, *args, **kwargs) -> ResearchState:
            if "metrics" not in state or state["metrics"] is None:
                state["metrics"] = {}
            state["metrics"].setdefault(name, NodeMetrics())

            start = time.perf_counter()
            try:
                result = await fn(state, *args, **kwargs)
                return result
            except Exception:
                logger.exception("Node %r raised an exception", name)
                raise
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                state["metrics"][name]["duration_ms"] = duration_ms
                logger.info("Node %r completed in %.1fms", name, duration_ms)

        return wrapper

    return decorator