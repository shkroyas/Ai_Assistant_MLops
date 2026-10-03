import json
from pathlib import Path

import pytest
import yaml

from assistant_mlops.agent import Agent
from assistant_mlops.gate import gate
from assistant_mlops.harness import assess, load_cases
from assistant_mlops.retrieval import Corpus
from assistant_mlops.schemas import EvalCase


class ScriptedProvider:
    """Protocol fixture only. Its results must never be represented as LLM quality evidence."""

    def __init__(self, messages):
        self.messages = iter(messages)

    async def complete(self, *args):
        return next(self.messages), {
            "total_tokens": 10,
            "prompt_tokens": 7,
            "completion_tokens": 3,
            "model": "fixture",
            "fallback": False,
        }


def call(name, args):
    return {
        "content": None,
        "tool_calls": [
            {
                "id": "call-1",
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(args)},
            }
        ],
    }


def final(status, answer, sources=None):
    return {"content": json.dumps({"status": status, "answer": answer, "sources": sources or []})}


@pytest.fixture
def corpus():
    value = Corpus()
    yield value
    value.client.close()


@pytest.mark.asyncio
async def test_cross_source_loop_and_usage(corpus):
    messages = [
        call(
            "search",
            {
                "query": "drift triggers challenger",
                "source_id": "drift-runbook",
                "reason": "Check drift action",
            },
        ),
        call("read_source", {"source_id": "release-policy", "reason": "Check promotion gate"}),
        final(
            "answered",
            "Drift triggers challenger evaluation. F1 must improve by 0.005.",
            [
                {
                    "source_id": "drift-runbook",
                    "quote": "Drift triggers challenger training and evaluation",
                },
                {"source_id": "release-policy", "quote": "F1 improves by at least 0.005"},
            ],
        ),
    ]
    config = yaml.safe_load(Path("configs/v1.yaml").read_text())
    trace = await Agent(corpus, ScriptedProvider(messages), config).run("What happens after drift?")
    assert trace["answer"]["status"] == "answered"
    assert trace["iterations"] == 3 and trace["tokens"] == 30
    assert trace["steps"][0]["reasoning"] == "Check drift action"
    assert trace["steps"][0]["args"]["reason"] == "Check drift action"


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["timeout", "malformed", "unavailable"])
async def test_failure_injection_recognized(corpus, failure):
    messages = [
        call("search", {"query": "retry limit", "reason": "Find policy"}),
        final("abstain", "Tool failed; cannot verify evidence."),
    ]
    config = yaml.safe_load(Path("configs/v1.yaml").read_text())
    trace = await Agent(corpus, ScriptedProvider(messages), config).run("Retry?", failure)
    assert trace["answer"]["status"] == "abstain"
    assert trace["tool_errors"] == 1
    assert trace["steps"][0]["result"]["evidence_valid"] is False


@pytest.mark.asyncio
async def test_unretrieved_citation_rejected(corpus):
    fake = final("answered", "F1 gate.", [{"source_id": "release-policy", "quote": "F1"}])
    config = yaml.safe_load(Path("configs/v1.yaml").read_text())
    config["max_iterations"] = 1
    trace = await Agent(corpus, ScriptedProvider([fake]), config).run("Promotion?")
    assert trace["answer"]["status"] == "abstain"
    assert trace["termination"] == "max_iterations"


@pytest.mark.asyncio
async def test_invalid_tool_and_step_limit(corpus):
    config = yaml.safe_load(Path("configs/v1.yaml").read_text())
    config["max_iterations"] = 2
    message = call("delete_all", {"reason": "Invalid operation"})
    trace = await Agent(corpus, ScriptedProvider([message, message]), config).run("Delete?")
    assert trace["iterations"] == 2 and trace["tool_errors"] == 2
    assert all(not s["valid"] for s in trace["steps"])


def test_datasets_and_harness():
    assert len(load_cases("datasets/dev_v1.jsonl")) == 35
    assert len(load_cases("datasets/golden_v1.jsonl")) == 18
    assert len({r.category for r in load_cases("datasets/dev_v1.jsonl")}) == 7
    case = EvalCase(
        id="x",
        category="failure-injection",
        question="x",
        expected_status="abstain",
        reference="Cannot verify",
        max_steps=2,
        failure="timeout",
    )
    trace = {
        "answer": {"status": "answered", "answer": "Wrong", "sources": []},
        "steps": [],
        "termination": "answered",
        "iterations": 1,
        "tool_errors": 2,
        "tokens": 1,
        "usage_complete": True,
        "latency_seconds": 0.1,
    }
    assert assess(case, trace)["failure_class"] == "cascading_soft_failure"


def test_promotion_requires_real_judge():
    verdict = gate(
        {
            "pct_ground_truth_passed": 1.0,
            "tool_call_correctness": 1.0,
            "hard_failure_rate": 0,
            "failure_injection_safe": 1,
            "usage_complete": 1,
        }
    )
    assert verdict["verdict"] == "REJECT"
    assert not verdict["checks"]["judge"]


def test_retrieval_bounds_and_sources(corpus):
    hits = corpus.search("API keys", source_id="security")
    assert hits and {r["source_id"] for r in hits} == {"security"}
    with pytest.raises(ValueError):
        corpus.search("keys", top_k=100)
