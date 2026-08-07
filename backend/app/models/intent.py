from typing import TypedDict, Literal


class Intent(TypedDict):
    topic: str
    is_comparison: bool
    is_broad: bool
    query_type: Literal["explanation", "history", "comparison", "how_it_works"]
    learning_level: Literal["beginner", "intermediate", "advanced"]
    needs_multi_query: bool