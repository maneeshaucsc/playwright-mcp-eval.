from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SITE_PATH = ROOT / "site" / "index.html"
TASKS_PATH = ROOT / "tasks_eval" / "tasks.jsonl"
REPORTS_DIR = ROOT / "tasks_eval" / "reports"

AGENT_MODEL = "claude-sonnet-5"
MAX_STEPS = 8

AGENT_SYSTEM_PROMPT = """You control a simple to-do list web app called TaskFlow by choosing one \
action per turn. You are given a task in plain English and a text description of the \
currently visible interactive elements on the page.

Available actions (call exactly one tool per turn):
- fill: type text into a textbox
- click: click a checkbox, button, or tab
- finish: declare that you are done, with success=true/false and a short reason

Rules:
- Only act on elements that appear in the page description you're given -- don't guess \
element names that aren't listed.
- If the task cannot be completed with the elements available (e.g. it refers to a task \
that doesn't exist), call finish with success=false and explain why.
- Call finish as soon as the task is complete. Don't take extra actions.
- You have a limited number of turns, so don't waste them re-checking state unnecessarily.
"""
