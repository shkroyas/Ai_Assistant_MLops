# Provider allocation

This allocation follows the W15–W17 implementation plan and the user's request to try Groq. Task A remains independent and uses no LLM API keys.

| Work | Provider/model | Purpose |
|---|---|---|
| W15 `/rag` single-pass baseline | Groq `openai/gpt-oss-20b` | Major-provider API baseline; exact corpus citations |
| W16 `/ask` and `/batch` agent | Explicit configuration override or promoted model | Native multi-step search/read-source loop |
| Runtime fallback | Groq `openai/gpt-oss-20b` | Endpoint failures still obey the answer/citation contract |
| W17 v1–v12 experiments | Fixed KU Qwen2.5-7B; fallback disabled | Prompt, retrieval, iteration and output-mode comparisons |
| W17 v13–v15 | Groq Qwen3.8-27B | Stronger candidate; quota-limited evidence retained |
| W17 v16–v19 | Groq GPT-OSS-120B | Stronger available candidate; native schema/final-answer/low-reasoning comparisons |
| Evidently correctness/completeness judge | Groq `openai/gpt-oss-20b`; Gemini alternative | Separate native judge calls and reviewed references; different family from Qwen |
| Judge calibration | Same Groq judge model | Measure agreement and false passes on 15 approved calibration labels |
| Nightly Airflow | Production agent; deterministic ground truth only | No judge calls or automatic promotion |

## Key use

Five Groq and five Gemini keys were supplied as comma-separated values. Each provider now has one active singular key; all supplied values are preserved in local `GROQ_API_KEYS` and `GEMINI_API_KEYS` reserve lists. Default Groq clients try reserve keys after authentication rejection (401/403). Explicit `key_pool: reserves` configurations use verified available buckets with per-key pacing, full reported Retry-After cooldowns, bounded waits and local token guards. A small accepted probe does not establish sufficient quota for a full run. Native judge calls use the configured active judge key. The active Groq key is also assigned to the runtime fallback; Gemini is an alternative judge rather than an agent fallback. Keys stay in ignored `.env` with mode 0600 and are never logged to MLflow.

Additional keys do not imply additional quota: Groq documents organization-level limits, while Gemini limits are project-scoped. Current Groq judging is paced at one request per 10 seconds. Gemini needs at least 15 seconds between requests for the observed 5 RPM quota. Sources: https://console.groq.com/docs/rate-limits and https://ai.google.dev/gemini-api/docs/rate-limits.

## Live checks

- `reports/api_availability.json`: Groq and Gemini model discovery both returned 200; selected models were listed.
- `reports/provider_connection.json`: real KU model discovery, greeting, and Qwen native search call passed after server tool support was enabled.
- `reports/provider_roles_smoke.json`: real Groq W15 retrieval response includes a verified quote; Groq native tool-call protocol passed; native Gemini/Evidently classified a matching reference as pass and a contradictory answer as fail.
- `reports/provider_judge_smoke/`: actual Evidently HTML, JSON and judge verdicts for those two examples. This is a plumbing smoke test, not full judge calibration or a benchmark. The Groq tool smoke produced an unrecognized source filter; full agent evaluation must measure tool argument correctness rather than inferring it from protocol support.

Royas authorized delegated assistant review of the 15 calibration labels. The review record includes provenance and label SHA. It does not claim individual manual human labeling. Full Groq calibration completed with agreement 1.0 and false-pass rate 0.0. Repeated experiments and native judging are underway; production promotion, healthy nightly evidence and cloud deployment remain separate execution stages.

The activated API's `/rag` query answered with Groq. The first Qwen `/ask` query safely abstained at its seven-iteration budget; see `reports/provider_routes_smoke.json`. This is a real initial quality failure to investigate with development traces, not an endpoint failure.

The initial full calibration attempt hit a genuine Gemini HTTP 429 (observed 5 RPM). It did not produce a completed calibration report. That Gemini attempt used a corrected 15-second interval, including a pause between native descriptors. That Gemini attempt used one active key with paced calls. Raw SDK exception chains are suppressed because they can include credential-bearing URLs. The initial v1 run was interrupted before its judge stage and explicitly marked KILLED in MLflow.

The user subsequently authorized Qwen or Groq for execution. Current experiments use independent Groq judging with paced calls and native duplicate-input reuse; Gemini remains an alternative rather than a quota-rotation target. See docs/evaluation-runtime.md.

GPT-OSS-120B agent and GPT-OSS-20B judge are different models with separate calls, but share a model family; this may limit judge independence. The frozen deterministic truth gate remains separately required. No golden labels, prompts or quality thresholds are changed in response to held-out results. The v16 rejection was diagnosed with development-query replays only: `source_id: null` is valid for unfiltered runtime search but did not match the old tool schema. v17 changes only that optional field and retains strict required/string-only `read_source`.

The smaller GPT-OSS-20B candidate (v20 and the protocol-repair follow-up) uses reserve credentials 2–5 for the agent and credential 1 for the judge. These are separate calls and credentials but the same model weights, so model independence is not claimed. The 15 approved calibration cases, frozen deterministic truth checks and unchanged promotion criteria still apply. Gemini remains an alternative with its earlier native two-case sanity evidence; no complete Gemini calibration is claimed.
