# Provider allocation

Task A remains a separate repository and uses no LLM API keys. This standalone Task B uses the assignment's fictional example-company handbook.

| Work | Provider/model | Purpose |
|---|---|---|
| W15 `/rag` baseline | Groq GPT-OSS-20B | Verified cited single-pass major-provider baseline |
| W16 `/ask` and `/batch` | Explicit configuration, or explicitly promoted configuration | Bounded native search/read-source verification loop |
| v1–v12 | KU Qwen2.5-7B GPU | Prompt, retrieval and context experiments |
| v13–v15 | Groq Qwen3.8-27B | Stronger candidate; quota failures retained |
| v16–v19 | Groq GPT-OSS-120B | Tool schema, final submission and reasoning experiments |
| v20–v22 | Groq GPT-OSS-20B | Smaller model, native name repair and medium reasoning experiments |
| v23 | Gemini 2.5 Flash | Independent model family; stopped with partial evidence after daily quota exhaustion |
| v24 | Groq GPT-OSS-120B, medium reasoning | Fresh full cohort with native name repair and conservative pacing |
| Historical native judge | Groq GPT-OSS-20B | Correctness and completeness; same family as GPT agents and same weights as 20B agents |
| Current native judge | Groq GPT-OSS-120B | Recalibrated on the same 15 approved labels; also shares weights with the v24 agent |
| Nightly Airflow | Promoted production agent, deterministic frozen references | No native judge calls or automatic promotion |

All five Groq and five Gemini credentials remain in ignored mode-0600 `.env`. No keys, tokens or cookies are logged or committed. Experiments disable provider fallback to preserve model identity. Default clients reserve authentication failover for 401/403; explicit `key_pool: reserves` candidates use paced, separately observed available buckets. Additional keys do not establish additional independent quota.

Groq agent pools exclude the active singular key and use conservative full reported-token budgets and complete server cooldowns. v24 uses a 25-second per-key interval. Explicit `JUDGE_API_KEYS` enables the separately paced native Groq judge pool; authentication failures retire a key and quota failures honor full server cooldowns. This does not remove project or organization limits. Model/endpoint headers stay scoped, including when fallback has the same model and URL.

Gemini uses the official OpenAI-compatible endpoint, native tools, and documented `reasoning_effort: none` for 2.5 Flash. Its pool is paced globally, so multiple keys do not multiply project RPM. Two Lite agent smoke cases and three Flash smoke cases passed, but the full Flash cohort encountered only unavailable-provider results. All five Flash keys subsequently returned HTTP 429 with `GenerateRequestsPerDayPerProjectPerModel-FreeTier` and quota value 20. See `reports/gemini_flash_project_quota.json` and `reports/v23/partial_manifest.json`. Small successful probes cannot establish capacity for 159 multi-step samples.

Native judging retains both actual criteria, approved references and cached verdict provenance. Unchanged agent checkpoints may resume a failed judge stage as a separate recorded run; failed agent samples are retained. Royas approved delegated assistant review of the 15 labels ("okay I trust you"). Both Groq judge models agreed with all 15 approved labels with zero false passes. This small assistant-reviewed calibration and shared agent/judge weights remain limitations; frozen deterministic ground truth and every unchanged gate criterion are still separately required.

See `reports/provider_connection.json` for real KU GPU inference/native tools, `reports/provider_roles_smoke.json` for the actual Groq baseline and initial Gemini judge smoke, and the complete versioned reports for measured quality. Production promotion, healthy nightly monitoring and cloud deployment require their own genuine evidence.

Provider quota documentation: https://console.groq.com/docs/rate-limits and https://ai.google.dev/gemini-api/docs/rate-limits. Gemini compatible API: https://ai.google.dev/gemini-api/docs/openai.
