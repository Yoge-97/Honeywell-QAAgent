"""Job Parser agent: turns raw job-description text or a job URL into a `Job` model.

Owner branch: feature/job-parser
"""

from urllib.parse import urlparse

from langchain_core.prompts import ChatPromptTemplate

from agents.job_parser.fetcher import get_job_text
from agents.job_parser.prompts import SYSTEM_PROMPT
from graph.state import AnalyzerState
from models.job import Job
from services.llm import get_llm


def _looks_like_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def parse_job(job_text: str) -> Job:
    """Extract structured job data from plain text or a job URL."""
    normalized_text = job_text.strip()
    if _looks_like_url(normalized_text):
        normalized_text = get_job_text(normalized_text)

    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "Job description:\n\n{job_text}")]
    )
    chain = prompt | get_llm().with_structured_output(Job)
    return chain.invoke({"job_text": normalized_text})


def job_parser_node(state: AnalyzerState) -> dict:
    """LangGraph node: reads `job_text`, writes `job`."""
    return {"job": parse_job(state["job_text"])}
