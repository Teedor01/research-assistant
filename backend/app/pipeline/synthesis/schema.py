# app/pipeline/synthesis/schema.py
from typing import Literal
from pydantic import BaseModel, Field

ClaimType = Literal["definition", "advantage", "limitation", "example",
                     "misconception", "fact", "process_step"]
RelationshipType = Literal["is_a", "part_of", "requires", "enables",
                            "contrasts_with", "causes", "precedes"]


class ExtractedConcept(BaseModel):
    name: str = Field(description="Canonical name of the concept")
    aliases: list[str] = Field(default_factory=list, description="Alternate names/abbreviations used in the text")


class ExtractedClaim(BaseModel):
    type: ClaimType
    concept_names: list[str] = Field(description="Which extracted concept(s) this claim is about, by name")
    text: str = Field(description="The claim itself, written as a clear standalone statement")


class ExtractedRelationship(BaseModel):
    from_concept: str
    to_concept: str
    type: RelationshipType
    description: str


class ExtractedProcess(BaseModel):
    name: str
    concept_name: str
    ordered_steps: list[str] = Field(description="Step descriptions in execution order")


class SourceKnowledge(BaseModel):
    concepts: list[ExtractedConcept] = Field(default_factory=list)
    claims: list[ExtractedClaim] = Field(default_factory=list)
    relationships: list[ExtractedRelationship] = Field(default_factory=list)
    processes: list[ExtractedProcess] = Field(default_factory=list)


class ConflictCheckResult(BaseModel):
    is_same_fact: bool = Field(description="True if both claims state the same underlying fact, just worded differently")
    contradicts: bool = Field(description="True if the claims genuinely disagree with each other")