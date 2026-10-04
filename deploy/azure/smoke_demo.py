"""Verify actual HTTPS demos without publishing private access or provider credentials."""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-dir", required=True, type=Path)
    parser.add_argument("--task-a-root", required=True, type=Path)
    parser.add_argument("--task-b-root", default=Path("."), type=Path)
    args = parser.parse_args()
    state = json.loads((args.private_dir / "deployment.json").read_text())
    access = json.loads((args.private_dir / "demo-access.json").read_text())
    assert state.get("cleanup_preflight") == "Succeeded", "Cleanup preflight must pass first"
    assert datetime.now(UTC) < datetime.fromisoformat(state["expires_utc"]), "Demo has expired"
    reports = {}
    for task, root in [("a", args.task_a_root), ("b", args.task_b_root)]:
        base = state["apps"][task]
        assert base.startswith("https://"), "HTTPS is required"
        report = {
            "checked_at": datetime.now(UTC).isoformat(),
            "scope": "Actual public Azure HTTPS deployment",
            "task": task.upper(),
            "base_url": base,
            "expires_utc": state["expires_utc"],
            "cleanup_preflight": state["cleanup_preflight"],
            "estimated_active_usd_with_margin": state["estimated_active_usd_with_margin"],
            "checks": [],
        }
        auth = (access["username"], access["password"])
        with httpx.Client(base_url=base, auth=auth, timeout=240) as client:
            routes = ["/", "/healthz", "/service/docs", "/service/openapi.json", "/tracking/"]
            if task == "b":
                routes.append("/assistant/")
            for path in routes:
                response = client.get(path)
                assert response.status_code == 200, f"Task {task}: {path} unavailable"
                row = {"path": path, "http_status": response.status_code}
                if path == "/healthz":
                    row["health"] = response.json()
                    if task == "b":
                        assert row["health"]["configuration_version"] == "v34"
                report["checks"].append(row)
            for path in ["/", "/service/docs", "/tracking/"]:
                response = httpx.get(base + path, timeout=30)
                assert response.status_code == 401, f"Task {task}: anonymous access allowed"
                report["checks"].append({"path": path, "anonymous_http_status": 401})
            if task == "a":
                payload = json.loads((root / "reports/deployment_smoke.json").read_text())[
                    "request"
                ]
                response = client.post("/service/predict", json=payload)
                assert response.status_code == 200
                prediction = response.json()
                assert 0 <= prediction["churn_probability"] <= 1 and prediction["model_version"]
                invalid = client.post("/service/predict", json={})
                assert invalid.status_code == 422
                report["prediction"] = prediction
                report["invalid_http_status"] = 422
            else:
                query = {
                    "question": "What retry strategy is allowed for transient provider errors?"
                }
                response = client.post("/service/ask", json=query)
                assert response.status_code == 200
                answer = response.json()
                assert answer["status"] == "answered" and answer["sources"], "No sourced answer"
                report["query"] = query
                report["answer"] = answer
                cached = client.post("/service/ask", json=query).json()
                assert cached["cache_hit"] and cached["tokens_consumed_this_request"] == 0
                report["cached_answer"] = cached
        report["status"] = "passed"
        directory = root / "reports/cloud_demo"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "azure_https_smoke.json").write_text(json.dumps(report, indent=2) + "\n")
        reports[task] = report
        print(f"Task {task.upper()}: actual HTTPS checks passed")
    (args.private_dir / "verified.json").write_text(json.dumps(reports, indent=2) + "\n")


if __name__ == "__main__":
    main()
