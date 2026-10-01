"""Resume Parser agent: turns raw resume text into a `Resume` model.

Owner branch: feature/resume-parser
"""

import asyncio
from collections.abc import Mapping
from io import BytesIO
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from docx import Document
from pypdf import PdfReader
from pydantic import BaseModel, Field

from agents.resume_parser.prompts import SYSTEM_PROMPT
from graph.state import AnalyzerState
from models.resume import Resume
from services.llm import get_llm


class ResumeValidation(BaseModel):
    """LLM decision about whether input represents a person's resume."""

    is_resume: bool = Field(description="Whether the document is a person's resume or CV.")
    reason: str = Field(description="Brief explanation for the classification.")


class ResumeValidationError(ValueError):
    """Raised when resume content is empty or classified as unrelated input."""

    def __init__(self, validation: ResumeValidation):
        self.validation = validation
        super().__init__(validation.reason)


def extract_pdf_text(source: str | Path | bytes) -> str:
    """Extract text from a PDF path or its bytes."""
    try:
        reader = PdfReader(BytesIO(source) if isinstance(source, bytes) else source)
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        raise ValueError(f"Unable to read PDF resume: {exc}") from exc
    if not text:
        raise ValueError("PDF resume contains no extractable text.")
    return text


def extract_docx_text(source: str | Path | bytes) -> str:
    """Extract paragraph and table text from a DOCX path or its bytes."""
    try:
        document = Document(BytesIO(source) if isinstance(source, bytes) else source)
        parts = [paragraph.text for paragraph in document.paragraphs]
        parts.extend(
            cell.text
            for table in document.tables
            for row in table.rows
            for cell in row.cells
        )
        text = "\n".join(parts).strip()
    except Exception as exc:
        raise ValueError(f"Unable to read DOCX resume: {exc}") from exc
    if not text:
        raise ValueError("DOCX resume contains no extractable text.")
    return text


async def validate_resume(resume_text: str) -> ResumeValidation:
    """Use the LLM to classify resume content without relying on fixed keywords."""
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ResumeValidationError(
            ResumeValidation(
                is_resume=False,
                reason="Resume is empty or contains no readable text.",
            )
        )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Determine whether the provided document is a person's resume or CV. "
                "Classify based on its meaning and overall content, not the presence "
                "of fixed headings or keywords. Reject terminal output, installation "
                "logs, job descriptions, and unrelated documents. Return a brief reason.",
            ),
            ("human", "Document:\n\n{resume_text}"),
        ]
    )
    chain = prompt | get_llm().with_structured_output(ResumeValidation)
    validation = await chain.ainvoke({"resume_text": resume_text})
    if not validation.is_resume:
        raise ResumeValidationError(validation)
    return validation


async def _prepare_resume_input(
    resume_input: str | Mapping[str, object],
) -> tuple[str, ResumeValidation]:
    if isinstance(resume_input, str):
        validation = await validate_resume(resume_input)
        return resume_input, validation

    if not isinstance(resume_input, Mapping):
        raise ValueError("Resume input must be text or a file-and-text mapping.")

    source = resume_input.get("file")
    validation_text = resume_input.get("text")
    file_name = resume_input.get("file_name")
    if not isinstance(validation_text, str):
        raise ValueError("File input must include readable resume text for validation.")
    if not isinstance(source, (str, Path, bytes)):
        raise ValueError("Resume file must be a path or file bytes.")

    if isinstance(source, bytes):
        if not isinstance(file_name, str) or not file_name:
            raise ValueError("A file_name with a .pdf or .docx extension is required for file bytes.")
        suffix = Path(file_name).suffix.casefold()
    else:
        suffix = Path(source).suffix.casefold()

    if suffix == ".pdf":
        extractor = extract_pdf_text
    elif suffix == ".docx":
        extractor = extract_docx_text
    else:
        raise ValueError("Unsupported resume file type; supported formats are PDF and DOCX.")

    extracted_text, validation = await asyncio.gather(
        asyncio.to_thread(extractor, source),
        validate_resume(validation_text),
    )
    if extracted_text != validation_text:
        validation = await validate_resume(extracted_text)
    return extracted_text, validation


def parse_resume(resume_text: str) -> Resume:
    """Extract structured resume data from plain text."""
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "Resume:\n\n{resume_text}")]
    )
    chain = prompt | get_llm().with_structured_output(Resume)
    return chain.invoke({"resume_text": resume_text})


def resume_parser_node(state: AnalyzerState) -> dict:
    """Parse resume input and return the LLM validation result."""
    resume_text, validation = asyncio.run(_prepare_resume_input(state["resume_text"]))
    return {
        "resume": parse_resume(resume_text),
        "resume_validation": validation.model_dump(),
    }
