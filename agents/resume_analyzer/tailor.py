"""Resume Tailor: rewrites the resume to fit the job, without inventing anything."""

from langchain_core.prompts import ChatPromptTemplate

from agents.resume_analyzer.models import TailoredResume
from agents.resume_analyzer.prompts import TAILOR_HUMAN_PROMPT, TAILOR_SYSTEM_PROMPT
from graph.state import AnalyzerState
from models.analysis import Analysis
from models.job import Job
from models.resume import Resume
from services.llm import get_llm


def tailor_resume(
    resume: Resume,
    job: Job,
    analysis: Analysis,
    feedback: str = "",
    previous: TailoredResume | None = None,
) -> TailoredResume:
    """Create a tailored resume. Pass `feedback` and `previous` to revise an earlier draft."""
    prompt = ChatPromptTemplate.from_messages(
        [("system", TAILOR_SYSTEM_PROMPT), ("human", TAILOR_HUMAN_PROMPT)]
    )
    chain = prompt | get_llm().with_structured_output(TailoredResume)
    tailored = chain.invoke(
        {
            "resume_json": resume.model_dump_json(indent=2),
            "job_json": job.model_dump_json(indent=2),
            "analysis_json": analysis.model_dump_json(indent=2),
            "previous_json": previous.model_dump_json(indent=2) if previous else "",
            "feedback": feedback,
        }
    )

    # Contact details are copied from the parsed resume so the LLM can never change them.
    tailored.full_name = resume.full_name
    tailored.email = resume.email
    tailored.phone = resume.phone
    tailored.location = resume.location
    return tailored


def resume_tailor_node(state: AnalyzerState) -> dict:
    """LangGraph node: reads resume/job/analysis (+ feedback), writes `tailored_resume`."""
    tailored = tailor_resume(
        state["resume"],
        state["job"],
        state["analysis"],
        feedback=state.get("feedback", ""),
        previous=state.get("tailored_resume"),
    )
    return {"tailored_resume": tailored}
