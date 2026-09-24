"""Run the resume analyzer.

Usage:
    python main.py

To analyze your own files, change RESUME_FILE and JOB_FILE below.
"""

import sys

from graph.workflow import run_analysis

RESUME_FILE = "samples/resume.txt"
JOB_FILE = "samples/job.txt"

# Windows consoles can't print some characters the LLM returns, so use UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

# 1. Read the two input files
with open(RESUME_FILE, encoding="utf-8") as f:
    resume_text = f.read()

with open(JOB_FILE, encoding="utf-8") as f:
    job_text = f.read()

# 2. Run all three agents (resume parser + job parser -> resume analyzer)
result = run_analysis(resume_text, job_text)

# 3. Print the analysis
analysis = result["analysis"]
print(analysis.model_dump_json(indent=2))
