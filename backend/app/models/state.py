
from typing import TypedDict, Literal, Optional
from typing import TypedDict, Optional

from app.models.intent import Intent
from app.models.source import SourceDocument
from app.models.knowledge import StructuredKnowledge
from app.models.metrics import NodeMetrics, RoundSummary
from app.models.response import FinalResponse


class ResearchState(TypedDict):
    topic: str
    intent: Optional[Intent]
    sub_queries: list[str]
    initial_sub_queries: list[str]
    sources: list[SourceDocument]
    structured_knowledge: Optional[StructuredKnowledge]
    final_response: Optional[FinalResponse]
    round_number: int
    started_at: float 
    research_log: list[RoundSummary]
    metrics: dict[str, NodeMetrics]


class SourceDocument(TypedDict):
    id: str
    url: str
    domain: str
    title: str
    published_date: Optional[str]
    extracted_text: Optional[str]
    domain_score: float
    content_score: Optional[float]
    credibility_score: Optional[float]
    status: Literal["pending", "extracted", "failed", "discarded"]
    discard_reason: Optional[str]


class Intent(TypedDict):
    topic: str
    is_comparison: bool
    is_broad: bool
    query_type: Literal["explanation", "history", "comparison", "how_it_works"]
    learning_level: Literal["beginner", "intermediate", "advanced"]
    needs_multi_query: bool


class Evidence(TypedDict):
    source_id: str
    supports: bool
    excerpt_paraphrase: str


class Claim(TypedDict):
    id: str
    type: Literal["definition", "advantage", "limitation", "example",
                   "misconception", "fact", "process_step"]
    concept_ids: list[str]
    text: str
    evidence: list[Evidence]
    confidence: Literal["high", "medium", "low"]
    confidence_score: float


class Concept(TypedDict):
    id: str
    name: str
    aliases: list[str]
    definition_claim_id: Optional[str]
    complexity_level: Literal["beginner", "intermediate", "advanced"]


class Relationship(TypedDict):
    id: str
    from_concept_id: str
    to_concept_id: str
    type: Literal["is_a", "part_of", "requires", "enables",
                   "contrasts_with", "causes", "precedes"]
    description: str
    evidence: list[Evidence]
    confidence: Literal["high", "medium", "low"]


class ProcessStep(TypedDict):
    order: int
    claim_id: str


class Process(TypedDict):
    id: str
    name: str
    concept_id: str
    steps: list[ProcessStep]


class ConflictingClaim(TypedDict):
    id: str
    concept_id: str
    conflicting_claim_ids: list[str]
    resolution: Literal["consensus_majority", "authority_wins", "unresolved"]
    resolution_note: str


class StructuredKnowledge(TypedDict):
    concepts: list[Concept]
    relationships: list[Relationship]
    claims: list[Claim]
    processes: list[Process]
    conflicts: list[ConflictingClaim]
    overall_confidence: float
    completeness: Literal["complete", "partial"]


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


class ResearchState(TypedDict):
    topic: str
    intent: Optional[Intent]
    sub_queries: list[str]
    sources: list[SourceDocument]
    structured_knowledge: Optional[StructuredKnowledge]
    final_response: Optional[dict]
    round_number: int
    research_log: list[RoundSummary]
    metrics: dict[str, NodeMetrics]