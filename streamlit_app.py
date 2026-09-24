"""Streamlit UI for uploading a resume, extracting text, and running the existing analyzer."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from agents.resume_parser.agent import analyze_uploaded_resume

load_dotenv()


def load_default_job_description() -> str:
    """Return the sample job description used by the project when no custom one is supplied."""
    default_path = Path(__file__).resolve().parent / "samples" / "job.txt"
    if default_path.exists():
        return default_path.read_text(encoding="utf-8")
    return ""


def render_analysis(result: dict) -> None:
    """Render the analysis returned by the existing workflow."""
    analysis = result["analysis"]

    st.subheader("Resume Analysis Result")
    st.metric("Overall Score", analysis.overall_score)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Skills", analysis.skills_score)
    with col2:
        st.metric("Experience", analysis.experience_score)
    with col3:
        st.metric("Education", analysis.education_score)

    st.markdown("### Summary")
    st.write(analysis.summary)

    if analysis.matched_skills:
        st.markdown("### Matched Skills")
        st.write(", ".join(analysis.matched_skills))

    if analysis.skill_gaps:
        st.markdown("### Skill Gaps")
        st.json(
            [
                {
                    "skill": gap.skill,
                    "importance": gap.importance,
                    "suggestion": gap.suggestion,
                }
                for gap in analysis.skill_gaps
            ]
        )

    if analysis.strengths:
        st.markdown("### Strengths")
        st.write("\n".join(f"- {strength}" for strength in analysis.strengths))

    if analysis.improvements:
        st.markdown("### Improvements")
        st.write("\n".join(f"- {improvement}" for improvement in analysis.improvements))

    st.markdown("### Full Analysis JSON")
    st.json(analysis.model_dump())


def main() -> None:
    """Run the Streamlit resume upload workflow."""
    st.set_page_config(page_title="Resume Upload Analyzer", page_icon="📄")
    st.title("Resume Upload Analyzer")
    st.caption("Upload a resume in PDF or DOCX format and compare it against a job description.")

    uploaded_file = st.file_uploader(
        "Upload resume (PDF or DOCX)",
        type=["pdf", "docx"],
        help="Upload the candidate's resume. We will extract the text and analyze it against the job description below.",
    )

    job_text = st.text_area(
        "Job Description",
        value=load_default_job_description(),
        height=250,
        help="Paste or edit the target job description. Leave it as-is to use the sample job description.",
    )

    if st.button("Analyze Resume", type="primary"):
        if uploaded_file is None:
            st.error("Please upload a PDF or DOCX resume before analyzing.")
            return

        try:
            with st.spinner("Extracting text and running the resume analysis..."):
                result = analyze_uploaded_resume(uploaded_file, job_text)
            render_analysis(result)
        except ValueError as exc:
            st.error(f"Invalid file or extraction error: {exc}")
        except RuntimeError as exc:
            st.error(f"Configuration error: {exc}")
        except Exception as exc:  # pragma: no cover - runtime safety net
            st.error(f"An unexpected error occurred while analyzing the resume: {exc}")


if __name__ == "__main__":
    main()
