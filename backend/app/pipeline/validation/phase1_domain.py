import logging
from app.models.state import ResearchState
from app.core.observability import observed_node
from app.core.domain_lists import (
    HIGH_AUTHORITY_SUFFIXES,
    HIGH_AUTHORITY_DOMAINS,
    KNOWN_TECHNICAL_DOMAINS,
    LOW_QUALITY_DOMAIN_PATTERNS,
)

logger = logging.getLogger(__name__)

DISCARD_THRESHOLD = 0.2

SCORE_HIGH_AUTHORITY = 0.9
SCORE_KNOWN_TECHNICAL = 0.75
SCORE_NEUTRAL = 0.5
SCORE_LOW_QUALITY = 0.15


def _score_domain(domain: str) -> float:
    if any(domain.endswith(suffix) for suffix in HIGH_AUTHORITY_SUFFIXES):
        return SCORE_HIGH_AUTHORITY
    if domain in HIGH_AUTHORITY_DOMAINS:
        return SCORE_HIGH_AUTHORITY
    if domain in KNOWN_TECHNICAL_DOMAINS:
        return SCORE_KNOWN_TECHNICAL
    if any(pattern in domain for pattern in LOW_QUALITY_DOMAIN_PATTERNS):
        return SCORE_LOW_QUALITY
    return SCORE_NEUTRAL


@observed_node("source_validation_phase1")
async def validate_domains(state: ResearchState) -> ResearchState:
    discarded_count = 0

    for source in state["sources"]:
        if source["status"] != "pending":
            continue  

        score = _score_domain(source["domain"])
        source["domain_score"] = score

        if score < DISCARD_THRESHOLD:
            source["status"] = "discarded"
            source["discard_reason"] = f"low domain score ({score:.2f}) — likely low-quality source"
            discarded_count += 1

    state["metrics"]["source_validation_phase1"]["pages_discarded"] = discarded_count
    logger.info("Phase 1 domain validation discarded %d/%d sources", discarded_count, len(state["sources"]))
    return state