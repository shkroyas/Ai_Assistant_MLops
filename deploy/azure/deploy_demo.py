"""Deploy separate HTTPS demos with a scoped, scheduled resource-group cleanup job.

Azure CLI is external tooling. Credentials are read from its configured login and
ignored .env; none are embedded in this source or passed as CLI secret arguments.
"""

import argparse
import json
import os
import re
import secrets
import subprocess
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml
from dotenv import dotenv_values


class DeploymentError(RuntimeError):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--az", default="az")
    parser.add_argument("--subscription", required=True)
    parser.add_argument("--location", default="centralindia")
    parser.add_argument("--private-dir", type=Path, required=True)
    parser.add_argument("--hours", type=int, default=4, choices=[4])
    parser.add_argument("--budget", type=float, default=5.0)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()
    private = args.private_dir.resolve()
    private.mkdir(parents=True, exist_ok=True)
    private.chmod(0o700)
    state_file = private / "deployment.json"
    env = dict(os.environ, AWS_EC2_METADATA_DISABLED="true", AZURE_CORE_COLLECT_TELEMETRY="false")
    docker_config = private / "docker"
    docker_config.mkdir(exist_ok=True)
    docker_config.chmod(0o700)
    os.environ["DOCKER_CONFIG"] = str(docker_config)
    sensitive = [
        value
        for key, value in dotenv_values(args.env_file).items()
        if value and any(part in key for part in ["KEY", "TOKEN", "COOKIE", "PASSWORD"])
    ]

    def save(state):
        state_file.write_text(json.dumps(state, indent=2) + "\n")
        state_file.chmod(0o600)

    def az(*arguments, none=False):
        command = [
            args.az,
            *map(str, arguments),
            "--only-show-errors",
            "--output",
            "none" if none else "json",
        ]
        (private / "last-operation.txt").write_text(" ".join(map(str, arguments[:4])))
        for retry in range(3):
            result = subprocess.run(command, env=env, capture_output=True, text=True)
            transient = any(
                code in result.stderr
                for code in [
                    "InternalServerError",
                    "ServiceUnavailable",
                    "GatewayTimeout",
                    "TooManyRequests",
                    "Precondition Failed",
                ]
            )
            if result.returncode == 0 or not transient or retry == 2:
                break
            time.sleep(5 * (retry + 1))
        if result.returncode:
            # SDK errors may repeat YAML contents. Report only a bounded, redacted code.
            message = result.stderr
            for value in sensitive:
                message = message.replace(value, "[redacted]")
            match = re.search(r"ERROR:\s*\(([^)]+)\)", message)
            code = match.group(1) if match else "AzureCommandFailed"
            (private / "error-operation.txt").write_text(" ".join(map(str, arguments[:4])))
            (private / "last-error.txt").write_text(message)
            (private / "last-error.txt").chmod(0o600)
            raise DeploymentError(code)
        return None if none or not result.stdout.strip() else json.loads(result.stdout)

    az("account", "set", "--subscription", args.subscription, none=True)
    if args.cleanup:
        state = json.loads(state_file.read_text())
        group = az("group", "show", "--name", state["resource_group"])
        if group.get("tags", {}).get("demo_run") != state["run"]:
            raise DeploymentError("Resource group ownership tag does not match")
        az("group", "delete", "--name", state["resource_group"], "--yes", none=True)
        print("Owned demo resource group deleted.")
        return
    if state_file.exists():
        raise DeploymentError(
            "State already exists; inspect it before starting another billable deployment"
        )
    # Conservative four-hour active estimate, no free grants assumed. Retail rates
    # must be refreshed in the handoff before launching in another region/date.
    estimate = 3 * 14400 * 0.000024 + 6 * 14400 * 0.000003 + 0.1666 + 0.50 + 4 * 0.14
    if args.budget > 5 or estimate > args.budget:
        raise DeploymentError("Configured plan exceeds the authorized demo budget")
    run = datetime.now(UTC).strftime("%Y%m%d") + "-" + secrets.token_hex(3)
    expiry = (datetime.now(UTC) + timedelta(hours=args.hours)).replace(second=0, microsecond=0)
    group_name = "rg-w17-demo-" + run
    state = {
        "run": run,
        "resource_group": group_name,
        "location": args.location,
        "expires_utc": expiry.isoformat(),
        "budget_usd": args.budget,
        "estimated_active_usd_with_margin": round(estimate, 2),
        "phase": "starting",
    }
    save(state)
    group_created = False
    try:
        group = az(
            "group",
            "create",
            "--name",
            group_name,
            "--location",
            args.location,
            "--tags",
            "purpose=week17-demo",
            "demo_run=" + run,
            "expires_utc=" + expiry.isoformat(),
        )
        group_created = True
        print(
            "Created isolated demo resource group; preparing cloud-side cleanup first.", flush=True
        )
        identity = az(
            "identity", "create", "--name", "demo-cleanup", "--resource-group", group_name
        )
        az(
            "role",
            "assignment",
            "create",
            "--assignee-object-id",
            identity["principalId"],
            "--assignee-principal-type",
            "ServicePrincipal",
            "--role",
            "Contributor",
            "--scope",
            group["id"],
            none=True,
        )
        environment = az(
            "containerapp",
            "env",
            "create",
            "--name",
            "demo-environment",
            "--resource-group",
            group_name,
            "--location",
            args.location,
            "--logs-destination",
            "none",
            "--environment-mode",
            "WorkloadProfiles",
        )
        profiles = environment.get("properties", {}).get("workloadProfiles", [])
        if any(p.get("workloadProfileType") != "Consumption" for p in profiles):
            raise DeploymentError("An unexpected paid workload profile was provisioned")
        state["environment_profiles"] = profiles
        save(state)
        cleanup_command = (
            'set -eu; az login --identity --client-id "$MI_CLIENT_ID" --output none; '
            'az account set --subscription "$SUBSCRIPTION_ID"; '
            'az group show --name "$DEMO_RESOURCE_GROUP" --query name --output none; '
            'if [ "$(date +%s)" -ge "$EXPIRES_UNIX" ]; then '
            'az group delete --name "$DEMO_RESOURCE_GROUP" --yes --no-wait; '
            'else echo "Cleanup permission check succeeded; deadline not reached."; fi'
        )
        job = {
            "location": args.location,
            "identity": {"type": "UserAssigned", "userAssignedIdentities": {identity["id"]: {}}},
            "properties": {
                "environmentId": environment["id"],
                "workloadProfileName": "Consumption",
                "configuration": {
                    "triggerType": "Schedule",
                    "replicaTimeout": 300,
                    "replicaRetryLimit": 2,
                    "scheduleTriggerConfig": {
                        "cronExpression": f"{expiry.minute} {expiry.hour} {expiry.day} {expiry.month} *",
                        "parallelism": 1,
                        "replicaCompletionCount": 1,
                    },
                },
                "template": {
                    "containers": [
                        {
                            "name": "cleanup",
                            "image": "mcr.microsoft.com/azure-cli:2.90.0",
                            "command": ["/bin/sh", "-c"],
                            "args": [cleanup_command],
                            "resources": {"cpu": 0.25, "memory": "0.5Gi"},
                            "env": [
                                {"name": k, "value": str(v)}
                                for k, v in {
                                    "MI_CLIENT_ID": identity["clientId"],
                                    "SUBSCRIPTION_ID": args.subscription,
                                    "DEMO_RESOURCE_GROUP": group_name,
                                    "EXPIRES_UNIX": int(expiry.timestamp()),
                                }.items()
                            ],
                        }
                    ]
                },
            },
        }
        job_file = private / "cleanup-job.yaml"
        job_file.write_text(yaml.safe_dump(job))
        job_file.chmod(0o600)
        job_uri = group["id"] + "/providers/Microsoft.App/jobs/four-hour-cleanup"
        job_json = private / "cleanup-job.json"
        job_json.write_text(json.dumps(job))
        job_json.chmod(0o600)
        az(
            "rest",
            "--method",
            "put",
            "--url",
            job_uri + "?api-version=2025-07-01",
            "--body",
            "@" + str(job_json),
            none=True,
        )
        for _ in range(180):
            job_state = az("rest", "--method", "get", "--url", job_uri + "?api-version=2025-07-01")
            (private / "cleanup-provisioning.json").write_text(json.dumps(job_state))
            (private / "cleanup-provisioning.json").chmod(0o600)
            provisioned = job_state.get("properties", {}).get("provisioningState")
            if provisioned == "Succeeded":
                break
            if provisioned in {"Failed", "Canceled"}:
                raise DeploymentError("Cleanup job provisioning failed")
            time.sleep(3)
        else:
            raise DeploymentError("Cleanup job provisioning timed out")
        previous = az(
            "rest",
            "--method",
            "get",
            "--url",
            job_uri + "/executions?api-version=2025-07-01",
        )
        previous_names = {r["name"] for r in previous.get("value", [])}
        execution = az(
            "rest",
            "--method",
            "post",
            "--url",
            job_uri + "/start?api-version=2025-07-01",
        )
        execution_name = (execution or {}).get("name")
        for _ in range(90):
            response = az(
                "rest",
                "--method",
                "get",
                "--url",
                job_uri + "/executions?api-version=2025-07-01",
            )
            runs = response.get("value", [])
            # Start may return 202 with no body. The newly created execution is
            # unambiguous because this fresh job has no concurrent scheduled run.
            if execution_name is None:
                created = [r for r in runs if r["name"] not in previous_names]
                if len(created) == 1:
                    execution_name = created[0]["name"]
            current = next((r for r in runs if r["name"] == execution_name), {})
            status = current.get("properties", {}).get("status")
            if status == "Succeeded":
                break
            if status in {"Failed", "Stopped"}:
                raise DeploymentError("Cloud cleanup preflight failed")
            time.sleep(5)
        else:
            raise DeploymentError("Cloud cleanup preflight timed out")
        if datetime.now(UTC) >= expiry - timedelta(minutes=15):
            raise DeploymentError("Insufficient time remains before the cleanup deadline")
        state["cleanup_preflight"] = "Succeeded"
        save(state)
        print(
            "Cloud-side four-hour cleanup preflight passed. Creating the small registry.",
            flush=True,
        )
        registry_name = "w17demo" + run.replace("-", "")
        registry = az(
            "acr",
            "create",
            "--name",
            registry_name,
            "--resource-group",
            group_name,
            "--sku",
            "Basic",
            "--admin-enabled",
            "true",
        )
        registry_credentials = az("acr", "credential", "show", "--name", registry_name)
        registry_password = registry_credentials["passwords"][0]["value"]
        sensitive.append(registry_password)
        login = subprocess.run(
            [
                "docker",
                "login",
                registry["loginServer"],
                "--username",
                registry_credentials["username"],
                "--password-stdin",
            ],
            input=registry_password,
            text=True,
            capture_output=True,
        )
        if login.returncode:
            raise DeploymentError("Docker registry login failed")
        state["registry"] = registry_name
        password = secrets.token_urlsafe(24)
        (private / "demo-access.json").write_text(
            json.dumps({"username": "royas", "password": password})
        )
        (private / "demo-access.json").chmod(0o600)
        sensitive.append(password)
        values = dotenv_values(args.env_file)
        apps = {}
        for task, cpu, memory in [("a", 1, "2Gi"), ("b", 2, "4Gi")]:
            image = registry["loginServer"] + f"/task-{task}:" + run
            subprocess.run(["docker", "tag", f"w17-task-{task}-azure:demo", image], check=True)
            push = subprocess.run(["docker", "push", image], capture_output=True, text=True)
            if push.returncode:
                raise DeploymentError("Docker image upload failed")
            secret_rows = [
                {"name": "registry-password", "value": registry_password},
                {"name": "demo-password", "value": password},
            ]
            app_env = [
                {"name": "DEMO_PASSWORD", "secretRef": "demo-password"},
                {"name": "DEMO_TASK", "value": task.upper()},
            ]
            if task == "b":
                for key in [
                    "AGENT_BASE_URL",
                    "AGENT_MODEL",
                    "AGENT_API_KEY",
                    "AGENT_PROXY_TOKEN",
                    "AGENT_PROXY_COOKIE",
                    "GROQ_API_KEY",
                    "GROQ_MODEL",
                ]:
                    value = values.get(key)
                    if not value:
                        continue
                    name = key.lower().replace("_", "-")
                    secret_rows.append({"name": name, "value": value})
                    app_env.append({"name": key, "secretRef": name})
                app_env.extend(
                    [
                        {"name": "ASSISTANT_CONFIG", "value": ""},
                        {"name": "EVIDENTLY_DISABLE_TELEMETRY", "value": "1"},
                    ]
                )
            app = {
                "location": args.location,
                "properties": {
                    "managedEnvironmentId": environment["id"],
                    "workloadProfileName": "Consumption",
                    "configuration": {
                        "activeRevisionsMode": "Single",
                        "secrets": secret_rows,
                        "registries": [
                            {
                                "server": registry["loginServer"],
                                "username": registry_credentials["username"],
                                "passwordSecretRef": "registry-password",
                            }
                        ],
                        "ingress": {
                            "external": True,
                            "targetPort": 8080,
                            "transport": "auto",
                            "allowInsecure": False,
                        },
                    },
                    "template": {
                        "containers": [
                            {
                                "name": "demo",
                                "image": image,
                                "resources": {"cpu": cpu, "memory": memory},
                                "env": app_env,
                                "probes": [
                                    {
                                        "type": "Startup",
                                        "httpGet": {"path": "/healthz", "port": 8080},
                                        "periodSeconds": 3,
                                        "failureThreshold": 240,
                                    },
                                    {
                                        "type": "Readiness",
                                        "httpGet": {"path": "/healthz", "port": 8080},
                                        "periodSeconds": 10,
                                    },
                                ],
                            }
                        ],
                        "scale": {"minReplicas": 1, "maxReplicas": 1},
                    },
                },
            }
            app_file = private / f"task-{task}.yaml"
            app_file.write_text(yaml.safe_dump(app))
            app_file.chmod(0o600)
            result = az(
                "containerapp",
                "create",
                "--name",
                f"task-{task}",
                "--resource-group",
                group_name,
                "--yaml",
                app_file,
            )
            apps[task] = "https://" + result["properties"]["configuration"]["ingress"]["fqdn"]
            state["apps"] = apps
            save(state)
            print(f"Task {task.upper()} provisioned: {apps[task]}", flush=True)
        subprocess.run(["docker", "logout", registry["loginServer"]], capture_output=True)
        state["phase"] = "provisioned"
        save(state)
        print(
            "Provisioned; verify real HTTPS requests before claiming deployment success.",
            flush=True,
        )
    except BaseException:
        state["phase"] = "failed"
        save(state)
        if group_created:
            print(
                "Deployment failed; deleting only this run's isolated resource group.", flush=True
            )
            try:
                az("group", "delete", "--name", group_name, "--yes", none=True)
                state["failure_cleanup"] = "deleted"
                save(state)
            except DeploymentError:
                print(
                    "Cleanup requires follow-up; isolated group is recorded in private state.",
                    flush=True,
                )
        raise


if __name__ == "__main__":
    try:
        main()
    except DeploymentError as exc:
        print("Deployment error:", exc)
        raise SystemExit(1) from None
