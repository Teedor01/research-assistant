import time
import logging
from app.models.state import ResearchState
from app.providers.llm.base import LLMProvider, ModelTier
from app.pipeline.gaps.schema import GapAnalysisSchema
from app.pipeline.gaps.summarize import summarize_knowledge
from app.pipeline.gaps.prompt import GAP_SYSTEM_PROMPT, build_gap_prompt
from app.core.config import Settings
from app.core.observability import observed_node

logger = logging.getLogger(__name__)

MAX_GAP_QUERIES = 3
MARGINAL_FACTS_THRESHOLD = 2  


def _hard_bound_hit(state: ResearchState, settings: Settings) -> tuple[bool, str | None]:
    if state["round_number"] >= settings.research_max_rounds:
        return True, "max rounds reached"
    if len(state["sources"]) >= settings.research_max_sources:
        return True, "max sources reached"
    elapsed = time.time() - state["started_at"]
    if elapsed >= settings.research_time_budget_seconds:
        return True, "time budget exceeded"
    return False, None


def _diminishing_returns(state: ResearchState) -> bool:
    if state["round_number"] < 2 or not state["research_log"]:
        return False  # round 1 always gets to continue if the LLM finds gaps
    last_round = state["research_log"][-1]
    return last_round["new_facts_added"] < MARGINAL_FACTS_THRESHOLD


@observed_node("gap_identifier")
async def identify_gaps(state: ResearchState, *, llm: LLMProvider, settings: Settings) -> ResearchState:
    knowledge = state["structured_knowledge"]

    hard_stop, hard_stop_reason = _hard_bound_hit(state, settings)
    if hard_stop:
        logger.info("Gap Identifier: stopping — %s", hard_stop_reason)
        knowledge["completeness"] = "partial"
        state["sub_queries"] = []
        return state

    if _diminishing_returns(state):
        logger.info("Gap Identifier: stopping — diminishing returns (few new facts last round)")
        knowledge["completeness"] = "complete"
        state["sub_queries"] = []
        return state

    knowledge_summary = summarize_knowledge(knowledge)
    try:
        response = await llm.generate_structured(
            system_prompt=GAP_SYSTEM_PROMPT,
            user_prompt=build_gap_prompt(state["topic"], state["initial_sub_queries"], knowledge_summary),
            response_model=GapAnalysisSchema,
            tier=ModelTier.FAST,
            temperature=0.1,
        )
        gaps = response.data.gaps[:MAX_GAP_QUERIES]
        state["metrics"]["gap_identifier"]["tokens_used"] = response.tokens_used.total_tokens
    except ValueError as e:
        logger.warning("Gap identification failed, treating as no gaps found. Error: %s", e)
        gaps = []

    if not gaps:
        logger.info("Gap Identifier: stopping — no gaps found, research considered complete")
        knowledge["completeness"] = "complete"
        state["sub_queries"] = []
        return state

    logger.info("Gap Identifier: %d gap(s) found, starting round %d", len(gaps), state["round_number"] + 1)
    state["round_number"] += 1
    state["sub_queries"] = [g.suggested_query for g in gaps]
    state["research_log"].append({
        "round_number": state["round_number"],
        "queries_run": state["sub_queries"],
        "sources_found": 0,
        "new_facts_added": 0,
        "redundant_sources": 0,
    })
    return state


def should_continue_research(state: ResearchState) -> str:
    """LangGraph conditional edge router — NOT decorated with observed_node since
    it's a pure routing function, not a data-transforming node. Returns the name
    of the next node to visit."""
    if state["sub_queries"]:
        return "search"  # loop back
    return "confidence_scorer"  # proceed forward