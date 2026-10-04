# Historical provider diagnostics

These smoke reports are actual provider/debugging observations, not completed 159-attempt benchmarks or promotion evidence. Frozen reference labels and thresholds were not changed.

- `provider_21_failure_diagnostic.json`, `provider_21_native_protocol_smoke.json` and `provider_22_medium_smoke.json` diagnose native transport behavior and availability.
- `provider_23_structured_smoke.json` records an abandoned schema-constrained transport prototype. Its failing requests are retained; that adapter is not part of the runtime.
- `provider_candidate_20b_smoke.json` and `provider_candidate_llama_quota.json` are bounded candidate checks.
- `gemini_lite_current_quota.json` and `gemini_lite_semantic_smoke.json` record the unavailable Gemini Lite candidate; they are not quality results.
- `groq_qwen_semantic_smoke.json` is a three-case development-only candidate check; one case passed.
- `groq_individual_accounts_models.json`, `groq_all_accounts_native_smoke.json` and `groq_v31_account_diagnostic.json` record the supplied-account listings, native replay and sanitized diagnostics. Tiny successful requests do not establish full-cohort capacity. The interrupted v31 evidence remains unchanged.

Completed native-judged configurations are listed exclusively in `completed_experiments.md`. Development preflights are marked in their manifests and MLflow tags; original failures remain available.
