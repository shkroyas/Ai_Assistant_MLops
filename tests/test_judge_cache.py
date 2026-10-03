import json

import pytest
from evidently.legacy.options.base import Options
from evidently.llm.models import LLMMessage
from evidently.llm.utils.wrapper import LLMRequest, LLMResult, LiteLLMWrapper, RateLimits

from assistant_mlops.regression import GroqJudgeOptions, GroqJudgeWrapper


@pytest.mark.asyncio
async def test_judge_reuses_identical_inputs_but_invalidates_changed_prompt(monkeypatch, tmp_path):
    monkeypatch.setenv("JUDGE_CACHE_PATH", str(tmp_path))
    calls = []

    async def complete(self, messages, seed=None):
        calls.append(messages)
        return LLMResult('{"passed": true}', 50, 10)

    monkeypatch.setattr(LiteLLMWrapper, "complete", complete)
    wrapper = GroqJudgeWrapper(
        "openai/gpt-oss-20b", Options.from_list([GroqJudgeOptions(api_key="fixture")])
    )

    def request(text):
        return LLMRequest(
            messages=[LLMMessage(role="user", content=text)],
            response_parser=json.loads,
            response_type=dict,
        )

    rows = await wrapper.run_batch([request("same"), request("same")], limits=RateLimits())
    assert rows == [{"passed": True}, {"passed": True}] and len(calls) == 1
    await wrapper.run_batch([request("same")], limits=RateLimits())
    assert len(calls) == 1
    await wrapper.run_batch([request("changed criteria")], limits=RateLimits())
    assert len(calls) == 2


def test_native_descriptor_sync_adapter_uses_cached_judgments(monkeypatch, tmp_path):
    import pandas as pd
    from assistant_mlops.regression import judge

    monkeypatch.setenv("JUDGE_CACHE_PATH", str(tmp_path / "cache"))
    monkeypatch.setenv("JUDGE_PROVIDER", "groq")
    monkeypatch.setenv("JUDGE_MODEL", "openai/gpt-oss-20b")
    monkeypatch.setenv("JUDGE_API_KEY", "fixture")
    monkeypatch.setenv("JUDGE_REQUEST_INTERVAL_SECONDS", "1")
    monkeypatch.setattr("assistant_mlops.regression.time.sleep", lambda _: None)
    calls = []

    async def complete(self, messages, seed=None):
        calls.append(messages)
        return LLMResult('{"category":"correct","reasoning":"fixture agreement"}', 50, 10)

    monkeypatch.setattr(LiteLLMWrapper, "complete", complete)
    frame = pd.DataFrame([{"query": "same", "reference": "yes", "response": "yes"}] * 2)
    scored = judge(frame, tmp_path / "first")
    assert scored.judge_pass.tolist() == [True, True] and len(calls) == 2
    judge(frame, tmp_path / "second")
    assert len(calls) == 2
