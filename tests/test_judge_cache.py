import json

import pytest
from evidently.legacy.options.base import Options
from evidently.llm.models import LLMMessage
from evidently.llm.utils.wrapper import LLMRequest, LLMResult, LiteLLMWrapper, RateLimits

from assistant_mlops.regression import GroqJudgeOptions, GroqJudgeWrapper


@pytest.mark.asyncio
async def test_native_judge_rotates_quota_failure_and_restores_key(monkeypatch, tmp_path):
    monkeypatch.setenv("JUDGE_API_KEYS", "first,second")
    monkeypatch.setenv("JUDGE_CACHE_PATH", str(tmp_path))
    monkeypatch.setenv("JUDGE_REQUEST_INTERVAL_SECONDS", "1")
    calls = []

    class Limited(Exception):
        status_code = 429

    async def complete(self, messages, seed=None):
        key = self.options.get_api_key()
        calls.append(key)
        if key == "first":
            raise Limited("Please try again in 1h2m3s")
        return LLMResult('{"passed": true}', 50, 10)

    monkeypatch.setattr(LiteLLMWrapper, "complete", complete)
    wrapper = GroqJudgeWrapper(
        "openai/gpt-oss-120b", Options.from_list([GroqJudgeOptions(api_key="first")])
    )
    result = await wrapper.complete([LLMMessage(role="user", content="question")])
    assert calls == ["first", "second"]
    assert result.input_tokens == 50 and result.output_tokens == 10
    assert wrapper.options.get_api_key() == "first"
    assert wrapper._judge_pool.used == [0, 60]
    import time

    assert wrapper._judge_pool.ready[0] - time.monotonic() > 3720


@pytest.mark.asyncio
async def test_native_judge_never_sends_reserve_keys_to_other_host(monkeypatch):
    monkeypatch.setenv("JUDGE_API_KEYS", "reserve")
    wrapper = GroqJudgeWrapper(
        "model",
        Options.from_list([GroqJudgeOptions(api_key="first", api_url="https://other.example/v1")]),
    )
    with pytest.raises(ValueError, match="official Groq"):
        await wrapper.complete([LLMMessage(role="user", content="question")])


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
