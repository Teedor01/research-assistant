from typing import TypedDict, Optional


class FinalResponse(TypedDict):
    """Shape of the Writer's output before persistence — the
    beginner-friendly explanation sections agreed on at the start."""
    simple_explanation: str
    core_concepts: str
    how_it_works: Optional[str]
    why_it_matters: str
    real_world_examples: str
    advantages: str
    limitations: str
    common_misconceptions: str
    faq: list[dict]
    summary: str
    references: list[dict]
    overall_confidence: float
    completeness: str