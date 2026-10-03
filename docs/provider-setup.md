# GPU proxy first, Groq next

The local `.env` selects the user's existing Qwen2.5-7B-Instruct GPU endpoint through HTTPS Jupyter server proxy. Credentials are ignored by Git and restricted to owner read/write.

Required local values:

```dotenv
AGENT_BASE_URL=https://YOUR-HOST/user/YOUR-USER/proxy/8000/v1
AGENT_MODEL=Qwen/Qwen2.5-7B-Instruct
AGENT_API_KEY=unused
AGENT_PROXY_TOKEN=YOUR_JUPYTER_TOKEN
AGENT_PROXY_COOKIE='YOUR_COOKIE_VALUE'
```

Paste only the cookie value; a leading `Cookie:` label is also accepted and removed. Requests send `Authorization: token ...` to the configured proxy. TLS verification stays enabled; redirects are not followed. Proxy credentials are separate for the primary and fallback endpoint and never appear in model traces or error reports. Renew expiring Jupyter sessions in this local file.

Run `.venv/bin/python scripts/check_provider.py` to check model discovery, a Nepali greeting, and native tool calls. It saves a sanitized `reports/provider_connection.json`. A failed check does not prove GPU inference works. After updating credentials/configuration, run `docker compose up -d --build --force-recreate backend`.

## Switch to Groq after obtaining the key

Set these values in `.env`:

```dotenv
AGENT_BASE_URL=https://api.groq.com/openai/v1
AGENT_MODEL=openai/gpt-oss-20b
AGENT_API_KEY=YOUR_GROQ_API_KEY
AGENT_PROXY_TOKEN=
AGENT_PROXY_COOKIE=
```

Clear both primary proxy fields when changing its URL. Verify that the chosen model is enabled for your Groq account using `/models`; repeat the provider check before experiments. Groq supports the existing OpenAI-compatible client protocol: https://console.groq.com/docs/openai. Current model availability: https://console.groq.com/docs/models.

Alternatively, keep Qwen as primary and configure Groq with `FALLBACK_BASE_URL`, `FALLBACK_MODEL`, and `FALLBACK_API_KEY`. Leave `FALLBACK_PROXY_TOKEN` and `FALLBACK_PROXY_COOKIE` empty for Groq. Primary proxy headers are never copied to the fallback.

Agent API access and judge API access are separate. Native Evidently evaluation still needs a configured judge and reviewed calibration labels. Cloud provider selection is deferred until the user supplies a target and budget.

## Verified university endpoint result

On 2026-10-03, authenticated `/models` returned 200 and listed Qwen/Qwen2.5-7B-Instruct. A real greeting returned नमस्ते, using 52 tokens. The initial native tool check returned HTTP 400 until automatic tool choice/parser were enabled. The subsequent check passed and returned a real native search call (335 tokens). Current evidence: `reports/provider_connection.json`.

On the GPU host, stop the existing model process before starting its replacement on the same port. Preserve its existing memory/context settings and any backend API key; add the two tool flags. A basic command for the supplied model is:

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice --tool-call-parser hermes
```

The proxy remains `/proxy/8000/v1`. The repository's `serving/serve_vllm.sh` also enables these flags, but uses port 8002 and requires its own API key; it is not a drop-in replacement for this proxy setup. Do not claim native agent execution until the check succeeds after the GPU server is restarted.

## Authorized provider allocation

KU Qwen2.5-7B runs v1–v12. Groq Qwen3.8-27B is the stronger candidate in v13/v14; the independent native Evidently judge remains Groq GPT-OSS-20B. Five Groq and five Gemini keys remain in the ignored local environment. Explicit `key_pool: reserves` activates paced available Groq buckets, full server cooldowns, bounded waits and local token guards; default clients retain authentication-only failover. Gemini remains an alternative. See [runtime evidence and quota limits](evaluation-runtime.md). No quota settings are modified.
