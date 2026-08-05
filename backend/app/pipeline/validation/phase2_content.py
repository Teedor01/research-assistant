import re
import logging
from app.models.state import ResearchState
from app.providers.llm.base import LLMProvider, ModelTier
from app.pipeline.validation.phase2_schema import ContentQualitySchema
from app.core.observability import observed_node

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 200  


SHORT_TEXT_CEILING = 500       
LLM_REVIEW_LOW = 0.35          
LLM_REVIEW_HIGH = 0.65

DUPLICATE_SIMILARITY_THRESHOLD = 0.85  

DOMAIN_WEIGHT = 0.4
CONTENT_WEIGHT = 0.6

DISCARD_CONTENT_FLOOR = 0.1  # only genuinely worthless content gets discarded here


def _heuristic_content_score(text: str) -> float:
    """Cheap, fast pass. No network/LLM calls. Returns a 0-1 estimate."""
    length = len(text)
    if length < MIN_TEXT_LENGTH:
        return 0.0  

    
    length_score = min(length / SHORT_TEXT_CEILING, 1.0)

    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        structure_score = 0.0
    else:
        avg_sentence_len = sum(len(s.split()) for s in sentences) / len(sentences)
        
        if 8 <= avg_sentence_len <= 35:
            structure_score = 1.0
        else:
            structure_score = 0.4

    
    words = re.findall(r'\b\w+\b', text.lower())
    if words:
        from collections import Counter
        counts = Counter(words)
        most_common_ratio = counts.most_common(1)[0][1] / len(words)
        stuffing_score = 1.0 if most_common_ratio < 0.04 else 0.3
    else:
        stuffing_score = 0.0

    return round(0.4 * length_score + 0.4 * structure_score + 0.2 * stuffing_score, 3)


def _text_similarity(a: str, b: str) -> float:
    """Cheap shingle-overlap similarity for duplicate detection. Not semantic —
    just catches near-identical republished text. Full semantic redundancy is
    handled later, against structured_knowledge, in the Synthesizer stage."""
    def shingles(text: str, n: int = 8) -> set:
        words = text.lower().split()
        return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}

    sa, sb = shingles(a), shingles(b)
    if not sa or not sb:
        return 0.0
    intersection = len(sa & sb)
    union = len(sa | sb)
    return intersection / union if union else 0.0


async def _llm_content_review(text: str, llm: LLMProvider) -> float:
    """Only called for heuristic scores in the ambiguous middle band."""
    system_prompt = (
        "You are a content quality reviewer. Given an excerpt of extracted web page text, "
        "rate its quality as a research source. Favor substantive, well-explained, apparently "
        "original content. Penalize thin summaries, SEO filler, and listicle-style shallow content."
    )
    truncated = text[:3000]  
    try:
        response = await llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=f"Rate this content:\n\n{truncated}",
            response_model=ContentQualitySchema,
            tier=ModelTier.FAST,
            temperature=0.0,
        )
        return response.data.content_score
    except ValueError as e:
        logger.warning("LLM content review failed, falling back to heuristic score. Error: %s", e)
        return None


@observed_node("source_validation_phase2")
async def validate_content(state: ResearchState, *, llm: LLMProvider) -> ResearchState:
    extracted = [s for s in state["sources"] if s["status"] == "extracted"]
    discarded_count = 0
    llm_reviewed_count = 0

    for source in extracted:
        text = source["extracted_text"] or ""
        heuristic_score = _heuristic_content_score(text)

        
        if LLM_REVIEW_LOW <= heuristic_score <= LLM_REVIEW_HIGH:
            llm_score = await _llm_content_review(text, llm)
            content_score = llm_score if llm_score is not None else heuristic_score
            if llm_score is not None:
                llm_reviewed_count += 1
        else:
            content_score = heuristic_score

        
        for other in extracted:
            if other is source or not other.get("content_score"):
                continue
            other_text = other["extracted_text"] or ""
            if _text_similarity(text, other_text) >= DUPLICATE_SIMILARITY_THRESHOLD:
                content_score = min(content_score, 0.2)
                source["discard_reason"] = f"near-duplicate of source {other['id']}"
                break

        source["content_score"] = content_score
        source["credibility_score"] = round(
            DOMAIN_WEIGHT * source["domain_score"] + CONTENT_WEIGHT * content_score, 3
        )

        if content_score < DISCARD_CONTENT_FLOOR:
            source["status"] = "discarded"
            if not source["discard_reason"]:
                source["discard_reason"] = f"content quality too low ({content_score:.2f})"
            discarded_count += 1

    state["metrics"]["source_validation_phase2"]["pages_discarded"] = discarded_count
    logger.info(
        "Phase 2 content validation: %d sources scored, %d LLM-reviewed, %d discarded",
        len(extracted), llm_reviewed_count, discarded_count,
    )
    return state