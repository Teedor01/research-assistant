# app/pipeline/synthesis/helpers.py
import uuid
from app.models.source import SourceDocument
from app.models.knowledge import Evidence


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def compute_confidence(evidence: list[Evidence], sources_by_id: dict[str, SourceDocument]) -> tuple[str, float]:
    """Deterministic confidence from evidence, not LLM self-assessment, per our
    research methodology design: 3+ corroborating high-credibility sources = high,
    1-2 or mixed credibility = medium, single low-credibility source = low."""
    supporting = [e for e in evidence if e["supports"]]
    if not supporting:
        return "low", 0.1

    credibilities = [
        sources_by_id[e["source_id"]]["credibility_score"] or 0.0
        for e in supporting
        if e["source_id"] in sources_by_id
    ]
    if not credibilities:
        return "low", 0.1

    avg_credibility = sum(credibilities) / len(credibilities)
    source_count = len(supporting)

    if source_count >= 3 and avg_credibility >= 0.6:
        return "high", min(1.0, 0.5 + 0.15 * source_count) * avg_credibility
    if source_count >= 2 or avg_credibility >= 0.6:
        return "medium", 0.5 * avg_credibility + 0.1 * source_count
    return "low", 0.3 * avg_credibility