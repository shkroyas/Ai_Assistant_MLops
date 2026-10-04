# Qwen3 14B GPU session — prepared, not executed

Task B is paused while Royas restarts the GPU session. `configs/v32.yaml` selects
`Qwen/Qwen3-14B-AWQ`, an official quantized 14B checkpoint, as the memory-saving
default. This configuration has no measured quality result or production promotion.
The exact GPU VRAM and available memory must be checked in the new session.

## Start the server in the GPU session

Use Python 3.12 and the existing pinned `serving/uv.lock` (vLLM 0.8.5). Run
`nvidia-smi` first. Set `VLLM_API_KEY` privately to the bearer key you choose, then:

```bash
export VLLM_MODEL=Qwen/Qwen3-14B-AWQ
export VLLM_MAX_MODEL_LEN=8192
export VLLM_MAX_NUM_SEQS=4
export GPU_UTIL=0.85
bash serving/serve_qwen14b.sh
```

The server listens on port **8002** and exposes `/v1`. Native tools use
`--enable-auto-tool-choice --tool-call-parser hermes`. The client explicitly sends
`chat_template_kwargs: {enable_thinking: false}` for this candidate. Do not add
`--enable-reasoning` or a reasoning parser to this vLLM 0.8.5 non-thinking setup:
Qwen documents an incompatibility between that parser and the non-thinking switch.
This keeps the bounded tool loop's existing completion budget and structured final
submission; thinking mode would be a separately evaluated configuration.

For full precision, use `VLLM_MODEL=Qwen/Qwen3-14B` only after confirming sufficient
VRAM for weights, runtime and KV cache. Also change `model` in `configs/v32.yaml`
and `AGENT_MODEL` to that exact ID before any v32 evaluation. If startup runs out
of memory, reduce `VLLM_MAX_NUM_SEQS` to 1 and/or `VLLM_MAX_MODEL_LEN` to 4096,
then verify that the actual agent context fits; do not assume a 14B checkpoint fits
the old GPU just because the previous 7B checkpoint did.

## Connect this workspace

After starting the new session, update only the ignored, mode-0600 root `.env`:

```dotenv
AGENT_BASE_URL=https://YOUR-NEW-HOST/proxy/8002/v1
AGENT_MODEL=Qwen/Qwen3-14B-AWQ
AGENT_API_KEY=YOUR-VLLM-BEARER-KEY
AGENT_PROXY_TOKEN=YOUR-NEW-JUPYTER-TOKEN
AGENT_PROXY_COOKIE=YOUR-NEW-COOKIE
```

Use the actual proxy path, not this example. For a direct/tunnel vLLM endpoint,
use `https://YOUR-HOST/v1` and leave both proxy fields empty. The current proxy
adapter uses `Authorization: token …` for Jupyter authentication when a proxy
token is set; otherwise it uses the vLLM bearer key. If the proxy also requires
independent upstream bearer authentication, its forwarding behavior must be
verified in the connection check. Keep the existing Groq/Gemini credentials for
judging. Do not paste credentials into YAML, reports or committed examples.

Leave `ASSISTANT_CONFIG` at its current value while the endpoint is unverified.
After checks pass, `ASSISTANT_CONFIG=configs/v32.yaml` selects this candidate for
development use; it does not promote it. Docker services need recreation to load
new environment values.

## Verify before continuing the assignment

```bash
.venv/bin/python scripts/check_provider.py --config configs/v32.yaml \
  --output reports/qwen3_14b_connection.json
```

This checks the exact `/models` ID, an actual completion with reported usage and
native retrieval tool calls. It preserves the earlier 7B connection evidence.
Next run a development-only preflight through the actual Agent, including native
final JSON, citations, safe refusal and injected retrieval failure. Only after the
preflight passes should the full 159-attempt cohort and both native judge criteria
run:

```bash
.venv/bin/python -m assistant_mlops.experiment run --config configs/v32.yaml \
  --diagnosis reports/diagnosis_v32.json --judge
```

The prepared diagnosis cites an original v31 development failure. All references,
labels and promotion thresholds remain unchanged. Failed prior samples remain
preserved. A model or endpoint change invalidates old checkpoints.

Sources: [Qwen vLLM deployment and non-thinking mode](https://qwen.readthedocs.io/en/stable/deployment/vllm.html),
[Qwen native function calling](https://qwen.readthedocs.io/en/stable/framework/function_call.html),
[official Qwen3-14B-AWQ checkpoint](https://huggingface.co/Qwen/Qwen3-14B-AWQ).
