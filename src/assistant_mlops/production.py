"""Load the actual promoted baseline in both the original workspace and a clean clone."""

import json
from pathlib import Path

import mlflow
from mlflow.exceptions import MlflowException

from assistant_mlops.gate import gate


def production_baseline(production):
    if not production.get("run_id"):
        return None, "none"
    try:
        return mlflow.get_run(production["run_id"]).data.metrics, "mlflow"
    except MlflowException as exc:
        if exc.error_code != "RESOURCE_DOES_NOT_EXIST":
            raise
    directory = Path("reports") / production["version"]
    decision = json.loads((directory / "gate.json").read_text())
    metrics = json.loads((directory / "metrics.json").read_text())
    if (
        decision.get("run_id") != production["run_id"]
        or decision.get("version") != production["version"]
        or decision.get("verdict") != "PROMOTE"
        or not decision.get("checks")
        or not all(decision["checks"].values())
        or gate(metrics)["verdict"] != "PROMOTE"
    ):
        raise ValueError("Committed production evidence does not match the promoted run")
    return metrics, "committed_live_report"
