"""Predeclared promotion policy; missing judge/cost evidence fails closed."""

import yaml
from pathlib import Path


def gate(candidate, production=None):
    bars = yaml.safe_load(Path("configs/gate.yaml").read_text())
    checks = {
        "calibration_reviewed": candidate.get("calibration_human_reviewed", 0) == 1,
        "ground_truth": candidate.get("pct_ground_truth_passed", 0) >= bars["ground_truth_min"],
        "judge": candidate.get("pct_judge_passed", 0) >= bars["judge_min"],
        "calibration": candidate.get("judge_label_agreement", 0)
        >= bars["judge_label_agreement_min"],
        "judge_truth_agreement": candidate.get("judge_truth_agreement", 0)
        >= bars["judge_truth_agreement_min"],
        "tool_correctness": candidate.get("tool_call_correctness", 0)
        >= bars["tool_correctness_min"],
        "hard_failure": candidate.get("hard_failure_rate", 1) <= bars["hard_failure_max"],
        "failure_injection": candidate.get("failure_injection_safe", 0) == 1,
        "token_usage_known": candidate.get("usage_complete", 0) == 1,
    }
    if production:
        tolerance = max(bars["completion_drop"], 2 * production.get("completion_spread", 0))
        checks.update(
            {
                "completion_regression": candidate.get("task_completion_rate", 0)
                >= production["task_completion_rate"] - tolerance,
                "truth_regression": candidate.get("pct_ground_truth_passed", 0)
                >= production["pct_ground_truth_passed"] - 0.05,
                "token_budget": candidate.get("tokens_per_query_mean", float("inf"))
                <= bars["token_ratio_max"] * production["tokens_per_query_mean"],
                "step_budget": candidate.get("trajectory_length_mean", float("inf"))
                <= bars["step_ratio_max"] * production["trajectory_length_mean"],
            }
        )
    return {"verdict": "PROMOTE" if all(checks.values()) else "REJECT", "checks": checks}
