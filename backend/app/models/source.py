from typing import TypedDict, Literal, Optional


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