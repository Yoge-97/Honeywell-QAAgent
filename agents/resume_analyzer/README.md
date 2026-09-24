# Resume Analyzer agent

Owner branch: `feature/resume-analyzer`

Compares the parsed resume with the parsed job, then (if the user wants) writes a tailored
resume, lets the user review it, and exports it.

## Flow

```
resume_analyzer ──> ask_to_tailor ──no──> END
                        │ yes
                        ▼
                  resume_tailor <──────────── revise (with feedback, max 3)
                        │                         │
                        ▼                         │
                  human_review ───────────────────┘
                   │  ▲    │
             edit  └──┘    │ approve
                           ▼
                     ask_to_export ──no──> END
                           │ yes
                           ▼
                       exporter ──> output/tailored_resume.docx + .pdf
```

`ask_to_tailor`, `human_review` and `ask_to_export` **pause** the graph with LangGraph's `interrupt()`.
The checkpointer keeps the state while it waits. The caller shows the question to the user and
continues with `graph.invoke(Command(resume=answer), config)` using the same `config` (thread id).

| Pause | Answer to send |
| --- | --- |
| `ask_to_tailor` | `True` or `False` |
| `human_review` | `{"action": "approve"}` |
| | `{"action": "edit", "tailored_resume": {...}}` — saved as-is, no LLM call |
| | `{"action": "revise", "feedback": "..."}` — the tailor rewrites the draft |
| `ask_to_export` | `True` (save DOCX + PDF) or `False` (finish without files) |

## Files

| File | What it does |
| --- | --- |
| `agent.py` | `analyze()`: scores, matched skills, skill gaps, improvements |
| `tailor.py` | `tailor_resume()`: rewrites the resume for the job. Never invents facts |
| `review.py` | The three pause points and the approve / edit / revise routing |
| `export.py` | `to_docx()`, `to_pdf()`: plain Python, no LLM |
| `models.py` | `TailoredResume`, `TailoredExperience` |
| `prompts.py` | Prompts for the analyzer and the tailor |
| `cli.py` | Terminal version of the pause questions (used by `main.py`) |
| `app.py` | Streamlit UI with live editing |

## Run

```bash
python main.py                                  # terminal
streamlit run agents/resume_analyzer/app.py     # browser
pytest tests/test_resume_analyzer.py            # tests, no API key needed
```

In the terminal, choosing **edit** writes the draft to `output/draft.json`. Edit it in your
editor, save, and press Enter.

## Tailoring rules

The tailor may reword, reorder, and emphasize, but must never add skills, jobs, numbers, or a
seniority level that isn't in the original resume. Missing skills stay in the analysis as advice.
If you change `TAILOR_SYSTEM_PROMPT`, check a few outputs for invented claims.

## Shared files this feature changed

Flag these in the PR, because the other agents depend on them:

- `graph/state.py`: new keys `tailor`, `tailored_resume`, `feedback`, `revision_count`, `export`, `export_paths`
- `graph/workflow.py`: new nodes, a checkpointer, and `new_session()`
- `main.py`: the pause/answer loop
- `requirements.txt`: `python-docx`, `fpdf2`, `streamlit`
- `.gitignore`: `output/`
