import pytest

from assistant_mlops.harness import evaluate
from assistant_mlops.schemas import EvalCase


@pytest.mark.asyncio
async def test_missing_token_split_never_produces_false_zero_cost(monkeypatch):
    monkeypatch.setenv("INPUT_USD_PER_MILLION", "1")
    monkeypatch.setenv("OUTPUT_USD_PER_MILLION", "2")

    class TotalOnlyProviderFixture:
        async def run(self, question, failure=None):
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
        id="cost",
        category="unanswerable",
        question="Unknown?",
        expected_status="abstain",
        reference="Unknown",
        max_steps=1,
    )
    rows, metrics = await evaluate(TotalOnlyProviderFixture(), [case], repeats=1)
    assert rows[0]["tokens"] == 10
    assert rows[0]["estimated_cost_usd"] is None
    assert metrics["cost_usage_coverage"] == 0
    assert "estimated_cost_usd_mean" not in metrics
