import json
from pathlib import Path

import pytest
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import INTERNAL_ERROR, RESOURCE_DOES_NOT_EXIST

from assistant_mlops.production import production_baseline


def test_clean_clone_uses_matching_passed_live_evidence(monkeypatch, tmp_path):
    policy = Path("configs/gate.yaml").read_text()
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs/gate.yaml").write_text(policy)
    monkeypatch.chdir(tmp_path)

    def missing_run(_):
        raise MlflowException("Fixture run absent", error_code=RESOURCE_DOES_NOT_EXIST)

    monkeypatch.setattr("assistant_mlops.production.mlflow.get_run", missing_run)
    metrics = {
        "calibration_review_approved": 1,
        "pct_ground_truth_passed": 1,
        "pct_judge_passed": 1,
        "judge_label_agreement": 1,
        "judge_truth_agreement": 1,
        "tool_call_correctness": 1,
        "hard_failure_rate": 0,
        "failure_injection_safe": 1,
        "usage_complete": 1,
        "golden_provider_failure_rate": 0,
    }
    directory = tmp_path / "reports/v17"
    directory.mkdir(parents=True)
    (directory / "metrics.json").write_text(json.dumps(metrics))
    decision = {
        "version": "v17",
        "run_id": "fixture-run",
        "verdict": "PROMOTE",
        "checks": {"all": True},
    }
    (directory / "gate.json").write_text(json.dumps(decision))
    baseline, source = production_baseline({"version": "v17", "run_id": "fixture-run"})
    assert baseline == metrics and source == "committed_live_report"
    with pytest.raises(ValueError, match="does not match"):
        production_baseline({"version": "v17", "run_id": "different-run"})
    metrics["pct_judge_passed"] = 0
    (directory / "metrics.json").write_text(json.dumps(metrics))
    with pytest.raises(ValueError, match="does not match"):
        production_baseline({"version": "v17", "run_id": "fixture-run"})


def test_tracking_errors_are_not_hidden_by_report_fallback(monkeypatch):
    def unavailable(_):
        raise MlflowException("Fixture tracking failure", error_code=INTERNAL_ERROR)

    monkeypatch.setattr("assistant_mlops.production.mlflow.get_run", unavailable)
    with pytest.raises(MlflowException):
        production_baseline({"version": "v17", "run_id": "fixture-run"})
