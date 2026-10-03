import asyncio
import os

import httpx


class ProviderError(RuntimeError):
    pass


class ChatProvider:
    """Gemini's compatible API or a vLLM endpoint. Never silently uses a mock."""

    def __init__(self, base_url=None, key=None, model=None, transport=None):
        self.base_url = (
            base_url
            or os.getenv("AGENT_BASE_URL")
            or "https://generativelanguage.googleapis.com/v1beta/openai"
        )
        self.key = key if key is not None else os.getenv("AGENT_API_KEY", "")
        self.model = model or os.getenv("AGENT_MODEL") or "gemini-2.5-flash"
        self.client = httpx.AsyncClient(timeout=40, transport=transport)
        self.fallback_url = os.getenv("FALLBACK_BASE_URL")

    async def close(self):
        await self.client.aclose()

    async def complete(self, messages, tools, temperature=0.1, top_p=0.9):
        if not self.key and not self.fallback_url:
            raise ProviderError("No model credentials configured")
        endpoints = [(self.base_url, self.key, self.model)]
        if self.fallback_url:
            endpoints.append(
                (
                    self.fallback_url,
                    os.getenv("FALLBACK_API_KEY", ""),
                    (os.getenv("FALLBACK_MODEL") or "Qwen/Qwen2.5-7B-Instruct"),
                )
            )
        for base, key, model in endpoints:
            for attempt in range(3):
                try:
                    response = await self.client.post(
                        base.rstrip("/") + "/chat/completions",
                        headers={"Authorization": f"Bearer {key}"},
                        json={
                            "model": model,
                            "messages": messages,
                            **({"tools": tools} if tools else {}),
                            "temperature": temperature,
                            "top_p": top_p,
                            "max_tokens": 1200,
                        },
                    )
                    if response.status_code == 429 or response.status_code >= 500:
                        if attempt < 2:
                            await asyncio.sleep(0.5 * 2**attempt)
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
                    # Do not invent usage when the upstream endpoint omits it.
                    return message, {
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "completion_tokens": usage.get("completion_tokens"),
                        "total_tokens": usage.get("total_tokens"),
                        "model": model,
                        "fallback": base != self.base_url,
                    }
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code != 429 and exc.response.status_code < 500:
                        break
                    if attempt < 2:
                        await asyncio.sleep(0.5 * 2**attempt)
                except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError):
                    if attempt < 2:
                        await asyncio.sleep(0.5 * 2**attempt)
        raise ProviderError("All configured model providers failed")
