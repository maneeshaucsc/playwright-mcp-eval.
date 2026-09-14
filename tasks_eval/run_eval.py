"""Run the browser agent over every labeled task, verify the outcome, and
save per-task + aggregate results.

Usage:
    python tasks_eval/run_eval.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "agent"))

import pandas as pd  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from config import REPORTS_DIR, SITE_PATH, TASKS_PATH  # noqa: E402
from run_agent import run_task  # noqa: E402
from verifiers import VERIFIERS  # noqa: E402


def load_tasks() -> list[dict]:
    with open(TASKS_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    tasks = load_tasks()
    print(f"Loaded {len(tasks)} tasks.")
    site_url = SITE_PATH.resolve().as_uri()

    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for i, task in enumerate(tasks, start=1):
            print(f"[{i}/{len(tasks)}] {task['id']}: {task['task']}")
            # Fresh context per task = fresh localStorage = deterministic starting state.
            context = browser.new_context()
            page = context.new_page()
            page.goto(site_url)

            trajectory = run_task(page, task["task"])
            actual_success = VERIFIERS[task["id"]](page)

            steps_taken = trajectory["steps_taken"] - 1  # exclude the final `finish` call
            step_efficiency = (
                min(task["min_steps"] / steps_taken, 1.0) if steps_taken > 0 else (1.0 if task["min_steps"] == 0 else 0.0)
            )

            rows.append({
                "id": task["id"],
                "task": task["task"],
                "min_steps": task["min_steps"],
                "steps_taken": steps_taken,
                "step_efficiency": round(step_efficiency, 3),
                "invalid_actions": trajectory["invalid_actions"],
                "actual_success": actual_success,
                "self_reported_success": trajectory["self_reported_success"],
                "self_reported_reason": trajectory["self_reported_reason"],
                "calibrated": actual_success == trajectory["self_reported_success"],
                "trajectory": json.dumps(trajectory["actions"]),
            })

            context.close()
            time.sleep(0.2)

        browser.close()

    df = pd.DataFrame(rows)
    out_path = REPORTS_DIR / "results.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved -> {out_path}")
    print(f"Task success rate: {df['actual_success'].mean():.3f}")
    print(f"Calibration (self-report matches actual): {df['calibrated'].mean():.3f}")
    print(f"Avg step efficiency: {df['step_efficiency'].mean():.3f}")
    print(f"Total invalid actions: {df['invalid_actions'].sum()}")


if __name__ == "__main__":
    main()
