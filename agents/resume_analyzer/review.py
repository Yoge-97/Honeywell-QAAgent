"""Human in the loop: nodes where the graph pauses and waits for the user.

`interrupt(payload)` stops the graph and hands `payload` to the caller (main.py or app.py).
The caller shows it to the user and continues the graph with `Command(resume=answer)`;
`answer` then becomes the return value of `interrupt(...)`.
"""

from langgraph.graph import END
from langgraph.types import Command, interrupt

from agents.resume_analyzer.models import TailoredResume
from graph.state import AnalyzerState

MAX_REVISIONS = 3


def ask_to_tailor_node(state: AnalyzerState) -> dict:
    """Pause after the analysis and ask whether to create a tailored resume.

    Expected answer: True or False.
    """
    answer = interrupt({"type": "ask_to_tailor", "question": "Create a tailored resume for this job?"})
    return {"tailor": bool(answer)}


def route_after_ask(state: AnalyzerState) -> str:
    return "resume_tailor" if state.get("tailor") else END


def human_review_node(state: AnalyzerState) -> Command:
    """Pause and let the user approve, edit, or ask for a revision of the tailored resume.

    Expected answer, one of:
        {"action": "approve"}
        {"action": "edit", "tailored_resume": {...edited resume as a dict...}}
        {"action": "revise", "feedback": "make the summary shorter"}
    """
    revision_count = state.get("revision_count", 0)
    decision = interrupt(
        {
            "type": "human_review",
            "tailored_resume": state["tailored_resume"].model_dump(),
            "revision_count": revision_count,
            "max_revisions": MAX_REVISIONS,
        }
    )
    action = decision.get("action")

    if action == "approve":
        return Command(goto="exporter")

    if action == "edit":
        edited = TailoredResume(**decision["tailored_resume"])
        return Command(goto="human_review", update={"tailored_resume": edited})

    if action == "revise" and revision_count < MAX_REVISIONS:
        return Command(
            goto="resume_tailor",
            update={"feedback": decision.get("feedback", ""), "revision_count": revision_count + 1},
        )

    # Unknown action, or no revisions left: show the same draft again.
    return Command(goto="human_review")
