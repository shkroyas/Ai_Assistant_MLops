# Provider allocation

This allocation follows the W15–W17 implementation plan and the user's request to try Groq. Task A remains independent and uses no LLM API keys.

| Work | Provider/model | Purpose |
|---|---|---|
| W15 `/rag` single-pass baseline | Groq `openai/gpt-oss-20b` | Major-provider API baseline; exact corpus citations |
| W16 `/ask` and `/batch` agent | KU GPU `Qwen/Qwen2.5-7B-Instruct` | Native multi-step search/read-source loop |
| Runtime fallback | Groq `openai/gpt-oss-20b` | Endpoint failures still obey the answer/citation contract |
| W17 v1–v4 experiments | Fixed KU Qwen model; fallback disabled | Compare prompt/retrieval/step changes without switching model families |
| Evidently correctness/completeness judge | Gemini `gemini-2.5-flash` | Independent model family; reviewed reference answers |
| Judge calibration | Same Gemini model | Measure agreement and false passes on 15 approved calibration labels |
| Nightly Airflow | Production agent; deterministic ground truth only | No judge calls or automatic promotion |

## Key use

Five Groq and five Gemini keys were supplied as comma-separated values. Each provider now has one active singular key; all supplied values are preserved in local `GROQ_API_KEYS` and `GEMINI_API_KEYS` reserve lists. Reserve lists are not automatically rotated. The active Groq key is also assigned to the runtime fallback; Gemini is reserved for the judge rather than serving as an agent fallback. Keys stay in ignored `.env` with mode 0600 and are never logged to MLflow.

Additional keys do not imply additional quota: Groq documents organization-level limits, while Gemini limits are project-scoped. Use backoff and the judge pacing at one request per 15 seconds (the observed Gemini quota is 5 RPM). Sources: https://console.groq.com/docs/rate-limits and https://ai.google.dev/gemini-api/docs/rate-limits.

## Live checks

- `reports/api_availability.json`: Groq and Gemini model discovery both returned 200; selected models were listed.
- `reports/provider_connection.json`: real KU model discovery, greeting, and Qwen native search call passed after server tool support was enabled.
- `reports/provider_roles_smoke.json`: real Groq W15 retrieval response includes a verified quote; Groq native tool-call protocol passed; native Gemini/Evidently classified a matching reference as pass and a contradictory answer as fail.
- `reports/provider_judge_smoke/`: actual Evidently HTML, JSON and judge verdicts for those two examples. This is a plumbing smoke test, not full judge calibration or a benchmark. The Groq tool smoke produced an unrecognized source filter; full agent evaluation must measure tool argument correctness rather than inferring it from protocol support.

Royas authorized delegated assistant review of the 15 calibration labels. The review record includes provenance and label SHA. It does not claim individual manual human labeling. Full calibration, repeated v1–v4 experiments, gate checks, promotion, healthy nightly evidence and cloud deployment are separate remaining execution stages.

The activated API's `/rag` query answered with Groq. The first Qwen `/ask` query safely abstained at its seven-iteration budget; see `reports/provider_routes_smoke.json`. This is a real initial quality failure to investigate with development traces, not an endpoint failure.

The initial full calibration attempt hit a genuine Gemini HTTP 429 (observed 5 RPM). It did not produce a completed calibration report. Judge requests now use a 15-second interval, including a pause between native descriptors. API keys are not auto-rotated to avoid quota pacing. Raw SDK exception chains are suppressed because they can include credential-bearing URLs. The initial v1 run was interrupted before its judge stage and explicitly marked KILLED in MLflow.
