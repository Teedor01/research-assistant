from typing import TypedDict, Literal
from pydantic import BaseModel, Field


class Intent(TypedDict):
    topic: str
    is_comparison: bool
    is_broad: bool
    query_type: Literal["explanation", "history", "comparison", "how_it_works"]
    learning_level: Literal["beginner", "intermediate", "advanced"]
    needs_multi_query: bool


class IntentSchema(BaseModel):
    """Pydantic model used to constrain/validate the LLM's structured output."""
    is_comparison: bool = Field(description="True if the user is asking to compare two or more things")
    is_broad: bool = Field(description="True if the topic spans many sub-concepts and can't be answered narrowly")
    query_type: Literal["explanation", "history", "comparison", "how_it_works"] = Field(
        description="The dominant shape of the request"
    )
    learning_level: Literal["beginner", "intermediate", "advanced"] = Field(
        description="Inferred from phrasing; default to beginner if unclear"
    )
    needs_multi_query: bool = Field(
        description="True unless this is a narrow, single-fact question answerable with one search"
    )