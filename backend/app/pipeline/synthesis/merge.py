# app/pipeline/synthesis/merge.py
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.knowledge import StructuredKnowledge, Concept, Claim, Relationship, Process, ProcessStep, ConflictingClaim, Evidence
from app.models.source import SourceDocument
from app.pipeline.synthesis.schema import SourceKnowledge
from app.pipeline.synthesis.helpers import new_id, compute_confidence
from app.providers.llm.base import LLMProvider, ModelTier
from app.pipeline.synthesis.schema import ConflictCheckResult
from app.pipeline.synthesis.prompt import CONFLICT_CHECK_SYSTEM_PROMPT, build_conflict_check_prompt

logger = logging.getLogger(__name__)

CORROBORATION_THRESHOLD = 0.55
AMBIGUOUS_FLOOR = 0.25


def _empty_knowledge() -> StructuredKnowledge:
    return {
        "concepts": [], "relationships": [], "claims": [], "processes": [],
        "conflicts": [], "overall_confidence": 0.0, "completeness": "partial",
    }


def _resolve_concept_id(name: str, knowledge: StructuredKnowledge) -> str | None:
    normalized = name.strip().lower()
    for concept in knowledge["concepts"]:
        if concept["name"].strip().lower() == normalized:
            return concept["id"]
        if any(a.strip().lower() == normalized for a in concept["aliases"]):
            return concept["id"]
    return None


def _merge_concepts(source_knowledge: SourceKnowledge, knowledge: StructuredKnowledge) -> dict[str, str]:
    """Returns a map of extracted concept name -> resolved global concept_id,
    creating new Concept entries for anything not already in the graph."""
    name_to_id: dict[str, str] = {}
    for extracted in source_knowledge.concepts:
        existing_id = _resolve_concept_id(extracted.name, knowledge)
        if existing_id:
            # Merge any new aliases into the existing concept
            concept = next(c for c in knowledge["concepts"] if c["id"] == existing_id)
            for alias in extracted.aliases:
                if alias not in concept["aliases"]:
                    concept["aliases"].append(alias)
            name_to_id[extracted.name] = existing_id
        else:
            new_concept: Concept = {
                "id": new_id("concept"),
                "name": extracted.name,
                "aliases": extracted.aliases,
                "definition_claim_id": None,
                "complexity_level": "beginner",  # refined later if needed
            }
            knowledge["concepts"].append(new_concept)
            name_to_id[extracted.name] = new_concept["id"]
    return name_to_id


def _find_best_match(claim_text: str, candidates: list[Claim]) -> tuple[Claim | None, float]:
    if not candidates:
        return None, 0.0
    texts = [c["text"] for c in candidates] + [claim_text]
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(texts)
        sims = cosine_similarity(matrix[-1], matrix[:-1])[0]
    except ValueError:
        return None, 0.0
    best_idx = sims.argmax()
    return candidates[best_idx], float(sims[best_idx])


async def _merge_claims(
    source_knowledge: SourceKnowledge,
    concept_name_to_id: dict[str, str],
    knowledge: StructuredKnowledge,
    source: SourceDocument,
    llm: LLMProvider,
) -> None:
    for extracted in source_knowledge.claims:
        concept_ids = [
            concept_name_to_id[name] for name in extracted.concept_names
            if name in concept_name_to_id
        ]
        if not concept_ids:
            continue  # claim references a concept we failed to resolve — skip rather than guess

        new_evidence: Evidence = {
            "source_id": source["id"],
            "supports": True,
            "excerpt_paraphrase": extracted.text[:200],
        }

        # Only compare against claims of the same type sharing at least one concept —
        # narrows the candidate pool before running similarity.
        candidates = [
            c for c in knowledge["claims"]
            if c["type"] == extracted.type and set(c["concept_ids"]) & set(concept_ids)
        ]
        best_match, similarity = _find_best_match(extracted.text, candidates)

        if best_match and similarity >= CORROBORATION_THRESHOLD:
            best_match["evidence"].append(new_evidence)
            confidence_label, confidence_score = compute_confidence(
                best_match["evidence"], {source["id"]: source}
            )
            best_match["confidence"] = confidence_label
            best_match["confidence_score"] = confidence_score
            continue

        if best_match and AMBIGUOUS_FLOOR <= similarity < CORROBORATION_THRESHOLD:
            result = await _check_conflict(best_match["text"], extracted.text, llm)
            if result and result.is_same_fact:
                best_match["evidence"].append(new_evidence)
                confidence_label, confidence_score = compute_confidence(
                    best_match["evidence"], {source["id"]: source}
                )
                best_match["confidence"] = confidence_label
                best_match["confidence_score"] = confidence_score
                continue
            if result and result.contradicts:
                new_claim = _new_claim(extracted, concept_ids, new_evidence)
                knowledge["claims"].append(new_claim)
                knowledge["conflicts"].append({
                    "id": new_id("conflict"),
                    "concept_id": concept_ids[0],
                    "conflicting_claim_ids": [best_match["id"], new_claim["id"]],
                    "resolution": "unresolved",
                    "resolution_note": "Flagged during synthesis; resolved by credibility comparison downstream.",
                })
                continue

        # Low similarity, or ambiguous check was inconclusive — treat as a new claim.
        new_claim = _new_claim(extracted, concept_ids, new_evidence)
        knowledge["claims"].append(new_claim)


def _new_claim(extracted, concept_ids: list[str], evidence: Evidence) -> Claim:
    return {
        "id": new_id("claim"),
        "type": extracted.type,
        "concept_ids": concept_ids,
        "text": extracted.text,
        "evidence": [evidence],
        "confidence": "low",       # single-source by definition at creation
        "confidence_score": 0.3,
    }


async def _check_conflict(claim_a: str, claim_b: str, llm: LLMProvider) -> ConflictCheckResult | None:
    try:
        response = await llm.generate_structured(
            system_prompt=CONFLICT_CHECK_SYSTEM_PROMPT,
            user_prompt=build_conflict_check_prompt(claim_a, claim_b),
            response_model=ConflictCheckResult,
            tier=ModelTier.FAST,
            temperature=0.0,
        )
        return response.data
    except ValueError as e:
        logger.warning("Conflict check failed, treating claims as distinct. Error: %s", e)
        return None


def _merge_relationships(source_knowledge: SourceKnowledge, concept_name_to_id: dict[str, str],
                          knowledge: StructuredKnowledge, source: SourceDocument) -> None:
    for extracted in source_knowledge.relationships:
        from_id = concept_name_to_id.get(extracted.from_concept)
        to_id = concept_name_to_id.get(extracted.to_concept)
        if not from_id or not to_id:
            continue
        duplicate = any(
            r["from_concept_id"] == from_id and r["to_concept_id"] == to_id and r["type"] == extracted.type
            for r in knowledge["relationships"]
        )
        if duplicate:
            continue
        knowledge["relationships"].append({
            "id": new_id("rel"),
            "from_concept_id": from_id,
            "to_concept_id": to_id,
            "type": extracted.type,
            "description": extracted.description,
            "evidence": [{"source_id": source["id"], "supports": True, "excerpt_paraphrase": extracted.description[:200]}],
            "confidence": "medium",
        })


def _merge_processes(source_knowledge: SourceKnowledge, concept_name_to_id: dict[str, str],
                      knowledge: StructuredKnowledge) -> None:
    for extracted in source_knowledge.processes:
        concept_id = concept_name_to_id.get(extracted.concept_name)
        if not concept_id:
            continue
        if any(p["name"] == extracted.name and p["concept_id"] == concept_id for p in knowledge["processes"]):
            continue  # naive dedup — good enough given processes are less common than claims

        steps: list[ProcessStep] = []
        for order, step_text in enumerate(extracted.ordered_steps, start=1):
            step_claim: Claim = {
                "id": new_id("claim"),
                "type": "process_step",
                "concept_ids": [concept_id],
                "text": step_text,
                "evidence": [],
                "confidence": "medium",
                "confidence_score": 0.5,
            }
            knowledge["claims"].append(step_claim)
            steps.append({"order": order, "claim_id": step_claim["id"]})

        knowledge["processes"].append({
            "id": new_id("process"), "name": extracted.name,
            "concept_id": concept_id, "steps": steps,
        })


async def merge_into_knowledge(
    source_knowledge: SourceKnowledge,
    source: SourceDocument,
    knowledge: StructuredKnowledge,
    llm: LLMProvider,
) -> None:
    """Mutates `knowledge` in place with everything extracted from one source."""
    concept_name_to_id = _merge_concepts(source_knowledge, knowledge)
    await _merge_claims(source_knowledge, concept_name_to_id, knowledge, source, llm)
    _merge_relationships(source_knowledge, concept_name_to_id, knowledge, source)
    _merge_processes(source_knowledge, concept_name_to_id, knowledge)