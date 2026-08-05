import logging
from app.models.state import ResearchState
from app.models.knowledge import ConflictingClaim, Claim
from app.core.observability import observed_node

logger = logging.getLogger(__name__)

AUTHORITY_GAP_THRESHOLD = 0.15  


def _resolve_conflict(conflict: ConflictingClaim, claims_by_id: dict[str, Claim],
                       sources_by_id: dict) -> None:
    involved = [claims_by_id[cid] for cid in conflict["conflicting_claim_ids"] if cid in claims_by_id]
    if len(involved) < 2:
        conflict["resolution"] = "unresolved"
        conflict["resolution_note"] = "One or more claims in this conflict could not be resolved."
        return

    def claim_authority(claim: Claim) -> float:
        credibilities = [
            sources_by_id[e["source_id"]]["credibility_score"] or 0.0
            for e in claim["evidence"] if e["source_id"] in sources_by_id
        ]
        return max(credibilities) if credibilities else 0.0

    scored = sorted(involved, key=claim_authority, reverse=True)
    top, runner_up = scored[0], scored[1]
    gap = claim_authority(top) - claim_authority(runner_up)

    # Majority check: does one claim simply have more corroborating sources?
    counts = [len(c["evidence"]) for c in involved]
    max_count = max(counts)
    majority_claims = [c for c, n in zip(involved, counts) if n == max_count]

    if gap >= AUTHORITY_GAP_THRESHOLD:
        conflict["resolution"] = "authority_wins"
        conflict["resolution_note"] = (
            f"Claim from higher-credibility source(s) favored (credibility gap: {gap:.2f})."
        )
    elif len(majority_claims) == 1 and max_count > min(counts):
        conflict["resolution"] = "consensus_majority"
        conflict["resolution_note"] = (
            f"Claim corroborated by more sources ({max_count} vs {min(counts)}) favored."
        )
    else:
        conflict["resolution"] = "unresolved"
        conflict["resolution_note"] = (
            "Sources are split roughly evenly across credibility and count — "
            "presented as genuine disagreement rather than resolved one way."
        )


def _compute_overall_confidence(claims: list[Claim]) -> float:
    if not claims:
        return 0.0
    total_weight = len(claims)
    weighted_sum = sum(c["confidence_score"] for c in claims)
    return round(weighted_sum / total_weight, 3)


@observed_node("confidence_scorer")
async def score_confidence(state: ResearchState) -> ResearchState:
    knowledge = state["structured_knowledge"]
    if knowledge is None:
        logger.warning("Confidence Scorer ran with no structured_knowledge — nothing to score")
        return state

    claims_by_id = {c["id"]: c for c in knowledge["claims"]}
    sources_by_id = {s["id"]: s for s in state["sources"]}

    unresolved_count = 0
    for conflict in knowledge["conflicts"]:
        if conflict["resolution"] == "unresolved":
            _resolve_conflict(conflict, claims_by_id, sources_by_id)
        if conflict["resolution"] == "unresolved":
            unresolved_count += 1

    knowledge["overall_confidence"] = _compute_overall_confidence(knowledge["claims"])

    logger.info(
        "Confidence Scorer: overall_confidence=%.2f, %d/%d conflicts still unresolved",
        knowledge["overall_confidence"], unresolved_count, len(knowledge["conflicts"]),
    )
    return state