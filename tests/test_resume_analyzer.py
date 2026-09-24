"""Tests for the Resume Analyzer extras: export and human-in-the-loop. No real LLM calls."""

from docx import Document

from agents.resume_analyzer import export
from agents.resume_analyzer.models import TailoredExperience, TailoredResume

SAMPLE = TailoredResume(
    full_name="Alice Doe",
    email="alice@example.com",
    summary="Backend engineer \u2011 builds APIs \u2014 \u201cfast\u201d.",  # characters the LLM often returns
    skills=["Python", "FastAPI"],
    experience=[
        TailoredExperience(job_title="Engineer", company="Acme", dates="2021 - Present", bullets=["Built APIs"])
    ],
    education=["B.S. Computer Science"],
)


def test_to_docx_writes_resume(tmp_path):
    path = export.to_docx(SAMPLE, tmp_path / "resume.docx")

    text = "\n".join(p.text for p in Document(path).paragraphs)
    assert "Alice Doe" in text
    assert "Built APIs" in text


def test_to_pdf_handles_unicode(tmp_path):
    path = export.to_pdf(SAMPLE, tmp_path / "resume.pdf")

    assert path.read_bytes().startswith(b"%PDF")


def test_exporter_node_returns_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(export, "OUTPUT_DIR", tmp_path)

    result = export.exporter_node({"tailored_resume": SAMPLE})

    assert result["export_paths"]["docx"].endswith("tailored_resume.docx")
    assert result["export_paths"]["pdf"].endswith("tailored_resume.pdf")


# ---------- Human in the loop (full graph with fake agents) ----------

import pytest
from langgraph.types import Command

from agents.job_parser import agent as job_agent
from agents.resume_analyzer import agent as analyzer_agent
from agents.resume_analyzer import review, tailor
from agents.resume_parser import agent as resume_agent
from graph.workflow import build_graph, new_session
from models.analysis import Analysis
from models.job import Job
from models.resume import Resume


@pytest.fixture
def fake_agents(monkeypatch, tmp_path):
    """Replace every LLM call with a fake. Returns the list of feedback the tailor received."""
    tailor_calls = []

    def fake_tailor(resume, job, analysis, feedback="", previous=None):
        tailor_calls.append(feedback)
        return TailoredResume(full_name=resume.full_name, summary=f"draft {len(tailor_calls)}")

    monkeypatch.setattr(resume_agent, "parse_resume", lambda text: Resume(full_name="Alice"))
    monkeypatch.setattr(job_agent, "parse_job", lambda text: Job(title="Engineer"))
    monkeypatch.setattr(analyzer_agent, "analyze", lambda resume, job: Analysis(overall_score=70))
    monkeypatch.setattr(tailor, "tailor_resume", fake_tailor)
    monkeypatch.setattr(export, "OUTPUT_DIR", tmp_path)
    return tailor_calls


@pytest.fixture
def graph(fake_agents):
    """The real graph, running on fake agents."""
    graph = build_graph()
    graph.tailor_calls = fake_agents
    return graph


def pending(result):
    """The payload of the question the paused graph is asking."""
    return result["__interrupt__"][0].value


def test_user_declines_tailoring(graph):
    config = new_session()
    result = graph.invoke({"resume_text": "r", "job_text": "j"}, config)
    assert pending(result)["type"] == "ask_to_tailor"

    result = graph.invoke(Command(resume=False), config)

    assert "__interrupt__" not in result
    assert "tailored_resume" not in result
    assert graph.tailor_calls == []


def test_revise_edit_approve_export(graph):
    config = new_session()
    graph.invoke({"resume_text": "r", "job_text": "j"}, config)

    # yes -> first draft is shown for review
    result = graph.invoke(Command(resume=True), config)
    assert pending(result)["tailored_resume"]["summary"] == "draft 1"

    # revise -> tailor runs again with the feedback
    result = graph.invoke(Command(resume={"action": "revise", "feedback": "shorter"}), config)
    assert graph.tailor_calls == ["", "shorter"]
    assert pending(result)["tailored_resume"]["summary"] == "draft 2"
    assert pending(result)["revision_count"] == 1

    # edit -> user's text is kept as-is, no LLM call
    edited = {**pending(result)["tailored_resume"], "summary": "my own words"}
    result = graph.invoke(Command(resume={"action": "edit", "tailored_resume": edited}), config)
    assert pending(result)["tailored_resume"]["summary"] == "my own words"
    assert len(graph.tailor_calls) == 2

    # approve -> asked whether to export
    result = graph.invoke(Command(resume={"action": "approve"}), config)
    assert pending(result)["type"] == "ask_to_export"

    # yes -> exported
    result = graph.invoke(Command(resume=True), config)
    assert "__interrupt__" not in result
    assert result["tailored_resume"].summary == "my own words"
    assert set(result["export_paths"]) == {"docx", "pdf"}


def test_user_declines_export(graph):
    config = new_session()
    graph.invoke({"resume_text": "r", "job_text": "j"}, config)
    graph.invoke(Command(resume=True), config)
    graph.invoke(Command(resume={"action": "approve"}), config)

    result = graph.invoke(Command(resume=False), config)

    assert "__interrupt__" not in result
    assert result["tailored_resume"].summary == "draft 1"  # approved resume is kept
    assert "export_paths" not in result


def test_revision_limit(graph, monkeypatch):
    monkeypatch.setattr(review, "MAX_REVISIONS", 1)
    config = new_session()
    graph.invoke({"resume_text": "r", "job_text": "j"}, config)
    graph.invoke(Command(resume=True), config)

    graph.invoke(Command(resume={"action": "revise", "feedback": "one"}), config)
    result = graph.invoke(Command(resume={"action": "revise", "feedback": "two"}), config)

    assert graph.tailor_calls == ["", "one"]  # the second revise was refused
    assert pending(result)["type"] == "human_review"


# ---------- Streamlit UI (clicked through with AppTest, fake agents) ----------

from streamlit.testing.v1 import AppTest


def test_streamlit_edit_and_approve(fake_agents):
    app = AppTest.from_file("../agents/resume_analyzer/app.py", default_timeout=30).run()

    app.button(key="analyze").click().run()
    assert app.metric[0].value == "70/100"

    app.button(key="tailor_yes").click().run()
    summary_box = next(box for box in app.text_area if box.label == "Summary")
    assert summary_box.value == "draft 1"

    summary_box.set_value("my own words").run()
    app.button(key="approve").click().run()
    app.button(key="export_yes").click().run()

    assert not app.exception
    assert app.success[0].value == "Your tailored resume is ready."
    exported = app.session_state.result["tailored_resume"]
    assert exported.summary == "my own words"  # unsaved edits were kept on approve
