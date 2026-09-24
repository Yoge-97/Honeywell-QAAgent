"""Resume Analyzer agent: compares a `Resume` with a `Job` and scores the match.

Owner branch: feature/resume-analyzer
"""

from graph.state import AnalyzerState
from models.analysis import Analysis
from models.job import Job
from models.resume import Resume


def analyze(resume: Resume, job: Job) -> Analysis:
    """Score the resume against the job and suggest improvements."""
    # TODO(feature/resume-analyzer): call the LLM with structured output.
    # Stub returns an empty Analysis so the pipeline still runs.
    return Analysis()


def resume_analyzer_node(state: AnalyzerState) -> dict:
    """LangGraph node: reads `resume` and `job`, writes `analysis`."""
    return {"analysis": analyze(state["resume"], state["job"])}
