import logging
from app.models.state import ResearchState
from app.models.response import FinalResponse
from app.core.observability import observed_node

logger = logging.getLogger(__name__)


def _used_source_ids(knowledge) -> set[str]:
    """A source counts as 'used' only if it appears as evidence on at least one
    claim or relationship in the final knowledge graph — not merely fetched."""
    ids: set[str] = set()
    for claim in knowledge["claims"]:
        for evidence in claim["evidence"]:
            ids.add(evidence["source_id"])
    for rel in knowledge["relationships"]:
        for evidence in rel["evidence"]:
            ids.add(evidence["source_id"])
    return ids


@observed_node("citation_formatter")
async def format_citations(state: ResearchState) -> ResearchState:
    knowledge = state["structured_knowledge"]
    final_response: FinalResponse = state["final_response"]

    if knowledge is None or final_response is None:
        logger.warning("Citation Formatter ran with missing knowledge or final_response")
        return state

    used_ids = _used_source_ids(knowledge)
    sources_by_id = {s["id"]: s for s in state["sources"]}

    references = []
    for source_id in used_ids:
        source = sources_by_id.get(source_id)
        if source is None:
            continue 
        references.append({
            "title": source["title"] or source["url"],
            "url": source["url"],
            "domain": source["domain"],
            "credibility_score": source["credibility_score"] or 0.0,
        })

    references.sort(key=lambda r: r["credibility_score"], reverse=True)

    final_response["references"] = references
    state["final_response"] = final_response

    logger.info(
        "Citation Formatter: %d sources cited out of %d total fetched",
        len(references), len(state["sources"]),
    )
    return state