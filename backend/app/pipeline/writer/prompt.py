from app.models.intent import Intent

LEARNING_LEVEL_GUIDANCE = {
    "beginner": "Write for someone with no prior background. Define any technical term the "
                "first time it's used. Prefer short sentences and concrete language.",
    "intermediate": "Assume basic familiarity with the general domain. You don't need to "
                     "define foundational terms, but still explain specialized ones.",
    "advanced": "Assume strong domain familiarity. Prioritize precision and depth over "
                "hand-holding explanation.",
}

WRITER_SYSTEM_PROMPT = """You are the writer module inside a research agent. You will be given
structured, pre-verified knowledge about a topic. Your ONLY job is to explain this knowledge
clearly — you must NOT introduce any fact, example, or claim that isn't present in the provided
knowledge below.

Every claim below is tagged with a confidence level. Reflect that honestly in your phrasing:
- [high confidence] claims can be stated directly.
- [medium confidence] claims should be stated with mild hedging ("generally", "typically").
- [low confidence] claims should be clearly hedged ("some sources suggest", "less well-documented").
- [disputed] claims must be presented as genuine disagreement — do not silently pick a side.

Respond with ONLY a JSON object matching the provided schema, no other text."""


def build_writer_prompt(topic: str, intent: Intent, context: str, has_process_info: bool) -> str:
    level_guidance = LEARNING_LEVEL_GUIDANCE[intent["learning_level"]]
    comparison_note = (
        "This is a comparison — structure core_concepts, advantages, and limitations to address "
        "each thing being compared clearly, side by side where natural.\n"
        if intent["is_comparison"] else ""
    )
    process_note = (
        "Process/step information IS available below — write a how_it_works section."
        if has_process_info else
        "No process/step information is available — you MUST return null for how_it_works. "
        "Do not invent a sequence of steps."
    )

    return (
        f"Topic: {topic}\n\n"
        f"Reading level: {intent['learning_level']}. {level_guidance}\n"
        f"{comparison_note}"
        f"{process_note}\n\n"
        f"Structured knowledge:\n{context}\n\n"
        f"Write the explanation."
    )