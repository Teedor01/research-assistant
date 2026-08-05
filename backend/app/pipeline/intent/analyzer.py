import logging
from app.providers.llm.base import LLMProvider, ModelTier
from app.pipeline.intent.schema import IntentSchema
from app.pipeline.intent.prompt import INTENT_SYSTEM_PROMPT, build_intent_prompt
from app.models.state import ResearchState
from app.models.intent import Intent
from app.core.observability import observed_node

logger = logging.getLogger(__name__)

DEFAULT_INTENT_FALLBACK = IntentSchema(
    is_comparison=False,
    is_broad=True,
    query_type="explanation",
    learning_level="beginner",
    needs_multi_query=True,
)


@observed_node("intent_analyzer")
async def analyze_intent(state: ResearchState, *, llm: LLMProvider) -> ResearchState:
    topic = state["topic"]

    try:
        response = await llm.generate_structured(
            system_prompt=INTENT_SYSTEM_PROMPT,
            user_prompt=build_intent_prompt(topic),
            response_model=IntentSchema,
            tier=ModelTier.FAST,
            temperature=0.0,
        )
        parsed = response.data
        state["metrics"]["intent_analyzer"]["tokens_used"] = response.tokens_used.total_tokens
    except ValueError as e:
        logger.warning(
            "Intent classification failed for topic=%r, using safe fallback. Error: %s",
            topic, e,
        )
        parsed = DEFAULT_INTENT_FALLBACK

    intent: Intent = {"topic": topic, **parsed.model_dump()}
    state["intent"] = intent
    return state