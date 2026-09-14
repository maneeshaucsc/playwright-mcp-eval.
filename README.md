# Browser-Agent Evaluation Harness

A Playwright learning project that grew into a second AI-evaluation portfolio
piece: after learning Playwright fundamentals, I built an evaluation harness
for an AI agent that completes tasks *inside a web app* — clicking, typing,
and navigating — rather than just answering questions in text.

This follows the same evaluation-engineering methodology as my other project,
[rag-eval-project](https://github.com/maneeshaucsc/rag-eval-project), but for
a different kind of AI system: multi-step decision-making instead of text
generation. Together the two projects demonstrate evaluating both major
shapes of modern LLM applications.

## Part 1 — Playwright fundamentals (`lessons/`)

Four short scripts, each isolating one concept:

| Lesson | Concept |
|---|---|
| `01_launch_and_navigate.py` | Browser → Context → Page; navigating |
| `02_locators_and_actions.py` | Finding elements by role (the same way assistive tech — and browser AI agents — perceive a page); auto-waiting |
| `03_assertions.py` | `expect()` — the actual pass/fail mechanism, with built-in retry |
| `04_screenshots_and_trace.py` | Capturing evidence (screenshots, full interactive traces) for debugging failures |

## Part 2 — Browser-agent evaluation harness (`site/`, `agent/`, `tasks_eval/`)

**The system under test:** `site/index.html` — a small, self-contained to-do
list app ("TaskFlow"). Built specifically for this project so the environment
is fully controlled and deterministic (no flaky third-party sites, no rate
limits) — the same reasoning benchmarks like WebArena use self-hosted sandbox
sites.

**The agent:** `agent/run_agent.py` — Claude picks one action per turn via
tool use (`click`, `fill`, or `finish`), using a plain-text description of
the page's interactive elements (`agent/state.py`) as its only view of the
world. Playwright (`agent/actions.py`) executes each action and the resulting
page state is fed back for the next turn. This loop is a minimal version of
how real browser-agent systems work.

**The eval set:** `tasks_eval/tasks.jsonl` — 10 natural-language tasks against
a known starting state, including **one deliberately impossible task**
("mark a task complete that doesn't exist in the list") — the same trick as
the unanswerable questions in the RAG project, testing whether the agent
correctly reports failure instead of fabricating success.

**The metrics** (`tasks_eval/verifiers.py`, `tasks_eval/run_eval.py`):

| Metric | What it measures | How it's computed |
|---|---|---|
| Task Success Rate | Did the app end up in the correct state? | Ground-truth verifier per task, written as Playwright `expect()` assertions |
| Calibration | Does the agent's own self-reported success match the ground truth? | `self_reported_success == actual_success` |
| Step Efficiency | Did the agent solve the task in close to the minimum number of actions? | `min_steps / steps_taken`, capped at 1.0 |
| Invalid Actions | Did the agent try to act on an element that doesn't exist? | Counted whenever an action targets a non-existent element |

Calibration is the interesting one: a system can be *right* by accident, or
*wrong but confident*. Comparing an agent's own self-assessment against ground
truth is a real technique from LLM evaluation (the same idea as confidence
calibration in classifiers), applied here to agent behavior.

## Results

- **Task success rate: 0.90** (9/10) — every *completable* task succeeded.
  The one "failure" is the impossible task, which the agent correctly
  identified and refused rather than fabricating a completed action.
- **Calibration: 1.00** — the agent's self-reported outcome matched the
  ground-truth verifier on all 10 tasks, including correctly predicting its
  own failure on the impossible one.
- **Avg step efficiency: 1.00** — no wasted actions on any task.
- **Invalid actions: 0** — the agent never tried to act on an element that
  wasn't actually on the page.

Full per-task breakdown: `tasks_eval/reports/AGENT_EVAL_REPORT.md`.

![agent eval chart](tasks_eval/reports/agent_eval_chart.png)

## Design notes / limitations

- All 10 tasks passed, which is a clean result but not a very demanding test
  of the harness itself — a stronger version of this project would add
  adversarial or ambiguous tasks (e.g. two similarly-named items, a task that
  requires backtracking) to see where the agent actually breaks, the same way
  the RAG project's top_k comparison surfaced a real tradeoff.
- The agent's "perception" is a hand-simplified list of interactive elements,
  not the full accessibility tree — good enough for a small app, but a real
  system would need to handle much larger, messier pages.
- Each task runs in a fresh browser context (fresh `localStorage`), so results
  are deterministic and comparable across runs.

## Running it

```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # add your ANTHROPIC_API_KEY

python tasks_eval/run_eval.py   # runs the agent on all 10 tasks
python tasks_eval/report.py     # generates the chart + report
```
