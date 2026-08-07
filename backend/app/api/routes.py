import asyncio
import logging
from fastapi import APIRouter, HTTPException

from app.api.schemas import ResearchRequest, ResearchResponse, ErrorResponse, ErrorDetail
from app.agent.runner import run_research
from app.core.config import get_settings
from app.core.exceptions import ResearchTimeoutError, ResearchFailedError

logger = logging.getLogger(__name__)
router = APIRouter()


REQUEST_TIMEOUT_BUFFER_SECONDS = 240


@router.post(
    "/research",
    response_model=ResearchResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 504: {"model": ErrorResponse}},
)
async def research(request: ResearchRequest) -> ResearchResponse:
    settings = get_settings()
    wall_clock_limit = settings.research_time_budget_seconds + REQUEST_TIMEOUT_BUFFER_SECONDS

    try:
        final_state = await asyncio.wait_for(
            run_research(request.topic), timeout=wall_clock_limit
        )
    except asyncio.TimeoutError:
        logger.error("Research request timed out at the wall-clock backstop for topic=%r", request.topic)
        raise HTTPException(
            status_code=504,
            detail=ErrorDetail(
                code="RESEARCH_TIMEOUT",
                message="This is taking longer than expected. Please try again.",
            ).model_dump(),
        )
    except Exception as e:
        logger.exception("Unhandled error researching topic=%r", request.topic)
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                code="RESEARCH_FAILED",
                message="We couldn't complete research on that topic right now. Please try again.",
            ).model_dump(),
        )

    final_response = final_state.get("final_response")
    if final_response is None:
        # Defensive — should be unreachable given the Writer's own fallback
        # guarantees final_response is always set, even on partial failure.
        logger.error("Graph completed with no final_response for topic=%r", request.topic)
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                code="RESEARCH_FAILED",
                message="We couldn't complete research on that topic right now. Please try again.",
            ).model_dump(),
        )

    return ResearchResponse(topic=request.topic, **final_response)