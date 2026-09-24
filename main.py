"""Run the resume analyzer.

Usage:
    python main.py

To analyze your own files, change RESUME_FILE and JOB_FILE below.
"""

import sys

from langgraph.types import Command

from agents.resume_analyzer.cli import answer_interrupt
from graph.workflow import build_graph, new_session

RESUME_FILE = "samples/resume.txt"
JOB_FILE = "samples/job.txt"

# Windows consoles can't print some characters the LLM returns, so use UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

# 1. Read the two input files
with open(RESUME_FILE, encoding="utf-8") as f:
    resume_text = f.read()

with open(JOB_FILE, encoding="utf-8") as f:
    job_text = f.read()

# 2. Run the agents (resume parser + job parser -> resume analyzer)
graph = build_graph()
config = new_session()
result = graph.invoke({"resume_text": resume_text, "job_text": job_text}, config)

# 3. Print the analysis
print(result["analysis"].model_dump_json(indent=2))

# 4. The graph pauses when it needs you (tailor? approve/edit/revise? export?). Answer until it finishes.
while "__interrupt__" in result:
    answer = answer_interrupt(result["__interrupt__"][0].value)
    result = graph.invoke(Command(resume=answer), config)

if "export_paths" in result:
    print(f"\nSaved: {result['export_paths']['docx']} and {result['export_paths']['pdf']}")
elif result.get("tailored_resume"):
    print("\nTailored resume approved. No files were exported.")
