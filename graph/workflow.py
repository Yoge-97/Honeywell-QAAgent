"""LangGraph workflow that connects the three agents.

    START ──> resume_parser ──┐
      │                       ├──> resume_analyzer ──> END
      └────> job_parser ──────┘

The two parsers run in parallel. The analyzer waits for both.
"""

from langgraph.graph import END, START, StateGraph

from agents.job_parser.agent import job_parser_node
from agents.resume_analyzer.agent import resume_analyzer_node
from agents.resume_parser.agent import resume_parser_node
from graph.state import AnalyzerState


def build_graph():
    graph = StateGraph(AnalyzerState)

    graph.add_node("resume_parser", resume_parser_node)
    graph.add_node("job_parser", job_parser_node)
    graph.add_node("resume_analyzer", resume_analyzer_node)

    graph.add_edge(START, "resume_parser")
    graph.add_edge(START, "job_parser")
    graph.add_edge(["resume_parser", "job_parser"], "resume_analyzer")
    graph.add_edge("resume_analyzer", END)

    return graph.compile()


def run_analysis(resume_text: str, job_text: str) -> AnalyzerState:
    """Run the full pipeline and return the final state."""
    return build_graph().invoke({"resume_text": resume_text, "job_text": job_text})
