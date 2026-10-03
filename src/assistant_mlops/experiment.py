import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path

import mlflow
import pandas as pd
import yaml
from dotenv import load_dotenv

from assistant_mlops.agent import Agent
from assistant_mlops.gate import gate
from assistant_mlops.harness import evaluate, load_cases, write_report
from assistant_mlops.provider import provider_for_config
from assistant_mlops.regression import calibrate, deterministic_report, judge
from assistant_mlops.retrieval import Corpus


async def run(config_path, with_judge=False, diagnosis=None):
    load_dotenv()
    config = yaml.safe_load(Path(config_path).read_text())
    if with_judge and not (os.getenv("GEMINI_API_KEY") or os.getenv("JUDGE_API_KEY")):
        raise RuntimeError("Configure the judge key before starting paid agent evaluations")
    if config["version"] != "v1" and not diagnosis:
        raise ValueError(
            "Revisions require --diagnosis pointing to a real previous failure diagnosis"
        )
    if diagnosis:
        evidence = json.loads(Path(diagnosis).read_text())
        trace_path = Path(evidence["trace_path"])
        previous = "v" + str(int(config["version"][1:]) - 1)
        if "/dev/" not in trace_path.as_posix():
            raise ValueError("Diagnosis must use development traces, never golden cases")
        if trace_path.exists():
            trace = json.loads(trace_path.read_text())
            if trace.get("prompt_version") != previous:
                raise ValueError("Diagnosis must cite the immediately preceding version")
        if (
            config["version"] in {"v2", "v3"}
            and str(trace_path) not in Path(config["prompt"]).read_text()
        ):
            raise ValueError("Prompt header must cite the actual motivating development trace")
        if not trace_path.is_file() or not evidence.get("change") or not evidence.get("failure"):
            raise ValueError("Diagnosis must cite an existing trace, failure, and one changed axis")
    mlflow.set_tracking_uri((os.getenv("MLFLOW_TRACKING_URI") or "sqlite:///mlflow.db"))
    mlflow.set_experiment("assistant-configurations")
    provider = provider_for_config(config)
    if not provider.configured:
        await provider.close()
        raise RuntimeError("Configure credentials for the selected agent provider")
    # Prompt comparisons must not silently switch models when the GPU fails.
    provider.fallback_url = None
    corpus = Corpus()
    agent = Agent(corpus, provider, config)
    directory = Path("reports") / config["version"]
    try:
        with mlflow.start_run(run_name=config["version"]) as active:
            mlflow.set_tag("execution_type", "live_provider")
            mlflow.log_params(
                {
                    **config,
                    "model": provider.model,
                    "provider_fallback_enabled": False,
                    "evaluation_concurrency": 4,
                    "judge_provider": os.getenv("JUDGE_PROVIDER", "gemini")
                    if with_judge
                    else "none",
                    "judge_model": os.getenv("JUDGE_MODEL", "gemini-2.5-flash")
                    if with_judge
                    else "none",
                    "corpus_sha256": corpus.fingerprint,
                    "prompt_sha256": hashlib.sha256(agent.prompt.encode()).hexdigest(),
                }
            )
            dev_rows, metrics = await evaluate(
                agent,
                load_cases("datasets/dev_v1.jsonl"),
                config["repeats"],
                directory=directory / "dev",
                concurrency=4,
            )
            write_report(dev_rows, metrics, directory / "dev")
            gold_rows, gold_metrics = await evaluate(
                agent,
                load_cases("datasets/golden_v1.jsonl"),
                config["repeats"],
                directory=directory / "golden",
                concurrency=4,
            )
            write_report(gold_rows, gold_metrics, directory / "golden")
            metrics["pct_ground_truth_passed"] = deterministic_report(gold_rows, directory)
            metrics["pct_tests_passed"] = metrics["pct_ground_truth_passed"]
            if with_judge:
                scored = await asyncio.to_thread(
                    judge,
                    pd.DataFrame([{k: v for k, v in r.items() if k != "trace"} for r in gold_rows]),
                    directory,
                )
                metrics["pct_judge_passed"] = float(scored.judge_pass.mean())
                metrics["pct_tests_passed"] = float((scored.judge_pass & scored.completed).mean())
                metrics["judge_truth_agreement"] = float(
                    (scored.judge_pass == scored.completed).mean()
                )
                calibration = await asyncio.to_thread(calibrate)
                metrics.update({k: v for k, v in calibration.items() if isinstance(v, float)})
                mlflow.log_artifacts("reports/judge_calibration", "judge_calibration")
            # Native nested MLflow spans in addition to complete raw JSON artifacts.
            for row in dev_rows[:3] + [r for r in dev_rows if not r["completed"]][:1]:
                with mlflow.start_span(name="agent_query") as root:
                    root.set_inputs({"question": row["query"]})
                    for step in row["trace"]["steps"]:
                        with mlflow.start_span(name=step["event"]) as child:
                            child.set_inputs(step.get("args") or {"step": step["step"]})
                            child.set_outputs(step.get("result") or step.get("reasoning"))
                    root.set_outputs(row["trace"]["answer"])
            production_file = Path("configs/production.yaml")
            production = yaml.safe_load(production_file.read_text())
            baseline = None
            if production.get("run_id"):
                baseline = mlflow.get_run(production["run_id"]).data.metrics
            result = gate(metrics, baseline)
            result.update({"run_id": active.info.run_id, "version": config["version"]})
            (directory / "gate.json").write_text(json.dumps(result, indent=2))
            (directory / "metrics.json").write_text(json.dumps(metrics, indent=2))
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(config["prompt"], "prompt")
            if diagnosis:
                mlflow.log_artifact(diagnosis, "diagnosis")
            mlflow.log_artifacts(str(directory), config["version"])
            mlflow.set_tag("gate", result["verdict"])
            # Scheduled evaluations never mutate production; promotion is an explicit command.
            return result
    finally:
        await provider.close()
        corpus.client.close()


def compare():
    load_dotenv()
    mlflow.set_tracking_uri((os.getenv("MLFLOW_TRACKING_URI") or "sqlite:///mlflow.db"))
    runs = mlflow.search_runs(experiment_names=["assistant-configurations"])
    columns = [
        c for c in runs if c == "run_id" or c.startswith(("params.", "metrics.", "tags.gate"))
    ]
    table = runs[columns]
    table.to_csv("reports/mlflow_comparison.csv", index=False)
    # Avoid requiring a separate Markdown-table dependency.
    Path("reports/mlflow_comparison.md").write_text(
        "| "
        + " | ".join(columns)
        + " |\n|"
        + "|".join(["---"] * len(columns))
        + "|\n"
        + "\n".join(
            "| " + " | ".join(str(v) for v in row) + " |"
            for row in table.itertuples(index=False, name=None)
        )
        + "\n"
    )


def promote(run_id):
    load_dotenv()
    mlflow.set_tracking_uri((os.getenv("MLFLOW_TRACKING_URI") or "sqlite:///mlflow.db"))
    run = mlflow.get_run(run_id)
    existing = yaml.safe_load(Path("configs/production.yaml").read_text())
    baseline = mlflow.get_run(existing["run_id"]).data.metrics if existing.get("run_id") else None
    verdict = gate(run.data.metrics, baseline)
    if verdict["verdict"] != "PROMOTE":
        raise RuntimeError("Gate rejected this run: " + json.dumps(verdict["checks"]))
    version = run.data.params["version"]
    Path("configs/production.yaml").write_text(
        yaml.safe_dump({"version": version, "run_id": run_id})
    )
    mlflow.MlflowClient().set_tag(run_id, "stage", "production")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run", "compare", "judge-check", "promote"])
    parser.add_argument("--config", default="configs/v1.yaml")
    parser.add_argument("--judge", action="store_true")
    parser.add_argument("--diagnosis")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    if args.command == "run":
        print(json.dumps(asyncio.run(run(args.config, args.judge, args.diagnosis)), indent=2))
    elif args.command == "judge-check":
        load_dotenv()
        print(json.dumps(calibrate(), indent=2))
    elif args.command == "promote":
        if not args.run_id:
            parser.error("--run-id required")
        promote(args.run_id)
    else:
        compare()
