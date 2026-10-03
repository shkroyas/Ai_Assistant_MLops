# Completed live experiments

35 development and 18 frozen golden questions, each repeated three times. Agents: KU Qwen2.5-7B (v1–v12), Groq Qwen3.8-27B (v14); independent judge: Groq GPT-OSS-20B. Only versions with completed native judge reports are shown. All MLflow runs, including interrupted and agent-only phases, remain in mlflow_comparison.csv.

| Version | Dev completion | Golden truth | Judge | Both | Dev tokens/query | Dev latency | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
| v1 | 47.62% | 44.44% | 48.15% | 35.19% | 4197.86 | 5.17s | REJECT |
| v2 | 48.57% | 48.15% | 37.04% | 20.37% | 2898.30 | 3.04s | REJECT |
| v3 | 50.48% | 57.41% | 42.59% | 33.33% | 1727.01 | 1.46s | REJECT |
| v4 | 51.43% | 57.41% | 42.59% | 35.19% | 1566.69 | 1.33s | REJECT |
| v5 | 66.67% | 72.22% | 50.00% | 40.74% | 2972.55 | 2.21s | REJECT |
| v6 | 56.19% | 62.96% | 40.74% | 33.33% | 2620.09 | 1.66s | REJECT |
| v7 | 58.10% | 62.96% | 48.15% | 31.48% | 2207.19 | 1.45s | REJECT |
| v8 | 51.43% | 64.81% | 46.30% | 40.74% | 2713.91 | 1.60s | REJECT |
| v9 | 64.76% | 68.52% | 57.41% | 51.85% | 4368.09 | 8.02s | REJECT |
| v10 | 68.57% | 68.52% | 57.41% | 50.00% | 4082.24 | 7.39s | REJECT |
| v11 | 65.71% | 62.96% | 59.26% | 46.30% | 5926.12 | 9.66s | REJECT |
| v12 | 60.95% | 64.81% | 70.37% | 53.70% | 5254.88 | 8.73s | REJECT |
| v14 | 96.19% | 64.81% | 50.00% | 50.00% | 5571.54 | 59.23s | REJECT |

Ground-truth floor: 85%; judge floor: 80%. A cost reduction cannot compensate for failing quality or safety checks.
v14 exhausted its local quota budget during golden evaluation: 31/54 golden traces terminated provider_unavailable. Its aggregate golden rates include those failures and cannot isolate model quality. See [infrastructure audit](v14/infrastructure_audit.json).

- v1: MLflow run `89373de5f91741d18d90078abce1f6f3`; [native judge report](v1/evidently_judge.html).
- v2: MLflow run `458fcb260c5542f8baa4f2ed4eca213a`; [native judge report](v2/evidently_judge.html).
- v3: MLflow run `b252c60fc035477a9e490c487d3c4a4b`; [native judge report](v3/evidently_judge.html).
- v4: MLflow run `c28846db778240f59120fd8c1a0a15a1`; [native judge report](v4/evidently_judge.html).
- v5: MLflow run `9ab535a1fb314ea4be2d97297f2a7715`; [native judge report](v5/evidently_judge.html).
- v6: MLflow run `303cc35407fe4fa49a7a3e98a4b7a574`; [native judge report](v6/evidently_judge.html).
- v7: MLflow run `66a09b3e346446ac991d74fb71b1e9e6`; [native judge report](v7/evidently_judge.html).
- v8: MLflow run `e6bcde8e82864e77956a776125c10ca8`; [native judge report](v8/evidently_judge.html).
- v9: MLflow run `3d7e55fca7654927bbd40b2fc96a90f6`; [native judge report](v9/evidently_judge.html).
- v10: MLflow run `80822374a88c461592acbb2f63012143`; [native judge report](v10/evidently_judge.html).
- v11: MLflow run `0f410b2f48d040628b54c584cb786ed2`; [native judge report](v11/evidently_judge.html).
- v12: MLflow run `b69699e46ee14cbdbcb0e69b8fa154c3`; [native judge report](v12/evidently_judge.html).
- v14: MLflow run `63a3a8e99aa5477085064b4703376371`; [native judge report](v14/evidently_judge.html).
