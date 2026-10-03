"""Capture actual local services; install Playwright in a separate tooling environment."""

import argparse
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ui-url", default="http://localhost:18501")
    parser.add_argument("--mlflow-url", default="http://localhost:5000")
    parser.add_argument("--airflow-url", default="http://localhost:8080")
    parser.add_argument("--healthy-run")
    parser.add_argument("--infra-run")
    args = parser.parse_args()
    directory = Path("reports/screenshots")
    directory.mkdir(parents=True, exist_ok=True)
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
        page.get_by_role("button", name="Verify answer").click()
        page.get_by_text("Status: answered", exact=False).wait_for(timeout=910000)
        page.screenshot(path=str(directory / "assistant_answer.png"), full_page=True)
        page.goto("http://localhost:8000/docs")
        page.get_by_text("/ask", exact=False).first.wait_for()
        page.screenshot(path=str(directory / "api_docs.png"), full_page=True)
        page.goto(args.mlflow_url)
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
            from urllib.parse import urlencode

            for label, run_id in [("healthy", args.healthy_run), ("infra", args.infra_run)]:
                query = urlencode({"dag_run_id": run_id})
                page.goto(args.airflow_url + "/dags/assistant_nightly_regression/grid?" + query)
                page.wait_for_timeout(4000)
                page.screenshot(path=str(directory / f"airflow_{label}.png"), full_page=True)
        browser.close()
    print("Saved actual service screenshots in reports/screenshots")


if __name__ == "__main__":
    main()
