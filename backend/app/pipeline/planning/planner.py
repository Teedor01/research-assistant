import logging
from app.providers.llm.base import LLMProvider, ModelTier
from app.pipeline.planning.schema import QueryPlanSchema
from app.pipeline.planning.prompt import PLANNING_SYSTEM_PROMPT, build_planning_prompt
from app.models.state import ResearchState
from app.core.observability import observed_node

logger = logging.getLogger(__name__)

MAX_SUB_QUERIES = 5


def _fallback_queries(topic: str) -> list[str]:
    """If planning fails, fall back to the raw topic as a single query rather
    than blocking the pipeline — matches the graceful-degradation approach
    used in Intent Analyzer."""
    return [topic]


@observed_node("query_planner")
async def plan_queries(state: ResearchState, *, llm: LLMProvider) -> ResearchState:
    topic = state["topic"]
    intent = state["intent"]
    state["sub_queries"] = queries
    state["initial_sub_queries"] = list(queries)

    if intent is None:
        
        raise RuntimeError("plan_queries called with no intent in state")

    try:
        response = await llm.generate_structured(
            system_prompt=PLANNING_SYSTEM_PROMPT,
            user_prompt=build_planning_prompt(topic, intent),
            response_model=QueryPlanSchema,
            tier=ModelTier.FAST,
            temperature=0.25,  
        )
        queries = response.data.sub_queries[:MAX_SUB_QUERIES]
        state["metrics"]["query_planner"]["tokens_used"] = response.tokens_used.total_tokens

        if not queries:
            logger.warning("Query planner returned empty list for topic=%r, using fallback", topic)
            queries = _fallback_queries(topic)

    except ValueError as e:
        logger.warning(
            "Query planning failed for topic=%r, using fallback. Error: %s", topic, e,
        )
        queries = _fallback_queries(topic)

    state["sub_queries"] = queries
    state["round_number"] = 1
    state["research_log"].append({
        "round_number": 1,
        "queries_run": queries,
        "sources_found": 0,       
        "new_facts_added": 0,     
        "redundant_sources": 0,   
    })

    return state