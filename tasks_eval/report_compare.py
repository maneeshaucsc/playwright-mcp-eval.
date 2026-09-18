"""Compare the hand-rolled agent (results.csv) against the Playwright-MCP-backed
agent (results_mcp.csv) on the same 10 tasks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "agent"))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from config import REPORTS_DIR  # noqa: E402


def main():
    hand = pd.read_csv(REPORTS_DIR / "results.csv")
    mcp = pd.read_csv(REPORTS_DIR / "results_mcp.csv")

    summary = pd.DataFrame({
        "Hand-rolled actions": {
            "Task Success Rate": hand["actual_success"].mean(),
            "Calibration": hand["calibrated"].mean(),
            "Invalid Actions (total)": hand["invalid_actions"].sum(),
            "Avg Steps Taken": hand["steps_taken"].mean(),
        },
        "Playwright MCP": {
            "Task Success Rate": mcp["actual_success"].mean(),
            "Calibration": mcp["calibrated"].mean(),
            "Invalid Actions (total)": mcp["invalid_actions"].sum(),
            "Avg Steps Taken": mcp["steps_taken"].mean(),
        },
    })

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    rate_metrics = ["Task Success Rate", "Calibration"]
    summary.loc[rate_metrics].plot(kind="bar", ax=axes[0], legend=True, color=["#4C72B0", "#DD8452"])
    axes[0].legend(loc="lower right", fontsize=8)
    axes[0].set_ylim(0, 1.15)
    axes[0].set_title("Success & Calibration")
    axes[0].tick_params(axis="x", rotation=20)
    for container in axes[0].containers:
        axes[0].bar_label(container, fmt="%.2f")

    summary.loc[["Invalid Actions (total)"]].plot(kind="bar", ax=axes[1], legend=False, color=["#4C72B0", "#DD8452"])
    axes[1].set_title("Invalid Actions (total, 10 tasks)")
    axes[1].tick_params(axis="x", rotation=20)
    for container in axes[1].containers:
        axes[1].bar_label(container, fmt="%.0f")

    summary.loc[["Avg Steps Taken"]].plot(kind="bar", ax=axes[2], legend=False, color=["#4C72B0", "#DD8452"])
    axes[2].set_title("Avg Steps Taken*")
    axes[2].tick_params(axis="x", rotation=20)
    for container in axes[2].containers:
        axes[2].bar_label(container, fmt="%.1f")

    fig.suptitle("Hand-rolled action space vs. Playwright MCP: same 10 tasks")
    fig.tight_layout()
    chart_path = REPORTS_DIR / "comparison_chart.png"
    fig.savefig(chart_path, dpi=150)

    lines = ["# Hand-Rolled vs. Playwright MCP: Agent Comparison", ""]
    lines.append(
        "Same 10 labeled tasks, same Claude model, same TaskFlow app -- only the "
        "action/perception layer differs: a small hand-written tool schema "
        "(`agent/actions.py` + `agent/state.py`) vs. the real Playwright MCP server."
    )
    lines.append("")
    lines.append(summary.round(3).to_markdown())
    lines.append("")
    lines.append(f"![comparison chart]({chart_path.name})")
    lines.append("")
    lines.append(
        "*Step counts aren't perfectly apples-to-apples: the MCP agent must "
        "explicitly call `browser_snapshot` to see the page (a real action, "
        "counted here), while the hand-rolled agent was handed a text "
        "description of the page for free each turn. The MCP agent's higher "
        "step count partly reflects that extra, more realistic perception cost."
    )
    lines.append("")
    lines.append(
        "**Finding:** both approaches hit the same 90% success rate and 100% "
        "calibration -- neither the hand-rolled action space nor the standard "
        "MCP one was the bottleneck here; Claude's underlying tool-use behavior "
        "was the limiting factor either way. The real difference is invalid "
        "actions: the MCP agent guessed a wrong `target` format (an element "
        "description instead of a snapshot ref) a few times before "
        "self-correcting, something the hand-rolled tool schema's simpler "
        "role+name interface didn't allow it to get wrong in the first place."
    )

    report_path = REPORTS_DIR / "COMPARISON_REPORT.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Chart  -> {chart_path}")
    print(f"Report -> {report_path}")
    print()
    print(summary.round(3))


if __name__ == "__main__":
    main()
