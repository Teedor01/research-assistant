import asyncio
import logging

from app.models.state import ResearchState
from app.providers.llm.base import LLMProvider, ModelTier
from app.pipeline.synthesis.schema import SourceKnowledge
from app.pipeline.synthesis.prompt import SYNTHESIS_SYSTEM_PROMPT, build_synthesis_prompt
from app.pipeline.synthesis.merge import merge_into_knowledge, _empty_knowledge
from app.core.observability import observed_node

logger = logging.getLogger(__name__)


async def _extract_from_source(source: dict, topic: str, llm: LLMProvider) -> SourceKnowledge | None:
    try:
        response = await llm.generate_structured(
            system_prompt=SYNTHESIS_SYSTEM_PROMPT,
            user_prompt=build_synthesis_prompt(topic, source["title"], source["extracted_text"] or ""),
            response_model=SourceKnowledge,
            tier=ModelTier.REASONING,  
            temperature=0.0,
        )
        return response.data
    except ValueError as e:
        logger.warning("Synthesis extraction failed for source_id=%s: %s", source["id"], e)
        return None


@observed_node("knowledge_synthesizer")
async def synthesize_knowledge(state: ResearchState, *, llm: LLMProvider) -> ResearchState:
    topic = state["topic"]
    candidates = [
        s for s in state["sources"]
        if s["status"] == "extracted" and not s.get("is_redundant", False)
    ]

    if state["structured_knowledge"] is None:
        state["structured_knowledge"] = _empty_knowledge()
    knowledge = state["structured_knowledge"]

    extractions = await asyncio.gather(
        *(_extract_from_source(s, topic, llm) for s in candidates)
    )

    new_facts_before = len(knowledge["claims"])

   
    for source, extraction in zip(candidates, extractions):
        if extraction is None:
            continue
        await merge_into_knowledge(extraction, source, knowledge, llm)

    new_facts_added = len(knowledge["claims"]) - new_facts_before
    state["metrics"]["knowledge_synthesizer"]["pages_extracted"] = sum(1 for e in extractions if e is not None)
    state["metrics"]["knowledge_synthesizer"]["pages_failed"] = sum(1 for e in extractions if e is None)

    if state["research_log"]:
        state["research_log"][-1]["new_facts_added"] = new_facts_added

    logger.info(
        "Synthesis: %d sources processed, %d new claims added, %d concepts, %d conflicts total",
        len(candidates), new_facts_added, len(knowledge["concepts"]), len(knowledge["conflicts"]),
    )
    return state