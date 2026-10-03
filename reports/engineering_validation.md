# Local verification evidence

Executed on 2026-10-03, from independent fresh source implementations.

- Assistant: 26 pytest tests passed; no live LLM quality claim.
- Native Evidently correctness/completeness report integration tested with stubbed descriptors; those reports are test plumbing evidence, not judge verdicts.
- W15 single-pass RAG, W16 cross-source multi-step loop, citation rejection, step bounds, timeout/malformed/unavailable retrieval, provider retry/fallback, cache coalescing, and rate limiting tested.
- Both application Docker images built successfully; Compose configurations validate. The UI/backend deployment smoke passed on ports 18501/8000; without credentials, the backend safely abstains.
- Actual Airflow unavailable-endpoint branch failed as expected and skipped regression (airflow_infra.txt).
- Live experiments, human calibration review, GPU/model serving, healthy nightly evaluation, and cloud deployment remain pending external resources.

A post-integration fix preserves SQLite tracking when .env contains an empty URI and records cost as unknown when a provider supplies total tokens without the input/output split. The regression test prevents a false zero-cost report.

Proxy authentication is endpoint-specific. A regression test verifies cookie normalization, token authorization, and that primary credentials never reach a fallback provider.

Live evaluation runtime adds checkpoint resume/input validation, quota backoff without key rotation, authentication-only Groq reserve failover, and native synchronous Evidently judgment caching. The independent Groq judge smoke correctly passed a matching answer and rejected a contradiction.
