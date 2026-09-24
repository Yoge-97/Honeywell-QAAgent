"""Terminal version of the human-in-the-loop questions, used by main.py."""

import json
from pathlib import Path

from agents.resume_analyzer.models import TailoredResume

DRAFT_FILE = Path("output/draft.json")


def answer_interrupt(payload: dict):
    """Show a paused graph's question in the terminal and return the user's answer."""
    if payload["type"] == "ask_to_tailor":
        return input(f"\n{payload['question']} [y/n] > ").strip().lower().startswith("y")
    return review_in_terminal(payload)


def print_resume(resume: TailoredResume) -> None:
    print(f"\n=== Tailored resume: {resume.full_name} ===")
    print(f"Summary: {resume.summary}")
    print(f"Skills : {', '.join(resume.skills)}")
    for job in resume.experience:
        print(f"\n{job.job_title} - {job.company} ({job.dates})")
        for bullet in job.bullets:
            print(f"  - {bullet}")
    print("\nChanges made:")
    for change in resume.changes_made:
        print(f"  * {change}")


def review_in_terminal(payload: dict) -> dict:
    resume = TailoredResume(**payload["tailored_resume"])
    revisions_left = payload["max_revisions"] - payload["revision_count"]
    print_resume(resume)

    choice = input(f"\n[a] approve  [e] edit  [r] revise ({revisions_left} left) > ").strip().lower()

    if choice == "a":
        return {"action": "approve"}

    if choice == "e":
        DRAFT_FILE.parent.mkdir(exist_ok=True)
        DRAFT_FILE.write_text(resume.model_dump_json(indent=2), encoding="utf-8")
        input(f"Edit {DRAFT_FILE} in your editor, save it, then press Enter...")
        try:
            edited = json.loads(DRAFT_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            print(f"Could not read your edits ({error}). Showing the draft again.")
            return {"action": "show_again"}
        return {"action": "edit", "tailored_resume": edited}

    if choice == "r":
        if revisions_left <= 0:
            print("No revisions left. Please edit or approve.")
            return {"action": "show_again"}
        return {"action": "revise", "feedback": input("What should change? > ")}

    return {"action": "show_again"}
