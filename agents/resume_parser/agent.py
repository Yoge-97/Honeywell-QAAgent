"""Resume Parser agent: turns raw resume text into a `Resume` model.

Owner branch: feature/resume-parser
"""

from graph.state import AnalyzerState
from models.resume import Resume


def parse_resume(resume_text: str) -> Resume:
    """Extract structured resume data from plain text."""
    # TODO(feature/resume-parser): call the LLM with structured output.
    # Stub returns an empty Resume so the rest of the pipeline still runs.
    return Resume()


def resume_parser_node(state: AnalyzerState) -> dict:
    """LangGraph node: reads `resume_text`, writes `resume`."""
    return {"resume": parse_resume(state["resume_text"])}
