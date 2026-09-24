"""Resume Parser agent: turns raw resume text into a `Resume` model.

Owner branch: feature/resume-parser
"""

from langchain_core.prompts import ChatPromptTemplate

from agents.resume_parser.prompts import SYSTEM_PROMPT
from graph.state import AnalyzerState
from models.resume import Resume
from services.llm import get_llm


def parse_resume(resume_text: str) -> Resume:
    """Extract structured resume data from plain text."""
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "Resume:\n\n{resume_text}")]
    )
    chain = prompt | get_llm().with_structured_output(Resume)
    return chain.invoke({"resume_text": resume_text})


def resume_parser_node(state: AnalyzerState) -> dict:
    """LangGraph node: reads `resume_text`, writes `resume`."""
    return {"resume": parse_resume(state["resume_text"])}
