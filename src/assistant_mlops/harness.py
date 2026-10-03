"""W16 evaluation harness, built from scratch; no evaluation framework here."""

import json
import os
import statistics
from pathlib import Path

from assistant_mlops.schemas import EvalCase


def load_cases(path):
    cases = [
        EvalCase.model_validate_json(line)
        for line in Path(path).read_text().splitlines()
        if line.strip()
    ]
    if not cases or len({c.id for c in cases}) != len(cases):
        raise ValueError("Evaluation IDs must be nonempty and unique")
    return cases


def assess(case, trace):
    answer = trace["answer"]
    sources = {s["source_id"] for s in answer["sources"]}
    correct = (
        answer["status"] == case.expected_status
        and all(term.lower() in answer["answer"].lower() for term in case.required_terms)
        and set(case.required_sources) <= sources
        and trace["iterations"] <= case.max_steps
    )
    calls = [s for s in trace["steps"] if s["event"] == "tool_call"]
    valid = sum(bool(c["valid"]) for c in calls)
    appropriate = 0
    for call in calls:
        result = call.get("result")
        found = (
            {r["source_id"] for r in result}
            if isinstance(result, list)
            else {result["source_id"]}
            if isinstance(result, dict) and "source_id" in result
            else set()
        )
        appropriate += bool(
            call["valid"]
            and (
                not case.required_sources
                or bool(found & set(case.required_sources))
                or case.failure
            )
        )
    if correct:
        failure = None
    elif trace["termination"] in {"provider_unavailable", "tool_budget_exceeded"}:
        failure = "hard_failure"
    elif (
        trace["tool_errors"] > 1 or sum(s["event"] == "invalid_answer" for s in trace["steps"]) > 1
    ):
        failure = "cascading_soft_failure"
    else:
        failure = "soft_failure"
    return {
        "case_id": case.id,
        "category": case.category,
        "completed": correct,
        "tool_calls": len(calls),
        "valid_calls": valid,
        "appropriate_calls": appropriate,
        "failure_class": failure,
        "iterations": trace["iterations"],
        "tokens": trace["tokens"],
        "usage_complete": trace["usage_complete"],
        "latency_seconds": trace["latency_seconds"],
        "reference": case.reference,
        "response": answer["answer"],
        "injected": bool(case.failure),
        "prompt_tokens": trace.get("prompt_tokens", 0),
        "completion_tokens": trace.get("completion_tokens", 0),
        "query": case.question,
        "status": answer["status"],
        "trace": trace,
    }


async def evaluate(agent, cases, repeats=3):
    rows, rates = [], []
    for repeat in range(repeats):
        group = []
        for case in cases:
            trace = await agent.run(case.question, failure=case.failure)
            row = assess(case, trace)
            row["repeat"] = repeat
            rows.append(row)
            group.append(row["completed"])
        rates.append(statistics.mean(group))
    count = len(rows)
    if not count:
        raise ValueError("No cases evaluated")
    calls = sum(r["tool_calls"] for r in rows)
    injected = [r for r in rows if r["injected"]]
    summary = {
        "task_completion_rate": statistics.mean(r["completed"] for r in rows),
        # Syntactic validity plus completed grounded trajectory; final-answer evidence
        # coverage makes inappropriate but syntactically valid tool choices visible.
        "tool_call_correctness": sum(r["appropriate_calls"] for r in rows) / calls if calls else 0,
        "tool_argument_validity": sum(r["valid_calls"] for r in rows) / calls if calls else 0,
        "trajectory_length_mean": statistics.mean(r["iterations"] for r in rows),
        "tokens_per_query_mean": statistics.mean(r["tokens"] for r in rows),
        "usage_complete": float(all(r["usage_complete"] for r in rows)),
        "latency_mean": statistics.mean(r["latency_seconds"] for r in rows),
        "completion_spread": max(rates) - min(rates),
        "hard_failure_rate": sum(r["failure_class"] == "hard_failure" for r in rows) / count,
        "failure_injection_safe": (
            statistics.mean(r["status"] in {"abstain", "clarify"} for r in injected)
            if injected
            else 0
        ),
    }
    if os.getenv("INPUT_USD_PER_MILLION") and os.getenv("OUTPUT_USD_PER_MILLION"):
        known = []
        for row in rows:
            valid = row["usage_complete"] and (
                row["prompt_tokens"] + row["completion_tokens"] == row["tokens"]
            )
            row["estimated_cost_usd"] = None
            if valid:
                row["estimated_cost_usd"] = (
                    row["prompt_tokens"] * float(os.environ["INPUT_USD_PER_MILLION"])
                    + row["completion_tokens"] * float(os.environ["OUTPUT_USD_PER_MILLION"])
                ) / 1_000_000
                known.append(row["estimated_cost_usd"])
        summary["cost_usage_coverage"] = len(known) / len(rows)
        if len(known) == len(rows):
            summary["estimated_cost_usd_mean"] = statistics.mean(known)
    return rows, summary


def write_report(rows, metrics, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "harness.json").write_text(
        json.dumps(
            {
                "metrics": metrics,
                "cases": [{k: v for k, v in row.items() if k != "trace"} for row in rows],
            },
            indent=2,
        )
    )
    for row in rows:
        (directory / f"trace_{row['case_id']}_r{row['repeat']}.json").write_text(
            json.dumps(row["trace"], indent=2)
        )
    lines = ["# Harness results", "", "| Metric | Value |", "|---|---|"]
    lines.extend(f"| {k} | {v:.4f} |" for k, v in metrics.items())
    lines.extend(
        ["", "| Case | Repeat | Complete | Steps | Tokens | Failure |", "|---|---|---|---|---|---|"]
    )
    lines.extend(
        f"| {r['case_id']} | {r['repeat']} | {r['completed']} | {r['iterations']} | "
        f"{r['tokens']} | {r['failure_class'] or '—'} |"
        for r in rows
    )
    (directory / "harness.md").write_text("\n".join(lines) + "\n")
