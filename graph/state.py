"""The shared state that flows through the LangGraph workflow.

Each agent reads the keys it needs and returns only the key it owns:
    resume_parser   -> "resume"
    job_parser      -> "job"
    resume_analyzer -> "analysis"
    ask_to_tailor   -> "tailor"
    resume_tailor   -> "tailored_resume"
    human_review    -> "tailored_resume" (user edits), "feedback", "revision_count"
    exporter        -> "export_paths"
"""

from typing import TypedDict

from agents.resume_analyzer.models import TailoredResume
from models.analysis import Analysis
from models.job import Job
from models.resume import Resume


class AnalyzerState(TypedDict, total=False):
    resume_text: str  # input
    job_text: str  # input
    resume: Resume  # set by resume_parser
    job: Job  # set by job_parser
    analysis: Analysis  # set by resume_analyzer
    tailor: bool  # set by ask_to_tailor: does the user want a tailored resume?
    tailored_resume: TailoredResume  # set by resume_tailor, or by human_review when the user edits it
    feedback: str  # set by human_review: the user's latest revision request
    revision_count: int  # set by human_review: how many times the user asked for a rewrite
    export_paths: dict[str, str]  # set by exporter: {"docx": path, "pdf": path}
