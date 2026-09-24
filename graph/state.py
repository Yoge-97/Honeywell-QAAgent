"""The shared state that flows through the LangGraph workflow.

Each agent reads the keys it needs and returns only the key it owns:
    resume_parser   -> "resume"
    job_parser      -> "job"
    resume_analyzer -> "analysis"
"""

from typing import TypedDict

from models.analysis import Analysis
from models.job import Job
from models.resume import Resume


class AnalyzerState(TypedDict, total=False):
    resume_text: str  # input
    job_text: str  # input
    resume: Resume  # set by resume_parser
    job: Job  # set by job_parser
    analysis: Analysis  # set by resume_analyzer
