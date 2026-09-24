"""Resume Parser agent: turns raw resume text into a `Resume` model.

Owner branch: feature/resume-parser
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Protocol

from docx import Document
from langchain_core.prompts import ChatPromptTemplate
from pypdf import PdfReader

from agents.resume_parser.prompts import SYSTEM_PROMPT
from graph.state import AnalyzerState
from models.resume import Resume
from services.llm import get_llm


class UploadedResume(Protocol):
    """Minimum interface required from a Streamlit uploaded file."""

    name: str

    def getvalue(self) -> bytes:
        ...


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract readable text from a PDF file."""
    try:
        reader = PdfReader(BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        raise ValueError(f"Failed to extract text from the PDF: {exc}") from exc

    if not text:
        raise ValueError("The PDF does not contain readable text.")
    return text


def extract_docx_text(file_bytes: bytes) -> str:
    """Extract readable text from a DOCX file."""
    try:
        document = Document(BytesIO(file_bytes))
        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]
        text = "\n".join(paragraphs).strip()
    except Exception as exc:
        raise ValueError(f"Failed to extract text from the DOCX file: {exc}") from exc

    if not text:
        raise ValueError("The DOCX file does not contain readable text.")
    return text


def extract_resume_text(uploaded_file: UploadedResume | None) -> str:
    """Read and convert a PDF or DOCX upload into plain text."""
    if uploaded_file is None:
        raise ValueError("Please upload a resume file first.")

    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(uploaded_file.getvalue())
    if suffix == ".docx":
        return extract_docx_text(uploaded_file.getvalue())

    raise ValueError("Unsupported file type. Please upload a PDF or DOCX resume.")


def analyze_uploaded_resume(uploaded_file: UploadedResume | None, job_text: str):
    """Extract an uploaded resume and run the existing resume analysis workflow."""
    if not job_text.strip():
        raise ValueError("Please provide a job description before running the analysis.")

    from graph.workflow import run_analysis

    return run_analysis(extract_resume_text(uploaded_file), job_text.strip())


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
