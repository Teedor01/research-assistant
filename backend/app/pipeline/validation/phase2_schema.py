from pydantic import BaseModel, Field


class ContentQualitySchema(BaseModel):
    content_score: float = Field(
        ge=0.0, le=1.0,
        description="0-1 score of content quality: substantiveness, apparent originality, "
                    "absence of spam/filler patterns. 1.0 = clearly authoritative, in-depth, "
                    "original content. 0.0 = thin, spammy, or low-value."
    )
    reasoning: str = Field(description="One brief sentence explaining the score")