"""Nightly ground-truth regression; infrastructure failures have a separate branch."""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.python import BranchPythonOperator, PythonOperator

ROOT = Path(os.getenv("PROJECT_DIR", "/opt/project"))


def health_branch():
    url = os.getenv("AGENT_BASE_URL", "").rstrip("/") + "/models"
    try:
        request = Request(
            url, headers={"Authorization": "Bearer " + os.getenv("AGENT_API_KEY", "")}
        )
        with urlopen(request, timeout=15) as response:
            if response.status != 200:
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
