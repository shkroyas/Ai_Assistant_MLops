import httpx
import pytest

from assistant_mlops.provider import ChatProvider, ProviderError


@pytest.mark.parametrize(
    "body,expected",
    [
        (
            [
                {
                    "error": {
                        "message": "Please retry in 54m25.5s.",
                        "details": [{"retryDelay": "3265s"}],
                    }
                }
            ],
            3265.5,
        ),
        ({"error": {"message": "Please try again in 1h2m3s."}}, 3723),
    ],
)
def test_quota_cooldown_honors_full_structured_server_delay(body, expected):
    from assistant_mlops.provider import quota_cooldown

    assert quota_cooldown(httpx.Response(429, json=body)) == expected


@pytest.mark.asyncio
async def test_gemini_pool_is_scoped_and_globally_paced(monkeypatch):
    import asyncio
    import json

    from assistant_mlops.provider import provider_for_config

    monkeypatch.setenv("GEMINI_API_KEY", "gemini-active")
    monkeypatch.setenv("GEMINI_API_KEYS", "gemini-active,gemini-one,gemini-two")
    monkeypatch.setenv("GROQ_API_KEYS", "groq-one,groq-two")
    clock, observed = [0.0], []
    monkeypatch.setattr("assistant_mlops.provider.monotonic", lambda: clock[0])

    async def sleep(delay):
        clock[0] += delay

    async def handler(request):
        body = json.loads(request.content)
        assert request.url.host == "generativelanguage.googleapis.com"
        assert request.headers["Authorization"] in {"Bearer gemini-one", "Bearer gemini-two"}
        assert body["reasoning_effort"] == "none"
        assert body["model"] == "gemini-2.5-flash"
        observed.append(clock[0])
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "{}"}}], "usage": {"total_tokens": 5}}
        )

    monkeypatch.setattr("assistant_mlops.provider.asyncio.sleep", sleep)
    provider = provider_for_config(
        {
            "provider": "gemini",
            "model": "gemini-2.5-flash",
            "reasoning_effort": "none",
            "key_pool": "reserves",
            "request_interval_seconds": 15,
        }
    )
    await provider.client.aclose()
    provider.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider.fallback_url = None
    try:
        assert provider.quota_pool.keys == ["gemini-one", "gemini-two"]
        await asyncio.gather(*(provider.complete([], []) for _ in range(4)))
        assert observed == [0.0, 15.0, 30.0, 45.0]
        assert sum(provider.quota_pool.used) == 20
    finally:
        await provider.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("native_name", "expected_name", "repaired"),
    [
        ("json<|channel|>commentary", "json", True),
        ("shell<|channel|>commentary", "shell<|channel|>commentary", False),
        ("json<|channel|>analysis", "json<|channel|>analysis", False),
    ],
)
async def test_native_channel_repair_is_exact_and_advertised(native_name, expected_name, repaired):
    import json

    async def handler(request):
        assert json.loads(request.content)["disable_tool_validation"] is True
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "tool_calls": [
                                {
                                    "id": "call-1",
                                    "function": {"name": native_name, "arguments": "{}"},
                                }
                            ]
                        }
                    }
                ],
                "usage": {"prompt_tokens": 8, "completion_tokens": 2, "total_tokens": 10},
            },
        )

    provider = ChatProvider(
        base_url="https://api.groq.com/openai/v1",
        key="fixture",
        model="openai/gpt-oss-20b",
        auth_prefix="GROQ",
        application_tool_validation=True,
        transport=httpx.MockTransport(handler),
    )
    provider.fallback_url = None
    try:
        message, usage = await provider.complete([], [{"function": {"name": "json"}}])
        assert message["tool_calls"][0]["function"]["name"] == expected_name
        assert usage["total_tokens"] == 10
        assert bool(usage.get("tool_name_normalizations")) is repaired
        if repaired:
            assert usage["tool_name_normalizations"][0]["original"] == native_name
    finally:
        await provider.close()


def test_application_validation_is_scoped_to_official_groq():
    with pytest.raises(ValueError, match="official Groq"):
        ChatProvider(
            base_url="https://example.com/v1",
            model="openai/gpt-oss-20b",
            application_tool_validation=True,
        )


@pytest.mark.asyncio
async def test_explicit_reasoning_effort_is_sent_to_supported_model():
    async def handler(request):
        import json

        assert json.loads(request.content)["reasoning_effort"] == "low"
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "{}"}}], "usage": {"total_tokens": 5}}
        )

    provider = ChatProvider(
        base_url="https://api.groq.com/openai/v1",
        key="fixture",
        model="openai/gpt-oss-120b",
        reasoning_effort="low",
        auth_prefix="GROQ",
        transport=httpx.MockTransport(handler),
    )
    provider.fallback_url = None
    await provider.complete([], [])
    await provider.close()


def test_invalid_reasoning_configuration_fails_before_opening_client():
    with pytest.raises(ValueError, match="requires GPT-OSS"):
        ChatProvider(model="Qwen/Qwen2.5-7B-Instruct", reasoning_effort="low")


@pytest.mark.asyncio
@pytest.mark.parametrize("fallback_model", ["openai/gpt-oss-20b", "openai/gpt-oss-120b"])
async def test_depleted_primary_pool_uses_scoped_same_endpoint_fallback(
    monkeypatch, fallback_model
):
    import json

    monkeypatch.setenv("FALLBACK_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setenv("FALLBACK_MODEL", fallback_model)
    monkeypatch.setenv("FALLBACK_API_KEY", "fixture-fallback")
    monkeypatch.delenv("FALLBACK_PROXY_TOKEN", raising=False)
    monkeypatch.delenv("FALLBACK_PROXY_COOKIE", raising=False)

    async def handler(request):
        assert json.loads(request.content)["model"] == fallback_model
        assert request.headers["Authorization"] == "Bearer fixture-fallback"
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "{}"}}], "usage": {"total_tokens": 5}}
        )

    provider = ChatProvider(
        base_url="https://api.groq.com/openai/v1",
        key="fixture-primary",
        model="openai/gpt-oss-120b",
        key_pool=["fixture-primary"],
        daily_token_budget=9,
        auth_prefix="GROQ",
        transport=httpx.MockTransport(handler),
    )
    provider.quota_pool.used[0] = 9
    _, usage = await provider.complete([], [])
    assert usage["fallback"] and usage["model"] == fallback_model
    assert provider.quota_pool.used == [9]
    await provider.close()


@pytest.mark.asyncio
async def test_retry_and_usage(monkeypatch):
    attempts = []

    async def handler(request):
        attempts.append(request)
        if len(attempts) == 1:
            return httpx.Response(503)
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "{}"}}], "usage": {"total_tokens": 9}}
        )

    async def no_sleep(_):
        pass

    monkeypatch.setattr("assistant_mlops.provider.asyncio.sleep", no_sleep)
    provider = ChatProvider(
        base_url="https://fixture.test", key="fixture", transport=httpx.MockTransport(handler)
    )
    message, usage = await provider.complete([], [])
    assert len(attempts) == 2 and usage["total_tokens"] == 9
    await provider.close()


@pytest.mark.asyncio
async def test_proxy_auth_is_scoped_and_cookie_prefix_removed(monkeypatch):
    monkeypatch.setenv("AGENT_PROXY_TOKEN", "fixture-token")
    monkeypatch.setenv("AGENT_PROXY_COOKIE", "\nCookie: fixture=session\n")
    monkeypatch.setenv("FALLBACK_BASE_URL", "https://groq.test/openai/v1")
    monkeypatch.setenv("FALLBACK_API_KEY", "groq-fixture")
    requests = []

    async def handler(request):
        requests.append(request)
        if request.url.host == "proxy.test":
            assert request.headers["Authorization"] == "token fixture-token"
            assert request.headers["Cookie"] == "fixture=session"
            return httpx.Response(401)
        assert request.headers["Authorization"] == "Bearer groq-fixture"
        assert "Cookie" not in request.headers
        return httpx.Response(200, json={"choices": [{"message": {"content": "hello"}}]})

    provider = ChatProvider(
        base_url="https://proxy.test/v1", key="", transport=httpx.MockTransport(handler)
    )
    assert provider.configured
    _, usage = await provider.complete([], [])
    assert usage["fallback"] and len(requests) == 2
    await provider.close()


@pytest.mark.asyncio
async def test_fallback_and_graceful_failure(monkeypatch):
    monkeypatch.setenv("FALLBACK_BASE_URL", "https://backup.test")

    async def no_sleep(_):
        pass

    monkeypatch.setattr("assistant_mlops.provider.asyncio.sleep", no_sleep)

    async def handler(request):
        if request.url.host == "backup.test":
            return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})
        return httpx.Response(503)

    provider = ChatProvider(
        base_url="https://primary.test", key="fixture", transport=httpx.MockTransport(handler)
    )
    _, usage = await provider.complete([], [])
    assert usage["fallback"] is True and usage["total_tokens"] is None
    await provider.close()


@pytest.mark.asyncio
async def test_explicit_groq_client_never_inherits_primary_proxy(monkeypatch):
    monkeypatch.setenv("AGENT_PROXY_TOKEN", "primary-secret")
    monkeypatch.setenv("AGENT_PROXY_COOKIE", "primary=session")

    async def handler(request):
        assert request.headers["Authorization"] == "Bearer groq-fixture"
        assert "Cookie" not in request.headers
        return httpx.Response(200, json={"choices": [{"message": {"content": "hello"}}]})

    provider = ChatProvider(
        base_url="https://groq.test/openai/v1",
        key="groq-fixture",
        auth_prefix="GROQ",
        transport=httpx.MockTransport(handler),
    )
    await provider.complete([], [])
    await provider.close()
    provider = ChatProvider(
        base_url="https://primary.test",
        key="fixture",
        transport=httpx.MockTransport(lambda _: httpx.Response(503)),
    )
    with pytest.raises(ProviderError):
        await provider.complete([], [])
    await provider.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, expected",
    [(401, ["Bearer rejected", "Bearer reserve"]), (429, ["Bearer rejected"] * 3)],
)
async def test_groq_reserve_keys_only_on_auth_rejection(monkeypatch, status, expected):
    monkeypatch.setenv("GROQ_API_KEYS", "rejected,reserve")
    observed = []
    pauses = []

    async def sleep(delay):
        pauses.append(delay)

    async def handler(request):
        observed.append(request.headers["Authorization"])
        if request.headers["Authorization"] == "Bearer reserve":
            return httpx.Response(200, json={"choices": [{"message": {"content": "hello"}}]})
        return httpx.Response(status, headers={"Retry-After": "2"})

    monkeypatch.setattr("assistant_mlops.provider.asyncio.sleep", sleep)
    provider = ChatProvider(
        base_url="https://api.groq.com/openai/v1",
        key="rejected",
        auth_prefix="GROQ",
        transport=httpx.MockTransport(handler),
    )
    provider.fallback_url = None
    if status == 429:
        with pytest.raises(ProviderError):
            await provider.complete([], [])
        assert pauses == [2, 2]
    else:
        await provider.complete([], [])
    assert observed == expected
    await provider.close()


@pytest.mark.asyncio
async def test_pacing_is_shared_across_concurrent_queries(monkeypatch):
    import asyncio

    clock = [0.0]
    sent = []
    monkeypatch.setattr("assistant_mlops.provider.monotonic", lambda: clock[0])

    async def sleep(delay):
        clock[0] += delay

    async def handler(request):
        sent.append(clock[0])
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

    monkeypatch.setattr("assistant_mlops.provider.asyncio.sleep", sleep)
    provider = ChatProvider(
        base_url="https://fixture.test",
        key="fixture",
        transport=httpx.MockTransport(handler),
        request_interval_seconds=15,
    )
    provider.fallback_url = None
    await asyncio.gather(*(provider.complete([], []) for _ in range(3)))
    assert sent == [0.0, 15.0, 30.0]
    await provider.close()


@pytest.mark.asyncio
async def test_recorded_groq_model_uses_groq_credentials(monkeypatch):
    from assistant_mlops.provider import provider_for_config

    monkeypatch.setenv("AGENT_PROXY_TOKEN", "primary-secret")
    monkeypatch.setenv("AGENT_PROXY_COOKIE", "primary=session")
    monkeypatch.setenv("GROQ_API_KEY", "groq-fixture")
    provider = provider_for_config(
        {"provider": "groq", "model": "candidate", "request_interval_seconds": 15}
    )
    assert provider.model == "candidate"
    assert provider.headers["Authorization"] == "Bearer groq-fixture"
    assert "Cookie" not in provider.headers
    assert provider.request_interval_seconds == 15
    await provider.close()


@pytest.mark.asyncio
async def test_quota_pool_cools_only_the_limited_bucket(monkeypatch):
    clock = [0.0]
    observed = []
    monkeypatch.setattr("assistant_mlops.provider.monotonic", lambda: clock[0])

    async def sleep(delay):
        clock[0] += delay

    async def handler(request):
        key = request.headers["Authorization"]
        observed.append((key, clock[0]))
        if key == "Bearer limited":
            return httpx.Response(429, headers={"Retry-After": "30"})
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "{}"}}], "usage": {"total_tokens": 9}}
        )

    monkeypatch.setattr("assistant_mlops.provider.asyncio.sleep", sleep)
    provider = ChatProvider(
        base_url="https://api.groq.com/openai/v1",
        key="limited",
        auth_prefix="GROQ",
        transport=httpx.MockTransport(handler),
        key_pool=["limited", "available"],
        request_interval_seconds=15,
    )
    provider.fallback_url = None
    await provider.complete([], [])
    await provider.complete([], [])
    assert observed == [
        ("Bearer limited", 0.0),
        ("Bearer available", 0.0),
        ("Bearer available", 15.0),
    ]
    assert provider.quota_pool.ready[0] == 30
    await provider.close()


@pytest.mark.asyncio
async def test_quota_pool_paces_each_bucket_independently(monkeypatch):
    import asyncio

    clock = [0.0]
    observed = []
    monkeypatch.setattr("assistant_mlops.provider.monotonic", lambda: clock[0])

    async def sleep(delay):
        clock[0] += delay

    async def handler(request):
        observed.append((request.headers["Authorization"], clock[0]))
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

    monkeypatch.setattr("assistant_mlops.provider.asyncio.sleep", sleep)
    provider = ChatProvider(
        base_url="https://api.groq.com/openai/v1",
        key="one",
        auth_prefix="GROQ",
        transport=httpx.MockTransport(handler),
        key_pool=["one", "two"],
        request_interval_seconds=15,
    )
    provider.fallback_url = None
    await asyncio.gather(*(provider.complete([], []) for _ in range(4)))
    for key in ["Bearer one", "Bearer two"]:
        assert [timestamp for seen, timestamp in observed if seen == key] == [0.0, 15.0]
    await provider.close()


@pytest.mark.asyncio
async def test_quota_pool_stops_at_local_daily_budget():
    async def handler(request):
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "{}"}}], "usage": {"total_tokens": 9}}
        )

    provider = ChatProvider(
        base_url="https://api.groq.com/openai/v1",
        key="one",
        auth_prefix="GROQ",
        transport=httpx.MockTransport(handler),
        key_pool=["one", "two"],
        daily_token_budget=9,
    )
    provider.fallback_url = None
    await provider.complete([], [])
    await provider.complete([], [])
    with pytest.raises(ProviderError):
        await provider.complete([], [])
    assert provider.quota_pool.used == [9, 9]
    await provider.close()


@pytest.mark.asyncio
async def test_pool_returns_safely_when_all_cooldowns_exceed_wait_budget():
    from assistant_mlops.provider import QuotaKeyPool

    pool = QuotaKeyPool(["fixture"], interval=15, daily_budget=180000)
    pool.block(0, 90)
    with pytest.raises(ProviderError, match="cooling down"):
        await pool.acquire()
