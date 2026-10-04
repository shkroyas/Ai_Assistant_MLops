# Qwen3-14B-AWQ execution

The user restarted the authenticated GPU/vLLM session and supplied its endpoint credentials in the ignored local `.env`. The connection report verifies the exact model listing, a real completion and native search calls. No fallback model was used.

The nine-case development preflight passed every original case, including safe refusal, clarification, citations, policy reading and injected retrieval failure. The fresh full v32 cohort preserves all 105 development and 54 frozen golden attempts. Development completion was 97/105 (92.38%), tool correctness 97.30%, hard failure 0%, and all 159 attempts had complete actual usage. Golden reference checks passed 54/54. v32 completed native 20B judging at 77.78% and remains REJECT. The v33 prompt preflight was abandoned. Fresh v34 retains the v32 agent setup, passes 54/54 golden checks and 81.48% joint calibrated 120B judge checks, and passes every unchanged gate. Run `1e0bc9bd432a426ca5c4e5e76e127490` is explicitly promoted. Production API features pass and the real Airflow nightly passed 18/18 cases; the port-9 infrastructure branch failed visibly and skipped regression.

Settings: official Qwen3-14B-AWQ, non-thinking mode, seven maximum iterations, pinned MiniLM semantic retrieval with top_k=3, temperature 0.1, top_p 0.9, one bounded self-review of answered drafts. AWQ is part of the selected checkpoint; this run does not isolate the effect of quantization or claim GPU throughput improvement. Price inputs are unset, so reported tokens are a cost proxy and dollar costs remain unknown.

Earlier partial and rejected configurations remain in history. The agent and Groq GPT-OSS-20B judge use different model families; calibration remains the 15 assistant-reviewed labels approved by Royas, with documented small-sample limitations.

Evidence: `qwen3_14b_connection.json`, `qwen3_14b_preflight/result.json`, `v32/dev`, `v32/golden`, and the final native reports once complete.
