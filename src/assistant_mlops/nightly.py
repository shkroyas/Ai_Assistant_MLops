import asyncio
import json
import os
from pathlib import Path

import mlflow
import yaml
from dotenv import load_dotenv

from assistant_mlops.agent import Agent
from assistant_mlops.harness import evaluate, load_cases, write_report
from assistant_mlops.provider import provider_for_config
from assistant_mlops.regression import deterministic_report
from assistant_mlops.retrieval import Corpus


async def main():
    load_dotenv()
    mlflow.set_tracking_uri((os.getenv("MLFLOW_TRACKING_URI") or "sqlite:///mlflow.db"))
    production = yaml.safe_load(Path("configs/production.yaml").read_text())
    if not production.get("run_id"):
        raise RuntimeError("Nightly evaluation requires an established production run")
    baseline = mlflow.get_run(production["run_id"]).data.metrics
    config = yaml.safe_load(Path(f"configs/{production['version']}.yaml").read_text())
    provider, corpus = provider_for_config(config), Corpus()
    provider.fallback_url = None
    try:
        agent = Agent(corpus, provider, config)
        rows, metrics = await evaluate(agent, load_cases("datasets/golden_v1.jsonl"), repeats=1)
        write_report(rows, metrics, "reports/nightly")
        passed = deterministic_report(rows, "reports/nightly")
        threshold = max(0.85, baseline["pct_ground_truth_passed"] - 0.05)
        degraded = bool(
            passed < threshold
            or metrics["failure_injection_safe"] < 1
            or metrics["hard_failure_rate"] > 0.05
            or metrics["usage_complete"] < 1
        )
        mlflow.set_experiment("assistant-nightly")
        with mlflow.start_run(run_name="nightly"):
            mlflow.log_params(
                {
                    "production_run_id": production["run_id"],
                    "production_version": production["version"],
                    "model": provider.model,
                }
            )
            mlflow.log_metrics({**metrics, "pct_tests_passed": passed, "degraded": int(degraded)})
            Path("reports/nightly/status.json").write_text(
                json.dumps(
                    {
                        "degraded": degraded,
                        "pct_tests_passed": passed,
                        "threshold": threshold,
                        "production_run_id": production["run_id"],
                        "production_version": production["version"],
                        "model": provider.model,
                    },
                    indent=2,
                )
            )
            mlflow.log_artifacts("reports/nightly")
        return degraded
    finally:
        await provider.close()
        corpus.client.close()


if __name__ == "__main__":
    raise SystemExit(1 if asyncio.run(main()) else 0)
