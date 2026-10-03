"""Separate implemented features from genuine live model/monitoring evidence."""

import argparse
import json
from pathlib import Path


def check(static=False):
    files = {
        "W15 single-pass baseline": "src/assistant_mlops/rag.py",
        "W15 LLM retries and fallback": "src/assistant_mlops/provider.py",
        "W15 RAG embeddings and vector database": "src/assistant_mlops/retrieval.py",
        "W15 structured output": "src/assistant_mlops/schemas.py",
        "W15 web UI": "src/assistant_mlops/ui.py",
        "W15 async batch, rate limiting, caching": "src/assistant_mlops/api.py",
        "W15 Dockerfile": "Dockerfile",
        "W15 Docker Compose": "compose.yaml",
        "W15 vLLM deployment": "serving/serve_vllm.sh",
        "W15 vLLM lockfile": "serving/uv.lock",
        "W16 model-directed bounded loop": "src/assistant_mlops/agent.py",
        "W16 scratch-built evaluation harness": "src/assistant_mlops/harness.py",
        "W16 failure-injection tests": "tests/test_agent.py",
        "W17 uv lockfile": "uv.lock",
        "W17 MLflow experiments": "src/assistant_mlops/experiment.py",
        "W17 native Evidently judge": "src/assistant_mlops/regression.py",
        "W17 regression promotion gate": "src/assistant_mlops/gate.py",
        "W17 Airflow DAG": "dags/assistant_regression.py",
        "Architecture and assignment write-up": "README.md",
    }
    checks = {
        name: Path(path).exists() and Path(path).stat().st_size > 0 for name, path in files.items()
    }
    if not static:
        role_path = Path("reports/provider_roles_smoke.json")
        roles = json.loads(role_path.read_text()) if role_path.exists() else {}
        baseline = roles.get("groq_baseline", {})
        checks["W15 live major-provider execution"] = (
            baseline.get("status") == "answered"
            and bool(baseline.get("sources"))
            and baseline.get("token_accounting") == "provider_usage"
            and baseline.get("tokens", 0) > 0
        )
        connection_path = Path("reports/provider_connection.json")
        connection = json.loads(connection_path.read_text()) if connection_path.exists() else {}
        checks["W15 GPU vLLM execution"] = (
            connection.get("status") == "passed"
            and connection.get("models_http_status") == 200
            and connection.get("model_listed") is True
            and bool(connection.get("native_tool_calls"))
            and connection.get("tool_usage", {}).get("total_tokens", 0) > 0
        )
        checks["W16 live harness results"] = Path("reports/v1/dev/harness.md").exists()
        versions = []
        for n in range(1, 5):
            filename = Path(f"reports/v{n}/metrics.json")
            if filename.exists():
                versions.append((f"v{n}", json.loads(filename.read_text())))
        checks["at least three actual prompt/config runs"] = len(versions) >= 3
        checks["judge, truth and total regression metrics per run"] = len(versions) >= 3 and all(
            {"pct_ground_truth_passed", "pct_judge_passed", "pct_tests_passed"} <= set(m)
            for _, m in versions
        )
        checks["native judge HTML per version"] = len(versions) >= 3 and all(
            Path(f"reports/{v}/evidently_judge.html").exists() for v, _ in versions
        )
        checks["full live trajectories"] = len(versions) >= 3 and all(
            len(list(Path(f"reports/{v}/dev").glob("trace_*.json"))) >= 3 for v, _ in versions
        )
        checks["judge calibration evidence"] = Path(
            "reports/judge_calibration/calibration.json"
        ).exists()
        checks["exported live MLflow comparison"] = Path("reports/mlflow_comparison.md").exists()
        checks["trace-driven revision diagnoses"] = all(
            Path(f"reports/diagnosis_v{n}.json").exists() for n in [2, 3]
        )
        checks["promoted production run"] = (
            "run_id: null" not in Path("configs/production.yaml").read_text()
        )
        checks["healthy and unavailable-endpoint Airflow evidence"] = all(
            Path(f"reports/airflow_{name}.txt").exists() for name in ["healthy", "infra"]
        )
    lines = ["| Requirement | Result |", "|---|---|"] + [
        f"| {name} | {'PASS' if value else 'PENDING'} |" for name, value in checks.items()
    ]
    lines.append(
        f"\n{sum(checks.values())}/{len(checks)} checks pass."
        + (" Static implementation only; no live model quality claim." if static else "")
    )
    print("\n".join(lines))
    if not static:
        Path("reports/deliverables.md").write_text("\n".join(lines) + "\n")
    return all(checks.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", action="store_true")
    raise SystemExit(0 if check(parser.parse_args().static) else 1)
