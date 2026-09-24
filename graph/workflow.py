"""LangGraph workflow that connects the agents.

    START ──> resume_parser ──┐
      │                       ├──> resume_analyzer ──> ask_to_tailor ──no──> END
      └────> job_parser ──────┘                              │ yes
                                                             ▼
                                                      resume_tailor <─────────┐
                                                             │                │ revise
                                                             ▼                │
                                      edit ┌──────────> human_review ─────────┘
                                           └──────────────── │
                                                             │ approve
                                                             ▼
                                                       ask_to_export ──no──> END
                                                             │ yes
                                                             ▼
                                                         exporter ──> END

The two parsers run in parallel. ask_to_tailor, human_review and ask_to_export pause the graph
and wait for the user (see agents/resume_analyzer/review.py).
"""

import uuid

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph

from agents.job_parser.agent import job_parser_node
from agents.resume_analyzer.agent import resume_analyzer_node
from agents.resume_analyzer.export import exporter_node
from agents.resume_analyzer.review import (
    ask_to_export_node,
    ask_to_tailor_node,
    human_review_node,
    route_after_ask,
    route_after_export_question,
)
from agents.resume_analyzer.tailor import resume_tailor_node
from agents.resume_parser.agent import resume_parser_node
from graph.state import AnalyzerState

# Our Pydantic models that the checkpointer is allowed to save and load while the graph is paused.
CHECKPOINT_MODELS = [
    ("models.resume", "Resume"),
    ("models.job", "Job"),
    ("models.analysis", "Analysis"),
    ("agents.resume_analyzer.models", "TailoredResume"),
]


def build_graph():
    graph = StateGraph(AnalyzerState)

    graph.add_node("resume_parser", resume_parser_node)
    graph.add_node("job_parser", job_parser_node)
    graph.add_node("resume_analyzer", resume_analyzer_node)
    graph.add_node("ask_to_tailor", ask_to_tailor_node)
    graph.add_node("resume_tailor", resume_tailor_node)
    graph.add_node(
        "human_review", human_review_node, destinations=("resume_tailor", "human_review", "ask_to_export")
    )
    graph.add_node("ask_to_export", ask_to_export_node)
    graph.add_node("exporter", exporter_node)

    graph.add_edge(START, "resume_parser")
    graph.add_edge(START, "job_parser")
    graph.add_edge(["resume_parser", "job_parser"], "resume_analyzer")
    graph.add_edge("resume_analyzer", "ask_to_tailor")
    graph.add_conditional_edges("ask_to_tailor", route_after_ask, ["resume_tailor", END])
    graph.add_edge("resume_tailor", "human_review")
    # human_review picks its own next step (see review.py), so it has no fixed edge.
    graph.add_conditional_edges("ask_to_export", route_after_export_question, ["exporter", END])
    graph.add_edge("exporter", END)

    # The checkpointer saves the state while the graph is paused, so it can continue later.
    checkpointer = MemorySaver(serde=JsonPlusSerializer(allowed_msgpack_modules=CHECKPOINT_MODELS))
    return graph.compile(checkpointer=checkpointer)


def new_session() -> dict:
    """Config for a new run. Reuse the same config to continue a paused graph."""
    return {"configurable": {"thread_id": str(uuid.uuid4())}}


def run_analysis(resume_text: str, job_text: str) -> AnalyzerState:
    """Parse and analyze only. The graph stops at the "create a tailored resume?" question."""
    return build_graph().invoke({"resume_text": resume_text, "job_text": job_text}, new_session())
