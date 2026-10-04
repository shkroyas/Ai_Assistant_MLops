"""Billing safeguards: failed cleanup setup cannot launch paid application resources."""

import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest


@pytest.fixture
def deployment():
    path = Path(__file__).resolve().parents[1] / "deploy/azure/deploy_demo.py"
    spec = importlib.util.spec_from_file_location("demo_deployment", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failed_cleanup_setup_never_creates_registry_or_apps(deployment, monkeypatch, tmp_path):
    calls = []
    current = datetime(2026, 10, 4, 6, 48, 59, 500000, tzinfo=UTC)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return current

    monkeypatch.setattr(deployment, "datetime", Clock)
    monkeypatch.setattr(
        sys, "argv", ["demo", "--subscription", "fixture", "--private-dir", str(tmp_path)]
    )

    def command(args, **kwargs):
        calls.append(args)
        operation = args[1:3]
        result = {}
        if operation == ["group", "create"]:
            result = {"id": "/subscriptions/fixture/resourceGroups/owned-demo"}
        elif operation == ["identity", "create"]:
            result = {"id": "/identity", "principalId": "principal", "clientId": "client"}
        elif operation == ["containerapp", "env"]:
            result = {"id": "/environment", "properties": {"workloadProfiles": []}}
        elif args[1] == "rest":
            return subprocess.CompletedProcess(args, 1, "", "ERROR: (Denied) fixture refusal")
        return subprocess.CompletedProcess(args, 0, json.dumps(result), "")

    monkeypatch.setattr(deployment.subprocess, "run", command)
    with pytest.raises(deployment.DeploymentError, match="Denied"):
        deployment.main()
    assert not any(c[0] == "docker" or c[1] == "acr" for c in calls)
    assert not any(c[1:3] == ["containerapp", "create"] for c in calls)
    deletes = [c for c in calls if c[1:3] == ["group", "delete"]]
    state = json.loads((tmp_path / "deployment.json").read_text())
    assert len(deletes) == 1 and state["resource_group"] in deletes[0]
    assert state["failure_cleanup"] == "deleted"
    job = json.loads((tmp_path / "cleanup-job.json").read_text())
    values = {v["name"]: v["value"] for v in job["properties"]["template"]["containers"][0]["env"]}
    expiry = datetime.fromtimestamp(int(values["EXPIRES_UNIX"]), UTC)
    assert expiry == datetime(2026, 10, 4, 10, 48, tzinfo=UTC)
    assert 0 < (expiry - current).total_seconds() <= 4 * 3600
    assert job["properties"]["configuration"]["scheduleTriggerConfig"]["cronExpression"] == (
        "48 10 4 10 *"
    )


def test_manual_cleanup_rejects_another_runs_resource_group(deployment, monkeypatch, tmp_path):
    (tmp_path / "deployment.json").write_text(
        json.dumps({"resource_group": "owned-demo", "run": "expected-run"})
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["demo", "--subscription", "fixture", "--private-dir", str(tmp_path), "--cleanup"],
    )
    calls = []

    def command(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(
            args, 0, json.dumps({"tags": {"demo_run": "different-run"}}), ""
        )

    monkeypatch.setattr(deployment.subprocess, "run", command)
    with pytest.raises(deployment.DeploymentError, match="ownership tag"):
        deployment.main()
    assert not any(c[1:3] == ["group", "delete"] for c in calls)
