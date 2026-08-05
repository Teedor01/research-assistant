from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)

    @field_validator("topic")
    @classmethod
    def topic_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("topic cannot be blank or whitespace-only")
        return stripped


class FAQItemResponse(BaseModel):
    question: str
    answer: str


class ReferenceResponse(BaseModel):
    title: str
    url: str
    domain: str
    credibility_score: float


class ResearchResponse(BaseModel):
    """Mirrors FinalResponse exactly — this is the contract the frontend
    brief documents in §3.2. Keep these in sync if either changes."""
    topic: str
    simple_explanation: str
    core_concepts: str
    how_it_works: str | None
    why_it_matters: str
    real_world_examples: str
    advantages: str
    limitations: str
    common_misconceptions: str
    faq: list[FAQItemResponse]
    summary: str
    references: list[ReferenceResponse]
    overall_confidence: float
    completeness: str


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail