from functools import partial
from langgraph.graph import StateGraph, END

from app.models.state import ResearchState
from app.providers.llm.base import LLMProvider
from app.providers.search.base import SearchProvider
from app.providers.extraction.base import ExtractionProvider
from app.core.config import Settings

from app.pipeline.intent.analyzer import analyze_intent
from app.pipeline.planning.planner import plan_queries
from app.pipeline.search.node import run_search
from app.pipeline.validation.phase1_domain import validate_domains
from app.pipeline.extraction.node import run_extraction
from app.pipeline.validation.phase2_content import validate_content
from app.pipeline.ranking.node import dedup_and_rank
from app.pipeline.synthesis.node import synthesize_knowledge
from app.pipeline.gaps.node import identify_gaps, should_continue_research
from app.pipeline.confidence.node import score_confidence
from app.pipeline.writer.node import write_response
from app.pipeline.citations.node import format_citations


def build_research_graph(
    *,
    llm: LLMProvider,
    search_provider: SearchProvider,
    extraction_provider: ExtractionProvider,
    settings: Settings,
):
    """Wires every pipeline node into one compiled LangGraph. Dependencies are
    bound here via functools.partial, so node functions themselves never
    import or construct a concrete provider — matches the interface boundary
    we've maintained since the LLM provider design."""
    graph = StateGraph(ResearchState)

    graph.add_node("intent_analyzer", partial(analyze_intent, llm=llm))
    graph.add_node("query_planner", partial(plan_queries, llm=llm))
    graph.add_node("search", partial(run_search, search_provider=search_provider, settings=settings))
    graph.add_node("source_validation_phase1", validate_domains)
    graph.add_node("extraction", partial(run_extraction, extraction_provider=extraction_provider, settings=settings))
    graph.add_node("source_validation_phase2", partial(validate_content, llm=llm))
    graph.add_node("dedup_ranking", dedup_and_rank)
    graph.add_node("knowledge_synthesizer", partial(synthesize_knowledge, llm=llm))
    graph.add_node("gap_identifier", partial(identify_gaps, llm=llm, settings=settings))
    graph.add_node("confidence_scorer", score_confidence)
    graph.add_node("writer", partial(write_response, llm=llm))
    graph.add_node("citation_formatter", format_citations)

    graph.set_entry_point("intent_analyzer")

    # Linear spine through the first research pass
    graph.add_edge("intent_analyzer", "query_planner")
    graph.add_edge("query_planner", "search")
    graph.add_edge("search", "source_validation_phase1")
    graph.add_edge("source_validation_phase1", "extraction")
    graph.add_edge("extraction", "source_validation_phase2")
    graph.add_edge("source_validation_phase2", "dedup_ranking")
    graph.add_edge("dedup_ranking", "knowledge_synthesizer")
    graph.add_edge("knowledge_synthesizer", "gap_identifier")

    # The loop: gap_identifier's own should_continue_research function decides
    # whether to route back to "search" (new round) or forward to "confidence_scorer"
    # (research is done). This is the exact conditional edge we designed back
    # when we built the Gap Identifier.
    graph.add_conditional_edges(
        "gap_identifier",
        should_continue_research,
        {
            "search": "search",
            "confidence_scorer": "confidence_scorer",
        },
    )

  
    graph.add_edge("confidence_scorer", "writer")
    graph.add_edge("writer", "citation_formatter")
    graph.add_edge("citation_formatter", END)

    return graph.compile()