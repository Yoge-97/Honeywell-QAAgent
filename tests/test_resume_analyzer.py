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
