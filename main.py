"""Command-line entry point.

Usage:
    python main.py --resume samples/resume.txt --job samples/job.txt
    python main.py --resume samples/resume.txt --job samples/job.txt --json
"""

import argparse
import json
import sys
from pathlib import Path

from graph.workflow import run_analysis
from models.analysis import Analysis


def print_report(analysis: Analysis) -> None:
    print("\n=== Resume Analysis ===")
    print(f"Overall score    : {analysis.overall_score}/100")
    print(f"Skills score     : {analysis.skills_score}/100")
    print(f"Experience score : {analysis.experience_score}/100")
    print(f"Education score  : {analysis.education_score}/100")

    print("\nMatched skills:")
    for skill in analysis.matched_skills:
        print(f"  + {skill}")

    print("\nSkill gaps:")
    for gap in analysis.skill_gaps:
        print(f"  - {gap.skill} ({gap.importance}): {gap.suggestion}")

    print("\nStrengths:")
    for item in analysis.strengths:
        print(f"  * {item}")

    print("\nImprovements:")
    for item in analysis.improvements:
        print(f"  * {item}")

    print(f"\nSummary: {analysis.summary}\n")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # LLM output may contain non-ASCII characters
    parser = argparse.ArgumentParser(description="Analyze a resume against a job description.")
    parser.add_argument("--resume", required=True, help="Path to a .txt file with the resume")
    parser.add_argument("--job", required=True, help="Path to a .txt file with the job description")
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON")
    args = parser.parse_args()

    resume_text = Path(args.resume).read_text(encoding="utf-8")
    job_text = Path(args.job).read_text(encoding="utf-8")

    result = run_analysis(resume_text, job_text)

    if args.json:
        output = {key: result[key].model_dump() for key in ("resume", "job", "analysis")}
        print(json.dumps(output, indent=2))
    else:
        print_report(result["analysis"])


if __name__ == "__main__":
    main()
