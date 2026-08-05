from typing import Optional
from pydantic import BaseModel, Field


class FAQItem(BaseModel):
    question: str
    answer: str


class WriterOutputSchema(BaseModel):
    simple_explanation: str = Field(description="2-4 paragraphs, plain-language overview")
    core_concepts: str = Field(description="Key terms and ideas, defined clearly")
    how_it_works: Optional[str] = Field(
        default=None,
        description="Step-by-step breakdown. MUST be null if no process information was provided."
    )
    why_it_matters: str
    real_world_examples: str
    advantages: str
    limitations: str
    common_misconceptions: str
    faq: list[FAQItem] = Field(default_factory=list, description="2-5 relevant questions with answers")
    summary: str = Field(description="2-3 sentence wrap-up")