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
    provider = ChatProvider(
        base_url="https://primary.test",
        key="fixture",
        transport=httpx.MockTransport(lambda _: httpx.Response(503)),
    )
    with pytest.raises(ProviderError):
        await provider.complete([], [])
    await provider.close()
