from app.models.knowledge import StructuredKnowledge, Claim

MAX_CLAIMS_IN_CONTEXT = 60  


def _confidence_tag(claim: Claim, unresolved_concept_ids: set[str]) -> str:
    if any(cid in unresolved_concept_ids for cid in claim["concept_ids"]):
        return "[disputed — sources disagree]"
    if claim["confidence"] == "high":
        return "[high confidence]"
    if claim["confidence"] == "low":
        return "[low confidence — limited sourcing]"
    return "[medium confidence]"


def build_writer_context(knowledge: StructuredKnowledge) -> str:
    unresolved_concept_ids = {
        c["concept_id"] for c in knowledge["conflicts"] if c["resolution"] == "unresolved"
    }

    # Prioritize best-evidenced claims first, in case we need to truncate.
    ranked_claims = sorted(
        knowledge["claims"], key=lambda c: c["confidence_score"], reverse=True
    )[:MAX_CLAIMS_IN_CONTEXT]

    claims_by_concept: dict[str, list[Claim]] = {}
    for claim in ranked_claims:
        for cid in claim["concept_ids"]:
            claims_by_concept.setdefault(cid, []).append(claim)

    lines = []
    for concept in knowledge["concepts"]:
        concept_claims = claims_by_concept.get(concept["id"], [])
        if not concept_claims:
            continue
        lines.append(f"\n## {concept['name']}")
        for claim in concept_claims:
            tag = _confidence_tag(claim, unresolved_concept_ids)
            lines.append(f"- ({claim['type']}) {claim['text']} {tag}")

    if knowledge["relationships"]:
        lines.append("\n## Relationships between concepts")
        for rel in knowledge["relationships"]:
            from_name = next((c["name"] for c in knowledge["concepts"] if c["id"] == rel["from_concept_id"]), "?")
            to_name = next((c["name"] for c in knowledge["concepts"] if c["id"] == rel["to_concept_id"]), "?")
            lines.append(f"- {from_name} {rel['type']} {to_name}: {rel['description']}")

    if knowledge["processes"]:
        lines.append("\n## Processes")
        for process in knowledge["processes"]:
            lines.append(f"\n{process['name']}:")
            claims_by_id = {c["id"]: c for c in knowledge["claims"]}
            for step in sorted(process["steps"], key=lambda s: s["order"]):
                step_claim = claims_by_id.get(step["claim_id"])
                if step_claim:
                    lines.append(f"  {step['order']}. {step_claim['text']}")

    return "\n".join(lines) if lines else "No structured knowledge available."