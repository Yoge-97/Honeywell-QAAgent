"""Streamlit UI: analyze, tailor, review with live editing, and download.

Run from the project root:
    streamlit run agents/resume_analyzer/app.py
"""

import sys
from pathlib import Path

# Streamlit runs this file directly, so make the project root importable.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402
from langgraph.types import Command  # noqa: E402

from agents.resume_analyzer.models import TailoredExperience, TailoredResume  # noqa: E402
from graph.workflow import build_graph, new_session  # noqa: E402

st.set_page_config(page_title="Resume Analyzer", layout="wide")

# The graph and its session live in st.session_state so they survive Streamlit reruns.
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
    st.session_state.config = new_session()
    st.session_state.result = None
    st.session_state.step = 0  # changes on every graph call, so edit boxes reload with the new draft


def run(graph_input) -> None:
    """Start or continue the graph, then redraw the page."""
    with st.spinner("Working..."):
        st.session_state.result = st.session_state.graph.invoke(graph_input, st.session_state.config)
    st.session_state.step += 1
    st.rerun()


def pending_question() -> dict | None:
    """What the paused graph is asking the user, or None if it is not paused."""
    result = st.session_state.result
    if result and "__interrupt__" in result:
        return result["__interrupt__"][0].value
    return None


st.title("Resume Analyzer")

# ---------- 1. Inputs ----------
left, right = st.columns(2)
resume_text = left.text_area(
    "Resume", (ROOT / "samples/resume.txt").read_text(encoding="utf-8"), height=260
)
job_text = right.text_area(
    "Job description", (ROOT / "samples/job.txt").read_text(encoding="utf-8"), height=260
)
if st.button("Analyze", type="primary", key="analyze"):
    st.session_state.config = new_session()
    run({"resume_text": resume_text, "job_text": job_text})

result = st.session_state.result
if not result:
    st.stop()

# ---------- 2. Analysis ----------
analysis = result["analysis"]
st.header("Analysis")
cols = st.columns(4)
cols[0].metric("Overall", f"{analysis.overall_score}/100")
cols[1].metric("Skills", f"{analysis.skills_score}/100")
cols[2].metric("Experience", f"{analysis.experience_score}/100")
cols[3].metric("Education", f"{analysis.education_score}/100")
st.write(analysis.summary)

left, right = st.columns(2)
left.subheader("Matched skills")
left.write("\n".join(f"- {skill}" for skill in analysis.matched_skills))
right.subheader("Skill gaps")
right.write("\n".join(f"- **{gap.skill}** ({gap.importance}): {gap.suggestion}" for gap in analysis.skill_gaps))
with st.expander("Suggested improvements"):
    st.write("\n".join(f"- {item}" for item in analysis.improvements))

question = pending_question()

# ---------- 3. Tailor? ----------
if question and question["type"] == "ask_to_tailor":
    st.header(question["question"])
    yes, no = st.columns(2)
    if yes.button("Yes, tailor my resume", type="primary", key="tailor_yes"):
        run(Command(resume=True))
    if no.button("No thanks", key="tailor_no"):
        run(Command(resume=False))

# ---------- 4. Review and live editing ----------
if question and question["type"] == "human_review":
    draft = TailoredResume(**question["tailored_resume"])
    revisions_left = question["max_revisions"] - question["revision_count"]
    step = st.session_state.step

    st.header("Review your tailored resume")
    with st.expander("What the AI changed", expanded=True):
        st.write("\n".join(f"- {change}" for change in draft.changes_made))

    original, tailored = st.columns(2)
    original.subheader("Original")
    original.text(result["resume_text"])

    tailored.subheader("Tailored (editable)")
    summary = tailored.text_area("Summary", draft.summary, key=f"summary_{step}")
    skills = tailored.text_input("Skills (comma separated)", ", ".join(draft.skills), key=f"skills_{step}")
    experience = []
    for i, job in enumerate(draft.experience):
        bullets = tailored.text_area(
            f"{job.job_title} - {job.company} ({job.dates}), one bullet per line",
            "\n".join(job.bullets),
            key=f"job_{i}_{step}",
        )
        experience.append(
            TailoredExperience(
                job_title=job.job_title,
                company=job.company,
                dates=job.dates,
                bullets=[line.strip() for line in bullets.splitlines() if line.strip()],
            )
        )

    edited = draft.model_copy(
        update={
            "summary": summary.strip(),
            "skills": [skill.strip() for skill in skills.split(",") if skill.strip()],
            "experience": experience,
        }
    )

    st.subheader("Next step")
    save, approve = st.columns(2)
    if save.button("Save edits", key="save", disabled=edited == draft):
        run(Command(resume={"action": "edit", "tailored_resume": edited.model_dump()}))
    if approve.button("Approve & export", type="primary", key="approve"):
        if edited != draft:  # keep unsaved edits
            st.session_state.graph.invoke(
                Command(resume={"action": "edit", "tailored_resume": edited.model_dump()}),
                st.session_state.config,
            )
        run(Command(resume={"action": "approve"}))

    feedback = st.text_input(
        f"Or ask the AI for changes ({revisions_left} revisions left)",
        placeholder="e.g. make the summary one sentence",
        key=f"feedback_{step}",
    )
    if st.button("Regenerate with feedback", key="revise", disabled=revisions_left <= 0 or not feedback):
        run(Command(resume={"action": "revise", "feedback": feedback}))

# ---------- 5. Download ----------
if "export_paths" in result:
    st.success("Your tailored resume is ready.")
    docx_path = Path(result["export_paths"]["docx"])
    pdf_path = Path(result["export_paths"]["pdf"])
    left, right = st.columns(2)
    left.download_button("Download DOCX", docx_path.read_bytes(), file_name=docx_path.name, key="download_docx")
    right.download_button("Download PDF", pdf_path.read_bytes(), file_name=pdf_path.name, key="download_pdf")
