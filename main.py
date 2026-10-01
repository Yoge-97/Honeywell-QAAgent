"""Run the resume analyzer.

Usage:
    python main.py

Enter a local .txt, .pdf, or .docx resume path when prompted.
"""

import json
import sys
from pathlib import Path

from agents.resume_parser.agent import (
    ResumeValidationError,
    extract_docx_text,
    extract_pdf_text,
)
from graph.workflow import run_analysis

JOB_FILE = "samples/job.txt"

# Windows consoles can't print some characters the LLM returns, so use UTF-8.
sys.stdout.reconfigure(encoding="utf-8")


def load_resume_input(file_path: str) -> str | dict[str, object]:
    """Load text or prepare a PDF/DOCX input for the Resume Parser."""
    if not file_path.strip():
        raise ValueError("A resume file path is required.")

    path = Path(file_path.strip().strip('"')).expanduser()
    suffix = path.suffix.casefold()
    if suffix not in {".txt", ".pdf", ".docx"}:
        raise ValueError(
            f"Unsupported resume file type '{suffix or '(none)'}'. Use .txt, .pdf, or .docx."
        )
    if suffix == ".txt":
        return path.read_text(encoding="utf-8")

    file_bytes = path.read_bytes()
    if suffix == ".pdf":
        extracted_text = extract_pdf_text(file_bytes)
    elif suffix == ".docx":
        extracted_text = extract_docx_text(file_bytes)
    return {
        "file": file_bytes,
        "file_name": path.name,
        "text": extracted_text,
    }


# 1. Get the resume path and read the job input
resume_file = input("Enter resume file path (.txt, .pdf, or .docx): ")
with open(JOB_FILE, encoding="utf-8") as f:
    job_text = f.read()

# 2. Read and extract the selected resume file
try:
    resume_input = load_resume_input(resume_file)
except (OSError, ValueError) as exc:
    print(json.dumps({"input_error": str(exc)}, indent=2))
    raise SystemExit(1) from exc

# 3. Run the workflow; the Resume Parser validates its input with the LLM
try:
    result = run_analysis(resume_input, job_text)
except ResumeValidationError as exc:
    print(
        json.dumps(
            {"resume_validation": exc.validation.model_dump()},
            indent=2,
        )
    )
    raise SystemExit(1) from exc

# 4. Print validation and analysis results
analysis = result["analysis"]
print(
    json.dumps(
        {
            "resume_validation": result["resume_validation"],
            "analysis": analysis.model_dump(),
        },
        indent=2,
    )
)
