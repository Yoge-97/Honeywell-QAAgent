"""Resume Analyzer agent: compares a `Resume` with a `Job` and scores the match.

Owner branch: feature/resume-analyzer
"""

from langchain_core.prompts import ChatPromptTemplate

from agents.resume_analyzer.prompts import HUMAN_PROMPT, SYSTEM_PROMPT
from graph.state import AnalyzerState
from models.analysis import Analysis
from models.job import Job
from models.resume import Resume
from services.llm import get_llm


def analyze(resume: Resume, job: Job) -> Analysis:
    """Score the resume against the job and suggest improvements."""
    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM_PROMPT), ("human", HUMAN_PROMPT)])
    chain = prompt | get_llm().with_structured_output(Analysis)
    return chain.invoke(
        {
            "resume_json": resume.model_dump_json(indent=2),
            "job_json": job.model_dump_json(indent=2),
        }
    )


def resume_analyzer_node(state: AnalyzerState) -> dict:
    """LangGraph node: reads `resume` and `job`, writes `analysis`."""
    return {"analysis": analyze(state["resume"], state["job"])}
