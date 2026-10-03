from types import SimpleNamespace

import pytest

from assistant_mlops.harness import evaluate
from assistant_mlops.schemas import EvalCase


@pytest.mark.asyncio
async def test_checkpoint_resumes_completed_real_calls_and_rejects_changed_inputs(tmp_path):
    calls = []

    class Fixture:
        config = {"version": "fixture"}
        prompt = "fixture prompt"
        provider = SimpleNamespace(model="fixture", base_url="https://fixture.test")
        corpus = SimpleNamespace(fingerprint="original-corpus")

        async def run(self, question, failure=None):
            calls.append(question)
            return {
                "answer": {"status": "abstain", "answer": "Unknown", "sources": []},
                "steps": [],
                "termination": "abstain",
                "tool_errors": 0,
                "iterations": 1,
                "tokens": 10,
                "usage_complete": True,
                "latency_seconds": 0.1,
            }

    case = EvalCase(
        id="resume",
        category="unanswerable",
        question="Unknown?",
        expected_status="abstain",
        reference="Unknown",
        max_steps=1,
    )
    agent = Fixture()
    rows, metrics = await evaluate(agent, [case], repeats=3, directory=tmp_path, concurrency=3)
    assert len(calls) == 3 and len(rows) == 3
    resumed, resumed_metrics = await evaluate(agent, [case], repeats=3, directory=tmp_path)
    assert len(calls) == 3 and resumed == rows and resumed_metrics == metrics
    assert len(list(tmp_path.glob("trace_*.json"))) == 3
    agent.corpus.fingerprint = "changed-corpus"
    with pytest.raises(ValueError, match="Checkpoint inputs changed"):
        await evaluate(agent, [case], repeats=3, directory=tmp_path)
    agent.corpus.fingerprint = "original-corpus"
    agent.provider.model = "changed-model"
    with pytest.raises(ValueError, match="Checkpoint inputs changed"):
        await evaluate(agent, [case], repeats=3, directory=tmp_path)
