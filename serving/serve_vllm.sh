#!/usr/bin/env bash
set -euo pipefail
: "${VLLM_API_KEY:?Set VLLM_API_KEY before starting the model endpoint}"
cd "$(dirname "$0")"
uv run --locked vllm serve "${VLLM_MODEL:-Qwen/Qwen2.5-7B-Instruct}" \
  --host 0.0.0.0 --port 8002 --api-key "$VLLM_API_KEY" \
  --enable-auto-tool-choice --tool-call-parser hermes \
  --dtype auto --max-model-len 8192 --gpu-memory-utilization "${GPU_UTIL:-0.85}"
