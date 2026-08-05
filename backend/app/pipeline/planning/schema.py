from pydantic import BaseModel, Field


class QueryPlanSchema(BaseModel):
    sub_queries: list[str] = Field(
        description="1 to 5 concrete, search-engine-style queries. Short and specific, "
                     "the way a person would actually type them into a search box — "
                     "not full sentences or questions."
    )