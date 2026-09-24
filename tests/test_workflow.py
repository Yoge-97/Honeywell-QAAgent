"""Checks that the LangGraph wiring works, without calling the real LLM."""

from agents.job_parser import agent as job_agent
from agents.resume_analyzer import agent as analyzer_agent
from agents.resume_parser import agent as resume_agent
from graph.workflow import run_analysis
from models.analysis import Analysis
from models.job import Job
from models.resume import Resume


def test_pipeline_passes_data_between_agents(monkeypatch):
    monkeypatch.setattr(resume_agent, "parse_resume", lambda text: Resume(full_name=text))
    monkeypatch.setattr(job_agent, "parse_job", lambda text: Job(title=text))
    monkeypatch.setattr(
        analyzer_agent,
        "analyze",
        lambda resume, job: Analysis(summary=f"{resume.full_name} vs {job.title}"),
    )

    result = run_analysis("Alice", "Engineer")

    assert result["resume"].full_name == "Alice"
    assert result["job"].title == "Engineer"
    assert result["analysis"].summary == "Alice vs Engineer"
