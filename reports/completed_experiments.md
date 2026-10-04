# Completed live experiments

35 development and 18 frozen golden questions, each repeated three times. The CSV records the selected agent model per configuration; The CSV also records each judge model from its actual MLflow parameters. GPT-OSS agents and judges share a family, and equal model names share weights; separate calls are not independent-model validation. Only versions with completed native judge reports are shown. All MLflow runs, including interrupted and agent-only phases, remain in mlflow_comparison.csv.

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
| v15 | 60.00% | 38.89% | 22.22% | 22.22% | 1332.15 | 13.73s | REJECT |
| v17 | 98.10% | 87.04% | 79.63% | 79.63% | 1842.15 | 26.90s | REJECT |
| v18 | 98.10% | 96.30% | 85.19% | 85.19% | 2280.06 | 27.77s | REJECT |
| v19 | 97.14% | 59.26% | 40.74% | 40.74% | 2055.54 | 27.04s | REJECT |
| v20 | 80.95% | 83.33% | 70.37% | 66.67% | 1719.63 | 25.36s | REJECT |
| v21 | 81.90% | 81.48% | 66.67% | 64.81% | 1902.38 | 25.90s | REJECT |
| v22 | 90.48% | 46.30% | 29.63% | 27.78% | 2300.47 | 27.06s | REJECT |
| v25 | 61.90% | 62.96% | 64.81% | 53.70% | 3810.77 | 5.12s | REJECT |
| v32 | 92.38% | 100.00% | 77.78% | 77.78% | 3908.69 | 3.60s | REJECT |
| v34 | 94.29% | 100.00% | 81.48% | 81.48% | 3906.07 | 3.21s | PROMOTE |

Ground-truth floor: 85%; judge floor: 80%. A cost reduction cannot compensate for failing quality or safety checks.
v14 exhausted its local quota budget during golden evaluation: 31/54 golden traces terminated provider_unavailable. Its aggregate golden rates include those failures and cannot isolate model quality. See [infrastructure audit](v14/infrastructure_audit.json).
v15 encountered Qwen daily quota exhaustion during development and cannot isolate model quality. Its original failed samples remain in the reports.

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
- v15: MLflow run `fa60fa3309404c0c80833afc917b538f`; [native judge report](v15/evidently_judge.html).
- v17: MLflow run `2904abc29c1a4e85b40882613f491682`; [native judge report](v17/evidently_judge.html).
- v18: MLflow run `4e623928952f4a67a2835227db278bf2`; [native judge report](v18/evidently_judge.html).
- v19: MLflow run `a3662fb77e8744fba9d04332798f7aff`; [native judge report](v19/evidently_judge.html).
- v20: MLflow run `4302fb7ebe664cfcad4cf755d6064bae`; [native judge report](v20/evidently_judge.html).
- v21: MLflow run `3438467e8c684bc295d552648f854f64`; [native judge report](v21/evidently_judge.html).
- v22: MLflow run `8d59b068ffbd44eaaebbf9330d1c658c`; [native judge report](v22/evidently_judge.html).
- v25: MLflow run `693b0d2933374fe5adde011cff2ee55a`; [native judge report](v25/evidently_judge.html).
- v32: MLflow run `638c9fc3ae8e41d3b73fcbab6631cf4d`; [native judge report](v32/evidently_judge.html).
- v34: MLflow run `1e0bc9bd432a426ca5c4e5e76e127490`; [native judge report](v34/evidently_judge.html).
