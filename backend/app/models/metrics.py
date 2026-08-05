from typing import TypedDict


class NodeMetrics(TypedDict, total=False):
    duration_ms: float
    tokens_used: int
    search_results: int
    pages_extracted: int
    pages_discarded: int
    pages_failed: int


class RoundSummary(TypedDict):
    round_number: int
    queries_run: list[str]
    sources_found: int
    new_facts_added: int
    redundant_sources: int