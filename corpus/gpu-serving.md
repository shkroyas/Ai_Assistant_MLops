# GPU serving — example deployment choices
The planned primary model is Qwen2.5-7B-Instruct served by vLLM using BF16 on a 24 GB GPU. For a 12 GB slot use an AWQ quantized model. For a cost comparison use Qwen2.5-3B-Instruct. Benchmark actual latency and quality before changing production. ONNX conversion is outside this project because vLLM owns the autoregressive decoding and KV cache.
