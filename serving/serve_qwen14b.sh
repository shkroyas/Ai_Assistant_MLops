#!/usr/bin/env bash
set -euo pipefail
# Set VLLM_MODEL to the AWQ model and VLLM_QUANTIZATION=awq when needed.
export VLLM_MODEL="${VLLM_MODEL:-Qwen/Qwen3-14B-AWQ}"
export VLLM_MAX_MODEL_LEN="${VLLM_MAX_MODEL_LEN:-8192}"
export VLLM_MAX_NUM_SEQS="${VLLM_MAX_NUM_SEQS:-4}"
exec bash "$(dirname "$0")/serve_vllm.sh"
