# Week 17 submission report — Task B: Agentic Assistant MLOps

Author: Royas Shakya. Handoff audit: 2026-10-04. This standalone project implements the W15 assistant, W16 verification agent and W17 configuration MLOps. It was built from the assignment PDFs and the implementation plan without reusing existing workspace projects or scaffolds. Task A remains an independent repository.

[Task B README](../README.md) · [Task A README](https://github.com/shkroyas/w17-trackA-churn-mlops#readme) · [Task A detailed report](https://github.com/shkroyas/w17-trackA-churn-mlops/blob/main/docs/week17-submission-report.md) · [Task B final release](https://github.com/shkroyas/Ai_Assistant_MLops/releases/tag/w17-trackB-final)

A [complete file inventory](deliverable-manifest.tsv) lists every committed deliverable with byte size and SHA-256. The inventory excludes itself to avoid a recursive checksum.

## Submission and file map

Submit **https://github.com/shkroyas/Ai_Assistant_MLops** as Task B. The implementation release is `w17-trackB-final`; W15/W16 tags are also retained. Documentation handoff commits do not move those implementation tags. Locations below are relative to this repository. Download HTML reports and open locally rather than expecting GitHub's source viewer to execute them.

| Deliverable | Location | What it establishes |
|---|---|---|
| Assessed write-ups | [README](../README.md) | W15, W16 sections and W17 a–d, with architecture |
| Application environment | [pyproject.toml](../pyproject.toml), [uv.lock](../uv.lock), `.python-version` | Locked Python 3.12 application and tests |
| GPU environment | [serving/pyproject.toml](../serving/pyproject.toml), [serving/uv.lock](../serving/uv.lock), [Qwen3 startup](../serving/serve_qwen14b.sh) | Separate vLLM serving setup |
| W15 baseline | [rag.py](../src/assistant_mlops/rag.py), [provider.py](../src/assistant_mlops/provider.py) | Single-pass `/rag`, asynchronous provider calls, retries/fallback |
| W16 agent and schemas | [agent.py](../src/assistant_mlops/agent.py), [schemas.py](../src/assistant_mlops/schemas.py) | Native model-selected tools, bounded loop, validated final status/citations |
| Retrieval | [retrieval.py](../src/assistant_mlops/retrieval.py), [semantic retrieval report](semantic-retrieval.md), `corpus/` | Qdrant, chunking, lexical baseline and pinned semantic production embeddings |
| Product/API | [api.py](../src/assistant_mlops/api.py), [ui.py](../src/assistant_mlops/ui.py), [auth.py](../src/assistant_mlops/auth.py) | FastAPI, Streamlit, admission, batch, cache and proxy authentication |
| Evaluation source/data | [harness.py](../src/assistant_mlops/harness.py), [dataset card](../datasets/README.md), [dev](../datasets/dev_v1.jsonl), [golden](../datasets/golden_v1.jsonl) | Scratch harness, 35 development and 18 frozen regression cases |
| Calibration and delegated approval | [labels](../datasets/judge_calibration_v1.jsonl), [review record](../datasets/calibration_review.json), [120B calibration](../reports/judge_calibration_groq120/calibration.json) | 15 labels, approval tied to SHA, agreement and false passes |
| Prompts and configurations | `prompts/prompt_v*.md`, `configs/v*.yaml`, [v34](../configs/v34.yaml), [production](../configs/production.yaml), [gate rules](../configs/gate.yaml) | Versioned experimental treatments and explicit promotion |
| Trace-driven decisions | `reports/diagnosis_v*.json`, `reports/v*/dev/trace_*.json` | Actual preceding development failure and stated revision axis |
| MLflow integration | [experiment.py](../src/assistant_mlops/experiment.py), [comparison](../reports/mlflow_comparison.md) | Parameters, metrics, raw trajectories, nested spans, artifacts and run identities |
| Complete-run comparison | [table](../reports/completed_experiments.md), [CSV](../reports/completed_experiments.csv), [chart](../reports/cost_quality.png) | All 23 completed native-judged configurations; tokens versus quality |
| Native Evidently implementation | [regression.py](../src/assistant_mlops/regression.py), [gate.py](../src/assistant_mlops/gate.py) | Reference-based correctness/completeness tests and promotion gate |
| Current regression reports | [native judge HTML](../reports/v34/evidently_judge.html), [ground-truth HTML](../reports/v34/evidently_ground_truth.html), [verdict CSV](../reports/v34/judge_verdicts.csv), [metrics](../reports/v34/metrics.json), [gate](../reports/v34/gate.json) | Actual v34 responses, judge reasons, results and all-PASS decision |
| Full current trajectories | `reports/v34/dev/`, `reports/v34/golden/`, `reports/v34/runtime/` | 105 dev and 54 golden traces plus actual system prompt/tools |
| Rejected and partial work | `reports/v*/`, `reports/v33_preflight/`, `partial_manifest.json` where present | Preserved failures, interruptions and preflights, excluded from complete-run count |
| Airflow bonus | [DAG](../dags/assistant_regression.py), [nightly.py](../src/assistant_mlops/nightly.py), [healthy states](../reports/airflow_healthy_states.json), [infra states](../reports/airflow_infra_states.json), [nightly status](../reports/nightly/status.json) | Real healthy inference and deliberately unavailable endpoint branches |
| Screenshots | [manifest](../reports/screenshots/manifest.json), `reports/screenshots/*.png` | Seven real screenshots matching production v34; older captures are archived separately |
| API/container proof | [API features](../reports/api_features_smoke.json), [deployment smoke](../reports/deployment_smoke.json), [compose](../compose.yaml), `Dockerfile`, `Dockerfile.airflow` | Actual cache/concurrency/batch and container infrastructure |
| Verification | [scorecard](../reports/deliverables.md), `tests/`, [CI](../.github/workflows/ci.yml) | Recorded 31/31 core checks; 78 engineering tests; credential-free CI |
| Provider/session/cloud handoff | [allocation](provider-allocation.md), [setup](provider-setup.md), [runtime](evaluation-runtime.md), [Qwen3 session](qwen14b-session.md), [cloud](../deploy/cloud.md) | Model roles, quota/transport handling and deployment prerequisites |

## W15 foundation and W16 feature

The eight authored handbook Markdown sources describe a fictional company's MLOps policies. The assistant does not claim access to an actual organization's policies. Ingestion supports Markdown, text and PDF, with 900-character chunks and 150-character overlap. W15 `/rag` makes one application-selected retrieval and one completion. W16 `/ask` lets one agent choose searches, source reads, clarification and termination based on intermediate evidence. Qdrant retrieval and model endpoints are bounded services; neither is an independent collaborating agent.

Production allows seven model iterations, at most four tools per iteration and top-k three retrieval. Final JSON reports `answered`, `abstain` or `clarify`, with exact retrieved quotations and source IDs. Native final submission, nullable search filters and bounded review of answered responses address observed protocol and factual failures. Review is a bounded stage in the same agent, rather than a second autonomous agent.

Older tool outputs are shortened in model context while complete raw results remain in external traces. Context compaction creates bounded per-source notes and preserves valid native tool/result pairs. Compaction can lose caveats, so the agent can read a source again and answer validation/harness results remain necessary.

The API applies four concurrent model slots, 30 queries per client per minute, a 300-second/128-entry LRU cache, and a maximum batch of eight. Cache identity includes corpus, prompt, configuration and provider. Concurrent identical questions share one computation. Infrastructure errors are not cached as successful answers. Cache/rate limits are process-local; a multi-worker cloud deployment needs shared enforcement. The production API smoke test passed all six checks, including one computation for concurrent identical requests and no additional model tokens for a cached answer.

## a. Environment and reproducibility

The app pins MLflow 2.22.2, SQLAlchemy 2.0.41, Evidently[llm] 0.7.23, CPU torch 2.7.0, transformers 4.51.3, sentence-transformers 4.1.0, Qdrant client 1.14.2, FastAPI 0.115.12 and Streamlit 1.45.1. uv fixes direct/transitive versions; CI pins uv 0.12.13. SQLAlchemy's pin resolves the observed MLflow pool-class incompatibility. CPU torch avoids a CUDA installation on the application laptop. `serving/uv.lock` isolates vLLM 0.8.5 and GPU requirements. Airflow invokes the app's isolated environment inside its container.

```bash
uv sync --locked
# Create .env only on a new clone; preserve an existing credential file.
test -f .env || cp .env.example .env
# Set private Qwen endpoint/authentication and Groq judge values as described below.
docker compose up -d --build backend ui mlflow
```

`uv sync --locked` reproduces the environment in one command. Real inference also needs a reachable model server, credentials and initial model downloads. The template's Gemini agent defaults are alternatives, not the endpoint for promoted v34. For production, set `AGENT_BASE_URL` to the actual authenticated Qwen3 `/v1` endpoint, `AGENT_MODEL=Qwen/Qwen3-14B-AWQ`, and `AGENT_API_KEY` privately. Use proxy token/cookie only if the session needs them. Leave `ASSISTANT_CONFIG` empty. For v34 native evaluation use `JUDGE_PROVIDER=groq`, `JUDGE_MODEL=openai/gpt-oss-120b` and a private `JUDGE_API_KEY`; preserve required pacing. The API does not require judge calls to answer ordinary questions.

For a development Gemini alternative, explicitly set `ASSISTANT_CONFIG=configs/v1.yaml` and the compatible Gemini endpoint/model/key. That override neither reproduces v34 behavior nor promotes v1. Current services use UI localhost:18501, API localhost:8000, MLflow localhost:5000 and Airflow localhost:8080; default UI port is 8501. Services are local development containers. A restarted GPU session requires updated credentials, connection verification and backend recreation.

Clean clones do not contain original MLflow databases or provider secrets. Exported evidence remains usable offline. The production-baseline helper can use matching committed metrics and an all-PASS gate when the recorded MLflow run is absent; it checks the run identity and gate, and does not invent a new historical run. New evaluations receive new UUIDs. Preserve original reports and use a fresh candidate version for new experiments rather than overwriting published evidence.

## b. Tracking strategy, experiment history and decisions

Each full configuration executes **35 development cases ×3 +18 golden cases ×3 =159 agent attempts**, plus separate native judge requests. MLflow records configuration, prompt/corpus hashes, raw tool arguments/results, visible intermediate decisions, iteration/termination reason, latency and provider-reported usage. Visible decision summaries are evidence of actions, not a claim to expose private model reasoning. Representative success/failure trajectories, native spans and complete trace directories are artifacts. The harness also checks required facts, sources, valid tool arguments, budgets and persistent failure injection.

Prompts were revised from development traces. For example, v2 addresses v1's prose instead of required JSON, citing `reports/v1/dev/trace_dev-01_r0.json`; v3 addresses guessed source filters and unrelated searches from the corresponding v2 trace. v4 changes only the iteration cap from seven to four to measure cost. It used **1,566.69** tokens/query versus v3's **1,727.01**, a **9.28% reduction**, while both retained **57.41%** golden truth. Both failed the quality gate; cheaper execution alone never permits promotion.

| Stage | Models/tools used | Decision and evidence |
|---|---|---|
| v1–v12 | GPU Qwen2.5-7B, native 20B judge | JSON, evidence selection, caveats and loop revisions; completed results remain REJECT |
| v13–v15 | Groq Qwen3.8-27B | Availability interruptions and model trade-offs; v13 partial, v14/v15 completed but REJECT |
| v16–v19 | Groq GPT-OSS-120B agent | Stronger dev results, but quality/availability issues; v16 partial; v18's incomplete usage blocks promotion despite passing quality floors |
| v20–v22 | Groq GPT-OSS-20B agent | Lower model cost option; insufficient regression quality; same-family judge is a disclosed validation limitation |
| v23–v24 | Gemini 2.5 Flash / Groq 120B attempts | Quota/availability interruptions; partial evidence preserved, never counted as complete |
| v25 | GPU Qwen2.5-7B with calibrated 120B judge | Full no-error run, but 62.96% truth and 64.81% joint judge; REJECT |
| v26–v30 | Development-only retrieval/review/prompt work | Pinned semantic embeddings, bounded answer review, preservation of negation and supersession; preflights are not full benchmarks |
| v31 | Groq 120B with five authorized accounts | Daily quota observations, queue defect and user-requested GPU restart; interrupted, preserved and excluded |
| v32 | GPU Qwen3-14B-AWQ, 20B judge | Full truth 100%, joint judge 77.78%; REJECT |
| v33 | Prompt-only development proposal | 9/12 preflight cases passed; policy inversion observed; abandoned |
| v34 | Same v32 agent, calibrated 120B judge | Fresh full cohort; all checks PASS; explicit promotion |

There are **23 completed native-judged configurations**, not 34: v1–v12, v14, v15, v17–v22, v25, v32 and v34. Partial/interrupted runs and preflights remain visible separately. The complete comparison CSV provides every run UUID, model, judge identity, metric and gate.

Early retrieval used normalized 512-dimensional hashing embeddings, a lightweight lexical baseline. Production uses normalized **384-dimensional MiniLM embeddings**, pinned to revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, on CPU. Semantic retrieval addresses development paraphrase recall; the cache fingerprint includes corpus/model/revision. Model and retrieval changes were evaluated rather than presumed beneficial.

The supplied five Groq accounts were explicitly authorized for paced pooling. The implementation respects per-account limits, header/body cooldowns and bounded retries; it does not bypass quota limits. An observed scheduling defect incorrectly cascaded failures while other accounts were busy; queue waiting was fixed and regression-tested. Gemini keys were retained as alternatives; their quotas did not support uninterrupted full evaluation. v24's original exact HTTP quota scope was not recorded, so its interruption is reported without claiming a proven daily limit. Later corrections preserve the original evidence and add provenance instead of silently rewriting history.

Royas supplied the restarted GPU session. The actual endpoint identified **Qwen/Qwen3-14B-AWQ**, and native tools/usage were verified. Serving instructions use Hermes tool parsing and non-thinking mode with the separate vLLM lock. AWQ is the memory-saving checkpoint choice; no isolated quantization benefit, throughput improvement or exact GPU memory fit is claimed.

### Final production result

Production config: **v34**, prompt `prompts/prompt_v30.md`, MLflow run **`1e0bc9bd432a426ca5c4e5e76e127490`**.

| Signal | Actual result |
|---|---:|
| Development task completion | 99/105 = **94.29%** |
| Frozen golden ground truth | 54/54 = **100%** |
| Native reference correctness | 51/54 = **94.44%** |
| Native completeness | 44/54 = **81.48%** |
| Joint native judge pass | 44/54 = **81.48%** |
| Tool-call correctness | **97.30%** |
| Mean development tokens/query | **3,906.07** |
| Mean development latency | **3.208 seconds** |
| Mean trajectory iterations | **2.314** |
| Usage coverage / injected failure safety | **100% / 100%** |
| Hard failures / golden provider failures | **0% / 0%** |
| Repeated-run completion spread | **0** |

v34 returned to the v32 agent settings and changed only the judge relative to that baseline. Fresh agent responses also vary. Moving from a 20B to a 120B judge **does not demonstrate agent improvement**; it changes the measurement. Both judges were calibrated against the same small reviewed set, and v32's REJECT remains intact. Frozen references, labels, native criteria and gate thresholds were not lowered or relabeled to obtain promotion.

Dollar cost is **unknown**, because billing rates were not supplied. The chart uses reported tokens as a cost proxy. Judge tokens/cost are additional to the development mean. Latencies include the actual endpoint/provider pacing, so cross-provider comparisons are not controlled hardware benchmarks.

## c. Native Evidently monitoring and judge sanity check

The golden file supplies approved corpus-grounded reference responses. Native `LLMEval` descriptors use `BinaryClassificationPromptTemplate` for correctness and completeness. `Report(include_tests=True)` adds native category-share tests ≥0.80 for both descriptors. Unknown verdicts fail. Ground truth, joint judge and their conjunction are logged separately; deterministic keyword/source checks can penalize valid paraphrases, while the judge can also misinterpret a short reference.

Calibration contains **15 cases: eight positive, seven negative**. The assistant drafted/audited labels, and Royas explicitly delegated and approved the review. The review JSON records this method and matching label SHA; it does not claim individual human annotations. Current 120B calibration agreement is **15/15**, with zero false passes. This small, non-independent review is a limitation, not proof of universal judge reliability.

All ten joint failures remain in `reports/v34/judge_verdicts.csv`. For example, `gold-04` repeat 0 correctly distinguishes drift from promotion, but the judge penalizes extra drift thresholds absent from the short reference; `gold-08` repeat 0 correctly names release-policy supersession, but completeness penalizes added promotion conditions. These show the native judge's strict reference interpretation. Its decisions were retained rather than overridden. Overall judge/truth agreement is **81.48%**. Reading response plus reasoning is necessary to distinguish real regressions from measurement limitations.

Promotion requires truth ≥85%, joint judge ≥80%, calibration ≥80% with matching owner-approved review, judge/truth agreement ≥75%, tool correctness ≥90%, hard failures ≤5%, safe injected failures and complete usage. With a baseline, completion, truth, tokens and steps also obey the fixed relative limits documented in the README/gate config. Only an explicit successful promotion updates `configs/production.yaml`. The API selects that configuration at startup; nightly monitoring never promotes.

## d. Airflow bonus and production monitoring

`assistant_nightly_regression` is scheduled at **02:00 UTC daily (07:45 Nepal)**, with the validated DAG unpaused. `/models` health selects either regression or a visible infrastructure-failure branch. Healthy monitoring runs the 18-case frozen set with deterministic ground-truth checks and no paid judge. The degradation threshold is `max(0.85, production_truth−0.05)`, currently **0.95**; unsafe injection or excessive hard failures also fail it.

Actual healthy DAG evidence shows `endpoint_health=success`, `regression=success`, `infrastructure_failure=skipped`; **18/18 cases passed**. Nightly MLflow run is `c7265a8a8ebb4267b64d302ea253a06c`, tied to the v34 production UUID. The deliberately unavailable port-9 test shows `endpoint_health=success`, `regression=skipped`, `infrastructure_failure=failed`. The health task succeeds because the branch decision executed; it does not mean the endpoint was reachable. This intentional failed DAG demonstrates outage handling.

Both are actual native Airflow test executions. A scheduled DAG and one healthy run do not establish long-term uptime. The UI's logical run timestamp can inflate displayed DAG duration; it is not a GPU latency benchmark. Airflow standalone is a local development deployment, not a cloud production scheduler. Seven production screenshots include both native Evidently tests and both Airflow branches; the older v25 captures are archived with their separate provenance.

## Repository management and remaining deployment work

GitHub has protected `main`, required `ci`, PR-only changes, linear history, squash-only merge, automatic feature-branch deletion and blocked force pushes/main deletion. Zero required approving reviews supports solo development. The completed W17 milestone and final release preserve the submission. At audit there were no open PRs or leftover remote feature branches; the only open issue was **#3, optional cloud deployment**, requiring a target and resource budget. This documentation uses a separate PR and leaves final implementation tags unchanged.

**31/31 core checks and 78 engineering tests** pass in the recorded delivery. CI runs locked setup, Ruff, tests and the static scorecard without paid provider credentials. That static check proves implementation presence; committed live reports establish experiments, judge evaluation, production and Airflow. The archive deliberately retains failed/partial experiments because reproducible decision history is an assessed deliverable.

At the original submission audit, cloud deployment was pending. The later temporary Azure deployment is verified in the follow-up below; no GPU VM or cloud Airflow scheduler is used. Keep secrets out of Git and archives; use cloud secret storage, authenticated HTTPS, persistent MLflow metadata/artifacts, backups and fresh real-query/concurrency checks. Separate GPU inference from application hosting. Model/tunnel availability, small evaluation size, overlapping dev/golden facts, process-local admission and judge bias remain practical limitations to address before relying on this as a public service.


## Post-submission temporary Azure demo preparation

The owner requested a short cloud demonstration, authorized US$5 and four hours, and supplied an Azure for Students subscription. Azure device authentication succeeded. Qwen access remains HTTPS through the authenticated Jupyter server proxy; SSH tunneling is unnecessary. This follow-up does not change the assignment’s original measured results, gates or immutable release tag.

The [Azure deployment guide](azure-demo.md) explains the added wrapper image, authenticated Nginx routes, actual FastAPI/MLflow services, independent runtime stores and scoped scheduled resource-group cleanup. Task A runs its actual pipeline at startup. Task B's wrapper copies the approved v34 configuration and prompts over the older base image, which otherwise selected v1. Local checks establish gateway operation; they do not establish a public Azure deployment. The real provider preflight confirms Qwen3-14B-AWQ supports completions and native tools through the refreshed proxy authentication. The corrected v34 local gateway also completed a sourced query and zero-new-token cached reuse.

Azure setup encountered region policy restrictions, Express-environment incompatibility with scheduled jobs, a transient job creation failure, environment quota errors during pending deletion, and a failed cleanup execution precondition. The launcher now explicitly requests WorkloadProfiles with Consumption only, uses stable ARM job APIs, waits for explicit provisioning success, handles asynchronous execution responses, and rounds the UTC expiration down to match the scheduled cron minute. Application launch remains gated on a successful managed-identity cleanup preflight. Failed attempts request deletion of only their isolated resource groups. Pending deletion can continue holding the subscription's single-environment quota; do not infer cleanup completion from an accepted request.

Task A's existing four tests and Task B's existing 78 tests passed again. Two additional Task B deployment tests cover cleanup failure gating, ownership checks and exact deadline alignment. Deployment Python is included in CI. The later Azure deployment passed the cleanup preflight and both applications were created. Actual Task A public prediction/invalid-input checks passed. Task B initially encountered blocked Jupyter proxy access; its real safe-abstention response is preserved separately. Browser loading exposed a WebSocket origin issue, fixed by explicitly forwarding Host in the Nginx upgrade location. The final report files are copied into the Task B wrapper to prevent older base-image evidence from replacing the current submission. The owner subsequently refreshed proxy credentials. Task B restarted with those values and passed actual public sourced Qwen inference and zero-new-token cache reuse; the original outage evidence remains retained. The complete 9-minute-32-second narration includes actual local services and successful Azure browser footage, delivered separately in the workspace video folder with captions, transcript, chapter index and checksum; combined footage remains private because it includes Task A's private project.

The final cloud evidence is in `reports/cloud_demo/azure_deployment.json` and `azure_https_smoke.json`. Both applications passed authenticated HTTPS checks, with anonymous access rejected. Task B also passed an actual Streamlit browser query after the Host forwarding fix. The fixed resource-group deletion deadline is **2026-10-04 11:15 UTC / 17:00 Nepal**. The conservative four-hour estimate is **US$2.52**; it is not an invoice or enforceable spending cap. Scheduled deletion has not yet executed at this report time. Original final tags and submission archives remain unchanged.
