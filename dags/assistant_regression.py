"""Nightly ground-truth regression; infrastructure failures have a separate branch."""

import json
import os
import runpy
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen

import yaml

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.python import BranchPythonOperator, PythonOperator

ROOT = Path(os.getenv("PROJECT_DIR", "/opt/project"))


def health_branch():
    try:
        production = yaml.safe_load((ROOT / "configs/production.yaml").read_text())
        selected = (
            f"configs/{production['version']}.yaml"
            if production.get("version")
            else os.getenv("ASSISTANT_CONFIG", "configs/v1.yaml")
        )
        config = yaml.safe_load((ROOT / selected).read_text())
        groq = config.get("provider") == "groq"
        base = "https://api.groq.com/openai/v1" if groq else os.getenv("AGENT_BASE_URL", "")
        prefix = "GROQ" if groq else "AGENT"
        key = os.getenv(prefix + "_API_KEY", "")
        model = config.get("model") or os.getenv(prefix + "_MODEL")
        url = base.rstrip("/") + "/models"
        headers = runpy.run_path(str(ROOT / "src/assistant_mlops/auth.py"))["endpoint_headers"]
        request = Request(url, headers=headers(prefix, key))
        with urlopen(request, timeout=15) as response:
            if response.status != 200:
                return "infrastructure_failure"
            listed = json.loads(response.read()).get("data", [])
            if model and not any(item.get("id") == model for item in listed):
                return "infrastructure_failure"
        return "regression"
    except Exception:
        return "infrastructure_failure"


def infra_failure():
    raise AirflowFailException(
        "Model endpoint unavailable; evaluation not run. No promotion attempted."
    )


def regression():
    # Dedicated module: no paid judge and no mutable production configuration.
    subprocess.run(
        [str(ROOT / ".venv/bin/python"), "-m", "assistant_mlops.nightly"],
        cwd=ROOT,
        check=True,
        timeout=3600,
    )
    result = json.loads((ROOT / "reports/nightly/status.json").read_text())
    if result["degraded"]:
        raise AirflowFailException("Ground-truth regression failed; inspect reports/nightly")


with DAG(
    "assistant_nightly_regression",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "royas", "retries": 0},
    dagrun_timeout=timedelta(hours=2),
) as dag:
    health = BranchPythonOperator(task_id="endpoint_health", python_callable=health_branch)
    check = PythonOperator(task_id="regression", python_callable=regression)
    infra = PythonOperator(task_id="infrastructure_failure", python_callable=infra_failure)
    health >> [check, infra]
