import logging
from app.models.state import ResearchState
from app.models.response import FinalResponse
from app.providers.llm.base import LLMProvider, ModelTier
from app.pipeline.writer.schema import WriterOutputSchema
from app.pipeline.writer.context import build_writer_context
from app.pipeline.writer.prompt import WRITER_SYSTEM_PROMPT, build_writer_prompt
from app.core.observability import observed_node

logger = logging.getLogger(__name__)

FALLBACK_TEXT = "This section could not be generated. Please try researching this topic again."


def _fallback_response(topic: str, knowledge) -> WriterOutputSchema:
    return WriterOutputSchema(
        simple_explanation=FALLBACK_TEXT, core_concepts=FALLBACK_TEXT,
        why_it_matters=FALLBACK_TEXT, real_world_examples=FALLBACK_TEXT,
        advantages=FALLBACK_TEXT, limitations=FALLBACK_TEXT,
        common_misconceptions=FALLBACK_TEXT, faq=[], summary=FALLBACK_TEXT,
    )


@observed_node("writer")
async def write_response(state: ResearchState, *, llm: LLMProvider) -> ResearchState:
    topic = state["topic"]
    intent = state["intent"]
    knowledge = state["structured_knowledge"]

    has_process_info = bool(knowledge["processes"]) or (
        intent is not None and intent["query_type"] == "how_it_works"
    )
    context = build_writer_context(knowledge)

    try:
        response = await llm.generate_structured(
            system_prompt=WRITER_SYSTEM_PROMPT,
            user_prompt=build_writer_prompt(topic, intent, context, has_process_info),
            response_model=WriterOutputSchema,
            tier=ModelTier.REASONING,
            temperature=0.4,  # some room for natural prose, but facts are fixed by the context
            max_tokens = 6000
        )
        draft = response.data
        state["metrics"]["writer"]["tokens_used"] = response.tokens_used.total_tokens
    except ValueError as e:
        logger.error("Writer generation failed for topic=%r: %s", topic, e)
        draft = _fallback_response(topic, knowledge)

    # Enforce the deterministic decision even if the model ignored the instruction —
    # never trust the LLM alone on a structural rule.
    if not has_process_info:
        draft.how_it_works = None

    final_response: FinalResponse = {
        "simple_explanation": draft.simple_explanation,
        "core_concepts": draft.core_concepts,
        "how_it_works": draft.how_it_works,
        "why_it_matters": draft.why_it_matters,
        "real_world_examples": draft.real_world_examples,
        "advantages": draft.advantages,
        "limitations": draft.limitations,
        "common_misconceptions": draft.common_misconceptions,
        "faq": [item.model_dump() for item in draft.faq],
        "summary": draft.summary,
        "references": [],  # filled in by Citation Formatter next
        "overall_confidence": knowledge["overall_confidence"],
        "completeness": knowledge["completeness"],
    }
    state["final_response"] = final_response
    return state