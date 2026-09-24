# Resume Analyzer

Compares a resume with a job description and returns match scores, matched skills,
skill gaps, and concrete improvements.

Built with **LangGraph** (orchestration), **ChatGroq** (LLM), and **Pydantic** (structured output).

## How it works

```
                 ┌──────────────────┐
  resume text ──>│  Resume Parser   │── Resume ──┐
                 └──────────────────┘            │    ┌───────────────────┐
                                                 ├──> │  Resume Analyzer  │──> Analysis
                 ┌──────────────────┐            │    └───────────────────┘
  job text ─────>│   Job Parser     │── Job ─────┘
                 └──────────────────┘
```

1. **Resume Parser** turns raw resume text into a `Resume` model.
2. **Job Parser** turns raw job-description text into a `Job` model.
3. **Resume Analyzer** compares the two and produces an `Analysis`: scores, matched skills,
   skill gaps, strengths, and improvements.

The two parsers run in parallel. The analyzer runs once both have finished.

Each parser uses `llm.with_structured_output(PydanticModel)`. The LLM reads the
`Field(description=...)` text in the model to decide what goes in each field, so **improving
those descriptions is the easiest way to improve extraction quality**.

## Project structure

```
agents/
  resume_parser/     agent.py, prompts.py   <- Developer 1 (feature/resume-parser)
  job_parser/        agent.py, prompts.py   <- Developer 2 (feature/job-parser)
  resume_analyzer/   agent.py, prompts.py   <- Developer 3 (feature/resume-analyzer)
models/              Pydantic schemas: resume.py, job.py, analysis.py   (shared)
services/llm.py      get_llm(): the single place ChatGroq is created    (shared)
graph/state.py       AnalyzerState passed between agents                (shared)
graph/workflow.py    LangGraph wiring                                   (shared)
samples/             Example resume and job description
tests/               pytest tests
main.py              CLI entry point
```

## Setup

Requires Python 3.10+.

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and set `GROQ_API_KEY`. You can get a free key at <https://console.groq.com/keys>.

## Run

```bash
python main.py --resume samples/resume.txt --job samples/job.txt
python main.py --resume samples/resume.txt --job samples/job.txt --json   # full output
```

Run the tests (these don't call the LLM, so no API key is needed):

```bash
pytest
```

## Working on your agent

Each agent is its own feature with its own folder and branch.

| Agent           | Folder                     | Branch                    | Input            | Output                 |
| --------------- | -------------------------- | ------------------------- | ---------------- | ---------------------- |
| Resume Parser   | `agents/resume_parser/`    | `feature/resume-parser`   | `resume_text`    | `resume` (`Resume`)    |
| Job Parser      | `agents/job_parser/`       | `feature/job-parser`      | `job_text`       | `job` (`Job`)          |
| Resume Analyzer | `agents/resume_analyzer/`  | `feature/resume-analyzer` | `resume`, `job`  | `analysis` (`Analysis`)|

Every agent follows the same pattern in `agent.py`:

```python
def parse_resume(resume_text: str) -> Resume:          # plain function, easy to test
    ...

def resume_parser_node(state: AnalyzerState) -> dict:   # LangGraph node wrapper
    return {"resume": parse_resume(state["resume_text"])}
```

A node returns **only the state key it owns**. On `main`, each agent is a stub that returns an
empty model, so the whole pipeline runs even before your agent is finished.

To try your agent on its own:

```bash
python -c "from agents.resume_parser.agent import parse_resume; print(parse_resume(open('samples/resume.txt').read()).model_dump_json(indent=2))"
```

### Git workflow

```bash
git checkout main && git pull
git checkout feature/<your-agent>        # e.g. feature/resume-parser
# ...work only inside agents/<your_agent>/ ...
git add agents/<your_agent>
git commit -m "resume-parser: <what changed>"
git push -u origin feature/<your-agent>
# open a Pull Request into main
```

Rules that keep merges conflict-free:

- **Stay inside your agent's folder.** You don't need to touch other folders for normal work.
- **Shared files** (`models/`, `graph/`, `services/`, `main.py`) are a contract between all three
  agents. Change them in a separate small PR and tell the other developers, because adding or
  renaming a field can break someone else's agent.
- Keep your branch up to date with `git pull origin main` (or `git rebase main`) before opening a PR.
- Run `pytest` before pushing.
