#!/usr/bin/env bash
set -euo pipefail
: "${VLLM_API_KEY:?Set VLLM_API_KEY before starting the model endpoint}"
cd "$(dirname "$0")"
extra_args=(--max-num-seqs "${VLLM_MAX_NUM_SEQS:-4}")
if [[ -n "${VLLM_QUANTIZATION:-}" ]]; then
  extra_args+=(--quantization "$VLLM_QUANTIZATION")
fi
uv run --locked vllm serve "${VLLM_MODEL:-Qwen/Qwen2.5-7B-Instruct}" \
  --host 0.0.0.0 --port 8002 --api-key "$VLLM_API_KEY" \
  --enable-auto-tool-choice --tool-call-parser hermes \
  --dtype auto --max-model-len "${VLLM_MAX_MODEL_LEN:-8192}" \
  --gpu-memory-utilization "${GPU_UTIL:-0.85}" "${extra_args[@]}"
