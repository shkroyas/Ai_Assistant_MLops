"""Refresh the owned demo's proxy secrets without extending its cleanup deadline."""

import argparse
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import httpx
import yaml
from dotenv import dotenv_values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-dir", required=True, type=Path)
    parser.add_argument("--env-file", default=Path(".env"), type=Path)
    parser.add_argument("--az", default="az")
    parser.add_argument("--subscription", required=True)
    args = parser.parse_args()
    state = json.loads((args.private_dir / "deployment.json").read_text())
    if datetime.now(UTC) >= datetime.fromisoformat(state["expires_utc"]):
        raise SystemExit("The demo deadline has passed; start a new authorized run")
    values = dotenv_values(args.env_file)
    token = values.get("AGENT_PROXY_TOKEN") or ""
    cookie = (values.get("AGENT_PROXY_COOKIE") or "").replace("\n", "").strip()
    if cookie.lower().startswith("cookie:"):
        cookie = cookie.split(":", 1)[1].strip()
    expected = yaml.safe_load(
        (Path(__file__).resolve().parents[2] / "configs/v34.yaml").read_text()
    )["model"]
    if values.get("AGENT_MODEL") != expected:
        raise SystemExit("Model differs from the approved v34 configuration; no changes made")
    headers = {"Authorization": "token " + token}
    if cookie:
        headers["Cookie"] = cookie
    with httpx.Client(timeout=30) as client:
        response = client.get(values["AGENT_BASE_URL"].rstrip("/") + "/models", headers=headers)
        if response.status_code != 200:
            raise SystemExit(
                f"Proxy preflight returned HTTP {response.status_code}; no changes made"
            )
        if not any(m["id"] == values["AGENT_MODEL"] for m in response.json().get("data", [])):
            raise SystemExit("Configured model is not available; no changes made")

    def az(*parts):
        command = [
            args.az,
            *map(str, parts),
            "--subscription",
            args.subscription,
            "--only-show-errors",
            "-o",
            "json",
        ]
        result = subprocess.run(command, env=os.environ.copy(), capture_output=True, text=True)
        if result.returncode:
            # Azure errors may echo secret YAML. Keep only redacted diagnostics private.
            message = result.stderr
            known = [v for v in values.values() if v and len(v) > 7]
            original = yaml.safe_load((args.private_dir / "task-b.yaml").read_text())
            known += [s["value"] for s in original["properties"]["configuration"]["secrets"]]
            for value in known:
                message = message.replace(value, "[redacted]")
            error_file = args.private_dir / "refresh-error.txt"
            error_file.write_text("Operation: " + " ".join(map(str, parts[:3])) + "\n" + message)
            error_file.chmod(0o600)
            raise SystemExit("Azure update failed; redacted diagnostics saved privately")
        return json.loads(result.stdout) if result.stdout.strip() else {}

    group = az("group", "show", "--name", state["resource_group"])
    if group.get("tags", {}).get("demo_run") != state["run"]:
        raise SystemExit("Resource-group ownership does not match; no changes made")
    path = args.private_dir / "task-b.yaml"
    app = yaml.safe_load(path.read_text())
    secrets = app["properties"]["configuration"]["secrets"]
    rows = app["properties"]["template"]["containers"][0]["env"]
    for key in [
        "AGENT_BASE_URL",
        "AGENT_MODEL",
        "AGENT_API_KEY",
        "AGENT_PROXY_TOKEN",
        "AGENT_PROXY_COOKIE",
    ]:
        value = values.get(key)
        if value is None:
            continue
        name = key.lower().replace("_", "-")
        row = next((s for s in secrets if s["name"] == name), None)
        if row is None:
            secrets.append({"name": name, "value": value})
            rows.append({"name": key, "secretRef": name})
        else:
            row["value"] = value
    path.write_text(yaml.safe_dump(app))
    path.chmod(0o600)
    az(
        "containerapp",
        "update",
        "--name",
        "task-b",
        "--resource-group",
        state["resource_group"],
        "--yaml",
        path,
    )
    current = az(
        "containerapp", "show", "--name", "task-b", "--resource-group", state["resource_group"]
    )
    az(
        "containerapp",
        "revision",
        "restart",
        "--name",
        "task-b",
        "--resource-group",
        state["resource_group"],
        "--revision",
        current["properties"]["latestRevisionName"],
    )
    print("Task B proxy credentials refreshed and revision restarted; cleanup deadline unchanged")


if __name__ == "__main__":
    main()
