import time
import logging
from app.agent.factory import get_research_graph
from app.models.state import ResearchState

logger = logging.getLogger(__name__)


GRAPH_RECURSION_LIMIT = 50


def build_initial_state(topic: str) -> ResearchState:
    return {
        "topic": topic,
        "intent": None,
        "sub_queries": [],
        "initial_sub_queries": [],
        "sources": [],
        "structured_knowledge": None,
        "final_response": None,
        "round_number": 0,
        "started_at": time.time(),
        "research_log": [],
        "metrics": {},
    }


async def run_research(topic: str) -> ResearchState:
    """Single entry point the api/ layer calls. Constructs a fresh state,
    invokes the compiled graph end to end, and returns the final state —
    the caller reads final_state["final_response"] for the JSON response."""
    graph = get_research_graph()
    initial_state = build_initial_state(topic)

    logger.info("Starting research for topic=%r", topic)
    final_state = await graph.ainvoke(
        initial_state, config={"recursion_limit": GRAPH_RECURSION_LIMIT}
    )
    logger.info(
        "Research complete for topic=%r — rounds=%d, sources=%d, confidence=%.2f",
        topic, final_state["round_number"], len(final_state["sources"]),
        final_state["structured_knowledge"]["overall_confidence"]
        if final_state["structured_knowledge"] else 0.0,
    )
    return final_state