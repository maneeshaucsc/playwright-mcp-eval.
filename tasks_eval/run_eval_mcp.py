"""Run the MCP-based browser agent over the same 10 labeled tasks used by the
hand-rolled agent (run_eval.py), producing directly comparable results.

Serves the TaskFlow app itself (no manual second terminal needed), launches
one Playwright MCP server subprocess, and reuses that single browser session
across all tasks -- clearing localStorage between tasks to reset to the
default seed state.

Usage:
    python tasks_eval/run_eval_mcp.py
"""
import asyncio
import json
import sys
import threading
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "agent"))

import pandas as pd  # noqa: E402
from mcp import ClientSession  # noqa: E402
from mcp.client.stdio import StdioServerParameters, stdio_client  # noqa: E402

from config import REPORTS_DIR, TASKS_PATH  # noqa: E402
from mcp_agent_lib import run_task  # noqa: E402
from verifiers_mcp import VERIFIERS  # noqa: E402

SITE_DIR = Path(__file__).resolve().parent.parent / "site"
PORT = 8000
BASE_URL = f"http://localhost:{PORT}/index.html"


def start_server() -> HTTPServer:
    handler = partial(SimpleHTTPRequestHandler, directory=str(SITE_DIR))
    server = HTTPServer(("localhost", PORT), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def load_tasks() -> list[dict]:
    with open(TASKS_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


async def reset_and_get_snapshot(session) -> None:
    await session.call_tool("browser_navigate", {"url": BASE_URL})
    await session.call_tool("browser_evaluate", {"function": "() => { localStorage.clear(); }"})
    await session.call_tool("browser_navigate", {"url": BASE_URL})


async def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    start_server()
    tasks = load_tasks()
    print(f"Loaded {len(tasks)} tasks. Serving TaskFlow at {BASE_URL}")

    params = StdioServerParameters(command="npx", args=["-y", "@playwright/mcp@latest"])
    rows = []

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = (await session.list_tools()).tools

            for i, task in enumerate(tasks, start=1):
                print(f"[{i}/{len(tasks)}] {task['id']}: {task['task']}")
                await reset_and_get_snapshot(session)

                trajectory = await run_task(session, task["task"], mcp_tools)

                final_snapshot = await session.call_tool("browser_snapshot", {})
                snapshot_text = final_snapshot.content[0].text if final_snapshot.content else ""
                actual_success = VERIFIERS[task["id"]](snapshot_text)

                rows.append({
                    "id": task["id"],
                    "task": task["task"],
                    "steps_taken": trajectory["steps_taken"] - 1,  # exclude the final `finish` call
                    "invalid_actions": trajectory["invalid_actions"],
                    "actual_success": actual_success,
                    "self_reported_success": trajectory["self_reported_success"],
                    "self_reported_reason": trajectory["self_reported_reason"],
                    "calibrated": actual_success == trajectory["self_reported_success"],
                    "trajectory": json.dumps(trajectory["actions"]),
                })

    df = pd.DataFrame(rows)
    out_path = REPORTS_DIR / "results_mcp.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved -> {out_path}")
    print(f"Task success rate: {df['actual_success'].mean():.3f}")
    print(f"Calibration: {df['calibrated'].mean():.3f}")
    print(f"Avg steps taken: {df['steps_taken'].mean():.2f}")
    print(f"Total invalid actions: {int(df['invalid_actions'].sum())}")


if __name__ == "__main__":
    asyncio.run(main())
