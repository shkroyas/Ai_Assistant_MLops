"""Summarize completed native-judged runs without treating partial runs as benchmarks."""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def summarize():
    rows = []
    for directory in sorted(
        (p for p in Path("reports").glob("v*") if p.is_dir() and p.name[1:].isdigit()),
        key=lambda p: int(p.name[1:]),
    ):
        required = [
            directory / name for name in ["metrics.json", "gate.json", "evidently_judge.json"]
        ]
        if not all(path.is_file() for path in required):
            continue
        metrics, decision = (json.loads(path.read_text()) for path in required[:2])
        if "pct_judge_passed" not in metrics:
            continue
        rows.append(
            {
                "version": directory.name,
                "run_id": decision["run_id"],
                "development_completion": metrics["task_completion_rate"],
                "golden_truth_pass": metrics["pct_ground_truth_passed"],
                "judge_pass": metrics["pct_judge_passed"],
                "truth_and_judge_pass": metrics["pct_tests_passed"],
                "tokens_per_development_query": metrics["tokens_per_query_mean"],
                "development_latency_seconds": metrics["latency_mean"],
                "gate": decision["verdict"],
            }
        )
    if not rows:
        raise RuntimeError("No completed native-judged experiment evidence")
    with Path("reports/completed_experiments.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# Completed live experiments",
        "",
        "35 development and 18 frozen golden questions, each repeated three times. "
        "Agents: KU Qwen2.5-7B (v1–v12), Groq Qwen3.8-27B (v14); "
        "independent judge: Groq GPT-OSS-20B. "
        "Only versions with completed native judge reports are shown. "
        "All MLflow runs, including interrupted and agent-only phases, remain in mlflow_comparison.csv.",
        "",
        "| Version | Dev completion | Golden truth | Judge | Both | Dev tokens/query | Dev latency | Gate |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['version']} | {row['development_completion']:.2%} | "
            f"{row['golden_truth_pass']:.2%} | {row['judge_pass']:.2%} | "
            f"{row['truth_and_judge_pass']:.2%} | {row['tokens_per_development_query']:.2f} | "
            f"{row['development_latency_seconds']:.2f}s | {row['gate']} |"
        )
    lines += [
        "",
        "Ground-truth floor: 85%; judge floor: 80%. "
        "A cost reduction cannot compensate for failing quality or safety checks.",
        "v14 exhausted its local quota budget during golden evaluation: 31/54 "
        "golden traces terminated provider_unavailable. Its aggregate golden rates "
        "include those failures and cannot isolate model quality. See "
        "[infrastructure audit](v14/infrastructure_audit.json).",
        "",
    ]
    lines += [
        f"- {row['version']}: MLflow run `{row['run_id']}`; "
        f"[native judge report]({row['version']}/evidently_judge.html)."
        for row in rows
    ]
    Path("reports/completed_experiments.md").write_text("\n".join(lines) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    versions = [row["version"] for row in rows]
    axes[0].plot(
        versions, [100 * row["golden_truth_pass"] for row in rows], "o-", label="Golden truth"
    )
    axes[0].plot(
        versions, [100 * row["judge_pass"] for row in rows], "s-", label="Independent judge"
    )
    axes[0].axhline(85, color="gray", linestyle="--", label="Truth floor 85%")
    axes[0].axhline(80, color="gray", linestyle=":", label="Judge floor 80%")
    axes[0].set(ylim=(0, 100), ylabel="Pass rate (%)", title="Held-out quality")
    axes[0].legend(fontsize=8)
    axes[1].bar(versions, [row["tokens_per_development_query"] for row in rows], color="#375f87")
    axes[1].set(ylabel="Actual provider tokens per query", title="Development cost proxy")
    fig.suptitle("Live coursework experiments — production requires a passing gate")
    fig.savefig("reports/cost_quality.png", dpi=160)
    plt.close(fig)
    print(f"Summarized {len(rows)} completed judged versions")


if __name__ == "__main__":
    summarize()
