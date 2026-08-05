from pydantic import BaseModel, Field


class GapItem(BaseModel):
    gap_description: str = Field(description="What specific information is missing")
    suggested_query: str = Field(description="A concrete, search-engine-style query to fill this gap")


class GapAnalysisSchema(BaseModel):
    gaps: list[GapItem] = Field(
        default_factory=list,
        description="List of specific, concrete gaps. Empty list if coverage is already sufficient. "
                     "Do not invent gaps just to have something to report."
    )