"""Aggregate results.csv into a chart + markdown report."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "agent"))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from config import REPORTS_DIR  # noqa: E402


def make_chart(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    metrics = {
        "Task Success Rate": df["actual_success"].mean(),
        "Calibration\n(self-report matches actual)": df["calibrated"].mean(),
        "Avg Step Efficiency": df["step_efficiency"].mean(),
    }
    ax.bar(metrics.keys(), metrics.values(), color=["#4C72B0", "#55A868", "#C44E52"])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score (0-1)")
    ax.set_title("Browser-Agent Eval: aggregate metrics across 10 tasks")
    for i, v in enumerate(metrics.values()):
        ax.text(i, v + 0.02, f"{v:.2f}", ha="center")
    fig.tight_layout()

    out_path = REPORTS_DIR / "agent_eval_chart.png"
    fig.savefig(out_path, dpi=150)
    return out_path


def make_report(df: pd.DataFrame, chart_path: Path) -> Path:
    lines = ["# Browser-Agent Evaluation Report", ""]
    lines.append(f"Total tasks: {len(df)} (including 1 deliberately impossible task)")
    lines.append("")
    lines.append(f"- **Task success rate:** {df['actual_success'].mean():.3f}")
    lines.append(f"- **Calibration** (self-reported outcome matches ground truth): {df['calibrated'].mean():.3f}")
    lines.append(f"- **Avg step efficiency:** {df['step_efficiency'].mean():.3f}")
    lines.append(f"- **Total invalid actions:** {int(df['invalid_actions'].sum())}")
    lines.append("")
    lines.append(f"![agent eval chart]({chart_path.name})")
    lines.append("")
    lines.append("## Per-task results")
    lines.append("")
    table = df[["id", "task", "steps_taken", "step_efficiency", "actual_success", "self_reported_success", "calibrated"]]
    lines.append(table.to_markdown(index=False))
    lines.append("")

    out_path = REPORTS_DIR / "AGENT_EVAL_REPORT.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main():
    df = pd.read_csv(REPORTS_DIR / "results.csv")
    chart_path = make_chart(df)
    report_path = make_report(df, chart_path)
    print(f"Chart  -> {chart_path}")
    print(f"Report -> {report_path}")


if __name__ == "__main__":
    main()
