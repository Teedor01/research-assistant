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