import asyncio
import os
from time import monotonic
from urllib.parse import urlsplit

import httpx

from assistant_mlops.auth import endpoint_headers


class ProviderError(RuntimeError):
    pass


class QuotaKeyPool:
    """Pace independently available, user-owned quota buckets and honor cooldowns."""

    def __init__(self, keys, interval, daily_budget):
        self.keys = list(dict.fromkeys(keys))
        self.interval, self.daily_budget = interval, daily_budget
        self.ready = [0.0] * len(self.keys)
        self.busy = [False] * len(self.keys)
        self.used = [0] * len(self.keys)
        self.condition = asyncio.Condition()

    async def acquire(self):
        deadline = monotonic() + 60
        while True:
            async with self.condition:
                eligible = [
                    i
                    for i in range(len(self.keys))
                    if self.used[i] < self.daily_budget and self.ready[i] != float("inf")
                ]
                if not eligible:
                    raise ProviderError("All configured quota buckets are unavailable")
                free = [i for i in eligible if not self.busy[i]]
                if not free:
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        raise ProviderError("Quota queue wait exceeded the request budget")
                    try:
                        await asyncio.wait_for(self.condition.wait(), timeout=remaining)
                    except asyncio.TimeoutError:
                        raise ProviderError(
                            "Quota queue wait exceeded the request budget"
                        ) from None
                    continue
                slot = min(free, key=lambda i: self.ready[i])
                delay = self.ready[slot] - monotonic()
                if delay <= 0:
                    self.busy[slot] = True
                    self.ready[slot] = monotonic() + self.interval
                    return slot, self.keys[slot]
                if monotonic() + delay > deadline:
                    raise ProviderError(
                        "Quota buckets are cooling down beyond the request wait budget"
                    )
            await asyncio.sleep(min(delay, 60))

    def block(self, slot, delay):
        self.ready[slot] = max(self.ready[slot], monotonic() + delay)

    async def release(self, slot):
        async with self.condition:
            self.busy[slot] = False
            self.condition.notify_all()


class ChatProvider:
    """OpenAI-compatible providers, including authenticated Jupyter-proxied vLLM."""

    def __init__(
        self,
        base_url=None,
        key=None,
        model=None,
        transport=None,
        auth_prefix="AGENT",
        request_interval_seconds=0,
        key_pool=None,
        daily_token_budget=180000,
        reasoning_effort=None,
    ):
        self.base_url = (
            base_url
            or os.getenv("AGENT_BASE_URL")
            or "https://generativelanguage.googleapis.com/v1beta/openai"
        )
        self.key = key if key is not None else os.getenv("AGENT_API_KEY", "")
        self.model = model or os.getenv("AGENT_MODEL") or "gemini-2.5-flash"
        if reasoning_effort is not None and (
            reasoning_effort not in {"low", "medium", "high"}
            or not self.model.startswith("openai/gpt-oss-")
        ):
            raise ValueError("Explicit reasoning effort requires GPT-OSS and low/medium/high")
        self.reasoning_effort = reasoning_effort
        self.client = httpx.AsyncClient(timeout=40, transport=transport)
        self.fallback_url = os.getenv("FALLBACK_BASE_URL")
        self.headers = endpoint_headers(auth_prefix, self.key)
        self.configured = bool(self.key or os.getenv(f"{auth_prefix}_PROXY_TOKEN"))
        if not 0 <= request_interval_seconds <= 60:
            raise ValueError("Request pacing interval must be between zero and sixty seconds")
        self.request_interval_seconds = request_interval_seconds
        self._pacing_lock = asyncio.Lock()
        self._last_request = None
        self.quota_pool = None
        if key_pool:
            if urlsplit(self.base_url).hostname != "api.groq.com" or "Cookie" in self.headers:
                raise ValueError(
                    "Quota pools require the official Groq endpoint without proxy cookies"
                )
            if not 1 <= daily_token_budget <= 200000:
                raise ValueError("Daily pool budget must fit the verified 200000-token allowance")
            self.quota_pool = QuotaKeyPool(key_pool, request_interval_seconds, daily_token_budget)

    async def close(self):
        await self.client.aclose()

    async def complete(self, messages, tools, temperature=0.1, top_p=0.9):
        if not self.configured and not self.fallback_url:
            raise ProviderError("No model credentials configured")
        endpoints = [(self.base_url, self.headers, self.model)] if self.configured else []
        if self.fallback_url:
            endpoints.append(
                (
                    self.fallback_url,
                    endpoint_headers("FALLBACK", os.getenv("FALLBACK_API_KEY", "")),
                    (os.getenv("FALLBACK_MODEL") or "Qwen/Qwen2.5-7B-Instruct"),
                )
            )
        for base, headers, model in endpoints:
            keys = [headers.get("Authorization", "")]
            if urlsplit(base).hostname == "api.groq.com" and "Cookie" not in headers:
                keys += [
                    "Bearer " + key.strip()
                    for key in os.getenv("GROQ_API_KEYS", "").split(",")
                    if key.strip()
                ]
            pool = (
                self.quota_pool
                if base == self.base_url
                and model == self.model
                and urlsplit(base).hostname == "api.groq.com"
                and "Cookie" not in headers
                else None
            )
            keys = list(dict.fromkeys(keys)) if not pool else [keys[0]]
            key_index, transient_attempt = 0, 0
            for _ in range(3 + (len(pool.keys) if pool else len(keys))):
                headers = {**headers, "Authorization": keys[key_index]}
                attempt = transient_attempt
                lease = None
                try:
                    if pool:
                        lease, leased_key = await pool.acquire()
                        headers["Authorization"] = "Bearer " + leased_key
                    if self.request_interval_seconds and not pool:
                        async with self._pacing_lock:
                            if self._last_request is not None:
                                delay = self.request_interval_seconds - (
                                    monotonic() - self._last_request
                                )
                                if delay > 0:
                                    await asyncio.sleep(delay)
                            self._last_request = monotonic()
                    response = await self.client.post(
                        base.rstrip("/") + "/chat/completions",
                        headers=headers,
                        json={
                            "model": model,
                            "messages": messages,
                            **({"tools": tools} if tools else {}),
                            "temperature": temperature,
                            "top_p": top_p,
                            "max_tokens": 1200,
                            **(
                                {"reasoning_effort": self.reasoning_effort}
                                if self.reasoning_effort and model.startswith("openai/gpt-oss-")
                                else {}
                            ),
                        },
                    )
                    if pool and response.status_code in {401, 403, 429}:
                        if response.status_code in {401, 403}:
                            pool.block(lease, float("inf"))
                        else:
                            try:
                                delay = float(response.headers.get("Retry-After", 60))
                            except ValueError:
                                delay = 60
                            pool.block(lease, max(pool.interval, delay))
                        continue
                    if response.status_code in {401, 403} and key_index + 1 < len(keys):
                        key_index += 1
                        continue
                    if response.status_code == 429 or response.status_code >= 500:
                        if attempt < 2:
                            transient_attempt += 1
                            try:
                                delay = float(response.headers.get("Retry-After", 0))
                            except ValueError:
                                delay = 0
                            await asyncio.sleep(min(60, max(delay, 0.5 * 2**attempt)))
                            continue
                    response.raise_for_status()
                    payload = response.json()
                    message = payload["choices"][0]["message"]
                    if not isinstance(message, dict):
                        raise ValueError("Malformed model message")
                    calls = message.get("tool_calls") or []
                    if not isinstance(calls, list):
                        raise ValueError("Malformed tool_calls")
                    for call in calls:
                        if not isinstance(call, dict) or not isinstance(call.get("function"), dict):
                            raise ValueError("Malformed tool call")
                        if not all(
                            isinstance(v, str)
                            for v in [
                                call.get("id"),
                                call["function"].get("name"),
                                call["function"].get("arguments"),
                            ]
                        ):
                            raise ValueError("Malformed tool-call fields")
                    usage = payload.get("usage", {})
                    if pool:
                        pool.used[lease] += usage.get("total_tokens") or 0
                    # Do not invent usage when the upstream endpoint omits it.
                    return message, {
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "completion_tokens": usage.get("completion_tokens"),
                        "total_tokens": usage.get("total_tokens"),
                        "model": model,
                        "fallback": (base, model) != (self.base_url, self.model),
                    }
                except ProviderError:
                    # A depleted primary pool must not prevent an independently
                    # configured fallback model from being attempted.
                    break
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code != 429 and exc.response.status_code < 500:
                        break
                    break
                except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError):
                    if attempt < 2:
                        transient_attempt += 1
                        await asyncio.sleep(0.5 * 2**attempt)
                    else:
                        break
                finally:
                    if pool and lease is not None:
                        await pool.release(lease)
        raise ProviderError("All configured model providers failed")


def provider_for_config(config):
    """Choose a recorded provider/model while keeping credentials in the environment."""
    if config.get("provider", "agent") == "agent":
        return ChatProvider(
            model=config.get("model"),
            request_interval_seconds=config.get("request_interval_seconds", 0),
        )
    if config["provider"] != "groq":
        raise ValueError("Unsupported experiment provider")
    pool = None
    if config.get("key_pool") == "reserves":
        active = os.getenv("GROQ_API_KEY", "")
        pool = [
            key.strip()
            for key in os.getenv("GROQ_API_KEYS", "").split(",")
            if key.strip() and key.strip() != active
        ]
        if not pool:
            raise ValueError("No independently available reserve keys configured")
    return ChatProvider(
        base_url="https://api.groq.com/openai/v1",
        key=pool[0] if pool else os.getenv("GROQ_API_KEY", ""),
        model=config.get("model") or os.getenv("GROQ_MODEL") or "openai/gpt-oss-20b",
        auth_prefix="GROQ",
        request_interval_seconds=config.get("request_interval_seconds", 0),
        key_pool=pool,
        daily_token_budget=config.get("daily_token_budget", 180000),
        reasoning_effort=config.get("reasoning_effort"),
    )
