"""Streamlit interface for resume and job-description analysis."""

import json
from pathlib import Path

import streamlit as st

from agents.resume_parser.agent import (
    ResumeValidationError,
    extract_docx_text,
    extract_pdf_text,
)
from graph.workflow import run_analysis


def extract_upload_text(upload) -> str:
    suffix = Path(upload.name).suffix.casefold()
    content = upload.getvalue()
    if suffix == ".txt":
        return content.decode("utf-8")
    if suffix == ".pdf":
        return extract_pdf_text(content)
    if suffix == ".docx":
        return extract_docx_text(content)
    raise ValueError("Unsupported file type. Use a TXT, PDF, or DOCX file.")


def prepare_resume_input(upload) -> str | dict[str, object]:
    text = extract_upload_text(upload)
    if Path(upload.name).suffix.casefold() == ".txt":
        return text
    return {
        "file": upload.getvalue(),
        "file_name": upload.name,
        "text": text,
    }


st.set_page_config(page_title="Resume and Job Fit", page_icon="RJ", layout="wide")
st.title("Resume and Job Fit")
st.caption("Upload a resume and provide a job description to view the match analysis.")

resume_column, job_column = st.columns(2, gap="large")
with resume_column:
    st.subheader("Resume")
    resume_upload = st.file_uploader(
        "Upload resume",
        type=["txt", "pdf", "docx"],
        key="resume_upload",
    )

with job_column:
    st.subheader("Job description")
    job_upload = st.file_uploader(
        "Upload job description file (optional)",
        type=["txt", "pdf", "docx"],
        key="job_upload",
    )
    job_text_input = st.text_area(
        "Or paste the job description",
        height=220,
        placeholder="Paste the full job description here...",
    )

analyze_clicked = st.button("Analyze match", type="primary", use_container_width=True)

if analyze_clicked:
    if resume_upload is None:
        st.error("Upload a resume file to continue.")
        st.stop()
    if job_upload is not None and job_text_input.strip():
        st.error("Upload a job-description file or paste its text, not both.")
        st.stop()
    if job_upload is None and not job_text_input.strip():
        st.error("Upload or paste a job description to continue.")
        st.stop()

    try:
        with st.spinner("Extracting documents and analyzing the match..."):
            resume_input = prepare_resume_input(resume_upload)
            job_text = (
                extract_upload_text(job_upload)
                if job_upload is not None
                else job_text_input.strip()
            )
            result = run_analysis(resume_input, job_text)
    except ResumeValidationError as exc:
        st.subheader("Resume validation")
        st.error("The uploaded document was not accepted as a resume.")
        st.json(exc.validation.model_dump())
        st.stop()
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        st.error(f"Unable to read or process an input file: {exc}")
        st.stop()
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    validation = result["resume_validation"]
    st.subheader("Resume validation")
    if validation["is_resume"]:
        st.success("This document was classified as a resume.")
    else:
        st.warning("This document was not classified as a resume.")
    st.write(validation["reason"])

    analysis_tab, resume_tab, job_tab = st.tabs(
        ["Match analysis", "Parsed resume", "Parsed job"]
    )
    with analysis_tab:
        st.json(result["analysis"].model_dump())
    with resume_tab:
        st.json(result["resume"].model_dump())
    with job_tab:
        st.json(result["job"].model_dump())