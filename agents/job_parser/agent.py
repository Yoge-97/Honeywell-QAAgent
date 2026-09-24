"""Job Parser agent: turns raw job-description text into a `Job` model.

Owner branch: feature/job-parser
"""

from graph.state import AnalyzerState
from models.job import Job


def parse_job(job_text: str) -> Job:
    """Extract structured job data from plain text."""
    # TODO(feature/job-parser): call the LLM with structured output.
    # Stub returns an empty Job so the rest of the pipeline still runs.
    return Job()


def job_parser_node(state: AnalyzerState) -> dict:
    """LangGraph node: reads `job_text`, writes `job`."""
    return {"job": parse_job(state["job_text"])}
