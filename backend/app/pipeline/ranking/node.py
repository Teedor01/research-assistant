import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.state import ResearchState
from app.core.observability import observed_node

logger = logging.getLogger(__name__)

REDUNDANCY_SIMILARITY_THRESHOLD = 0.75


def _assign_ranks(active_sources: list) -> None:
    """Non-redundant sources rank first; within each tier, higher credibility first."""
    ordered = sorted(
        active_sources,
        key=lambda s: (s.get("is_redundant", False), -(s["credibility_score"] or 0.0)),
    )
    for i, source in enumerate(ordered, start=1):
        source["rank"] = i


@observed_node("dedup_ranking")
async def dedup_and_rank(state: ResearchState) -> ResearchState:
    active = [s for s in state["sources"] if s["status"] == "extracted"]

    if len(active) < 2:
        # Nothing to compare against — rank trivially and exit.
        _assign_ranks(active)
        return state

    texts = [s["extracted_text"] or "" for s in active]

    try:
        vectorizer = TfidfVectorizer(max_features=2000, stop_words="english")
        matrix = vectorizer.fit_transform(texts)
        similarity = cosine_similarity(matrix)
    except ValueError:
        # Can happen if all texts end up empty vocabulary after stopword removal —
        # rare, but degrade gracefully rather than crash the pipeline.
        logger.warning("TF-IDF vectorization failed, skipping semantic redundancy check")
        _assign_ranks(active)
        return state

    n = len(active)
    grouped = [False] * n
    redundant_count = 0

    for i in range(n):
        if grouped[i]:
            continue
        group_indices = [i]
        for j in range(i + 1, n):
            if grouped[j]:
                continue
            if similarity[i][j] >= REDUNDANCY_SIMILARITY_THRESHOLD:
                group_indices.append(j)
                grouped[j] = True

        if len(group_indices) > 1:
            # Keep the highest-credibility source in the group active;
            # flag the rest as redundant.
            group_indices.sort(
                key=lambda idx: active[idx]["credibility_score"] or 0.0, reverse=True
            )
            for idx in group_indices[1:]:
                active[idx]["is_redundant"] = True
                redundant_count += 1

    _assign_ranks(active)

    state["metrics"]["dedup_ranking"]["pages_discarded"] = redundant_count
    if state["research_log"]:
        state["research_log"][-1]["redundant_sources"] = redundant_count

    logger.info(
        "Dedup+Ranking: %d/%d sources flagged semantically redundant", redundant_count, n
    )
    return state