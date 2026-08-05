from app.models.knowledge import StructuredKnowledge

ALL_CLAIM_TYPES = {"definition", "advantage", "limitation", "example",
                    "misconception", "fact", "process_step"}


def summarize_knowledge(knowledge: StructuredKnowledge) -> str:
    """Compact, human-readable summary for the gap-identification prompt —
    deliberately NOT the raw graph, to keep the prompt small and cheap."""
    if not knowledge["concepts"]:
        return "No knowledge gathered yet."

    lines = []
    for concept in knowledge["concepts"]:
        claim_types_present = {
            c["type"] for c in knowledge["claims"] if concept["id"] in c["concept_ids"]
        }
        missing = ALL_CLAIM_TYPES - claim_types_present
        line = f"- {concept['name']}: has {', '.join(sorted(claim_types_present)) or 'nothing'}"
        if missing:
            line += f" | missing: {', '.join(sorted(missing))}"
        lines.append(line)

    if knowledge["conflicts"]:
        unresolved = [c for c in knowledge["conflicts"] if c["resolution"] == "unresolved"]
        if unresolved:
            lines.append(f"\n{len(unresolved)} unresolved conflicting claim(s) present.")

    return "\n".join(lines)