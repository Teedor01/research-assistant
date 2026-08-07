from app.models.intent import Intent

SYNTHESIS_SYSTEM_PROMPT = """You are a knowledge extraction module inside a research agent.
Given the text of ONE source about a topic, extract structured knowledge from it.

Rules:
- Extract concepts: the key named ideas/entities/terms discussed. Use consistent, canonical
  names (e.g. always "Retrieval-Augmented Generation", not sometimes "RAG").
- Extract claims: atomic, standalone factual statements. Each claim must have a "type"
  (definition, advantage, limitation, example, misconception, fact, or process_step) and must
  reference which concept(s) it's about by name.
- Extract relationships between concepts only when the text explicitly supports one
  (is_a, part_of, requires, enables, contrasts_with, causes, precedes).
- Extract a process only if the text describes an actual ordered sequence of steps.
- Do not invent information not present in the text.
- Do not editorialize or add opinions — extract only what the source states.

Respond with ONLY a JSON object matching the provided schema, no other text."""


def build_synthesis_prompt(topic: str, source_title: str, source_text: str) -> str:
    
    truncated = source_text[:2500]
    return (
        f"Research topic: {topic}\n"
        f"Source title: {source_title}\n\n"
        f"Source text:\n{truncated}"
    )


CONFLICT_CHECK_SYSTEM_PROMPT = """You are comparing two claims about the same concept from
different sources. Determine whether they state the same underlying fact (possibly worded
differently) or whether they genuinely contradict each other.

Respond with ONLY a JSON object matching the provided schema, no other text."""


def build_conflict_check_prompt(claim_a: str, claim_b: str) -> str:
    return f"Claim A: {claim_a}\n\nClaim B: {claim_b}"