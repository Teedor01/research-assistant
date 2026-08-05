from app.models.intent import Intent

PLANNING_SYSTEM_PROMPT = """You are a search query planner inside a research agent.
Given a topic and its classified intent, produce the search queries needed to research it.

Rules:
- Queries must be short and specific, like something a person would type into a search
  engine, NOT full questions or sentences.
- If needs_multi_query is false, return exactly ONE query.
- If is_comparison is true, return one query per entity being compared, PLUS one
  head-to-head comparison query.
- If is_broad is true, return 3-5 queries covering genuinely distinct facets of the
  topic. Do not generate near-duplicate queries that would return overlapping results.
- If is_broad is false and it's not a comparison, 1-2 queries is usually enough.
- Never return more than 5 queries.

Respond with ONLY a JSON object matching the provided schema, no other text."""


def build_planning_prompt(topic: str, intent: Intent) -> str:
    return (
        f"Topic: {topic}\n\n"
        f"Intent classification:\n"
        f"- query_type: {intent['query_type']}\n"
        f"- is_comparison: {intent['is_comparison']}\n"
        f"- is_broad: {intent['is_broad']}\n"
        f"- needs_multi_query: {intent['needs_multi_query']}\n"
        f"- learning_level: {intent['learning_level']}\n\n"
        f"Produce the search queries."
    )