import httpx
import pytest

from assistant_mlops.provider import ChatProvider, ProviderError


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
