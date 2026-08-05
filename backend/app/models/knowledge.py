from typing import TypedDict, Literal, Optional


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