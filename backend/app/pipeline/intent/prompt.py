INTENT_SYSTEM_PROMPT = """You are an intent classification module inside a research agent.
Given a user's topic or question, classify it according to the schema provided.
Be decisive. If ambiguous, prefer is_broad=true and needs_multi_query=true — it is safer
to over-research than under-research.

Respond with ONLY a JSON object matching this exact structure, no other text:
{
  "is_comparison": boolean,
  "is_broad": boolean,
  "query_type": "explanation" | "history" | "comparison" | "how_it_works",
  "learning_level": "beginner" | "intermediate" | "advanced",
  "needs_multi_query": boolean
}"""


def build_intent_prompt(topic: str) -> str:
    return f"Classify this topic:\n\n{topic}"