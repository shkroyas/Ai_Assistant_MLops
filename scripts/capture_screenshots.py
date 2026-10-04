"""Capture actual local services; install Playwright in a separate tooling environment."""

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ui-url", default="http://localhost:18501")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--mlflow-url", default="http://localhost:5000")
    parser.add_argument("--airflow-url", default="http://localhost:8080")
    parser.add_argument("--healthy-run")
    parser.add_argument("--infra-run")
    parser.add_argument("--version")
    args = parser.parse_args()
    directory = Path("reports/screenshots")
    directory.mkdir(parents=True, exist_ok=True)
    with urlopen(args.api_url + "/health", timeout=15) as response:
        health = json.load(response)
    if args.healthy_run and health.get("configuration_version") != args.version:
        raise ValueError("Healthy-run screenshots require the matching API configuration")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]
        )
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.goto(args.ui_url)
        page.get_by_role("textbox", name="Your question").fill(
            "How many provider attempts and what retry strategy are allowed?"
        )
        page.get_by_role("textbox", name="Your question").press("Tab")
        expect(page.get_by_role("button", name="Verify answer")).to_be_enabled(timeout=30000)
        page.get_by_role("button", name="Verify answer").click()
        page.get_by_text("Status: answered", exact=False).wait_for(timeout=910000)
        page.locator("details").evaluate_all("items => items.forEach(item => item.open = true)")
        page.screenshot(path=str(directory / "assistant_answer.png"), full_page=True)
        page.goto(args.api_url + "/docs")
        page.get_by_text("/ask", exact=False).first.wait_for()
        page.screenshot(path=str(directory / "api_docs.png"), full_page=True)
        with urlopen(
            args.mlflow_url
            + "/api/2.0/mlflow/experiments/get-by-name?"
            + urlencode({"experiment_name": "assistant-configurations"}),
            timeout=10,
        ) as response:
            experiment_id = json.load(response)["experiment"]["experiment_id"]
        page.goto(args.mlflow_url + "/#/experiments/" + experiment_id)
        page.wait_for_timeout(5000)
        page.screenshot(path=str(directory / "mlflow_experiments.png"), full_page=True)
        if args.healthy_run and args.infra_run:
            # Keep the local Airflow admin password in memory; never log or screenshot it.
            password = subprocess.run(
                [
                    "docker",
                    "compose",
                    "exec",
                    "-T",
                    "airflow",
                    "cat",
                    "/opt/airflow/standalone_admin_password.txt",
                ],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            page.goto(args.airflow_url + "/login/")
            page.locator("#username").fill("admin")
            page.locator("#password").fill(password)
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_url("**/home**")
            for label, run_id in [("healthy", args.healthy_run), ("infra", args.infra_run)]:
                query = urlencode({"dag_run_id": run_id})
                page.goto(args.airflow_url + "/dags/assistant_nightly_regression/grid?" + query)
                page.wait_for_timeout(4000)
                page.screenshot(path=str(directory / f"airflow_{label}.png"), full_page=True)
        if args.version:
            page.goto(Path(f"reports/{args.version}/evidently_judge.html").resolve().as_uri())
            page.wait_for_timeout(3000)
            page.screenshot(path=str(directory / "evidently_judge.png"), full_page=True)
        browser.close()
    (directory / "manifest.json").write_text(
        json.dumps(
            {
                "captured_at_utc": datetime.now(UTC).isoformat(),
                "api_configuration_version": health.get("configuration_version"),
                "judge_report_version": args.version,
                "api_health": health,
                "healthy_run_id": args.healthy_run,
                "infra_run_id": args.infra_run,
                "files": {
                    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in directory.glob("*.png")
                },
            },
            indent=2,
        )
    )
    print("Saved actual service screenshots in reports/screenshots")


if __name__ == "__main__":
    main()
