# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.6667 |
| tool_call_correctness | 1.0000 |
| tool_argument_validity | 1.0000 |
| trajectory_length_mean | 2.2381 |
| tokens_per_query_mean | 2972.5524 |
| usage_complete | 1.0000 |
| latency_mean | 2.2105 |
| completion_spread | 0.0286 |
| hard_failure_rate | 0.0000 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| dev-01 | 0 | True | 3 | 4215 | — |
| dev-02 | 0 | True | 3 | 4190 | — |
| dev-03 | 0 | True | 3 | 4259 | — |
| dev-04 | 0 | True | 3 | 4233 | — |
| dev-05 | 0 | True | 3 | 4401 | — |
| dev-06 | 0 | False | 4 | 6086 | soft_failure |
| dev-07 | 0 | False | 4 | 6297 | soft_failure |
| dev-08 | 0 | False | 4 | 6474 | soft_failure |
| dev-09 | 0 | False | 1 | 1065 | soft_failure |
| dev-10 | 0 | True | 4 | 6172 | — |
| dev-11 | 0 | False | 4 | 6218 | soft_failure |
| dev-12 | 0 | False | 3 | 4308 | soft_failure |
| dev-13 | 0 | False | 1 | 1062 | soft_failure |
| dev-14 | 0 | False | 3 | 4327 | soft_failure |
| dev-15 | 0 | False | 1 | 1057 | soft_failure |
| dev-16 | 0 | True | 1 | 1049 | — |
| dev-17 | 0 | True | 4 | 6255 | — |
| dev-18 | 0 | True | 1 | 1051 | — |
| dev-19 | 0 | True | 1 | 1050 | — |
| dev-20 | 0 | True | 1 | 1050 | — |
| dev-21 | 0 | True | 1 | 1051 | — |
| dev-22 | 0 | False | 1 | 1050 | soft_failure |
| dev-23 | 0 | True | 1 | 1050 | — |
| dev-24 | 0 | False | 1 | 1046 | soft_failure |
| dev-25 | 0 | True | 1 | 1054 | — |
| dev-26 | 0 | True | 1 | 1050 | — |
| dev-27 | 0 | True | 1 | 1051 | — |
| dev-28 | 0 | True | 1 | 1057 | — |
| dev-29 | 0 | True | 1 | 1060 | — |
| dev-30 | 0 | True | 1 | 1053 | — |
| dev-31 | 0 | True | 4 | 4661 | — |
| dev-32 | 0 | True | 4 | 4656 | — |
| dev-33 | 0 | True | 1 | 1052 | — |
| dev-34 | 0 | True | 4 | 4730 | — |
| dev-35 | 0 | True | 4 | 4757 | — |
| dev-01 | 1 | True | 3 | 4217 | — |
| dev-02 | 1 | True | 3 | 4186 | — |
| dev-03 | 1 | True | 3 | 4259 | — |
| dev-04 | 1 | True | 3 | 4235 | — |
| dev-05 | 1 | True | 3 | 4401 | — |
| dev-06 | 1 | False | 4 | 6184 | soft_failure |
| dev-07 | 1 | False | 4 | 6382 | soft_failure |
| dev-08 | 1 | False | 4 | 6474 | soft_failure |
| dev-09 | 1 | False | 1 | 1065 | soft_failure |
| dev-10 | 1 | False | 4 | 6301 | soft_failure |
| dev-11 | 1 | False | 4 | 6222 | soft_failure |
| dev-12 | 1 | False | 3 | 4308 | soft_failure |
| dev-13 | 1 | False | 1 | 1062 | soft_failure |
| dev-14 | 1 | False | 3 | 4327 | soft_failure |
| dev-15 | 1 | False | 1 | 1057 | soft_failure |
| dev-16 | 1 | True | 1 | 1049 | — |
| dev-17 | 1 | True | 1 | 1050 | — |
| dev-18 | 1 | True | 1 | 1051 | — |
| dev-19 | 1 | True | 1 | 1050 | — |
| dev-20 | 1 | True | 1 | 1050 | — |
| dev-21 | 1 | True | 1 | 1051 | — |
| dev-22 | 1 | False | 1 | 1050 | soft_failure |
| dev-23 | 1 | True | 1 | 1050 | — |
| dev-24 | 1 | False | 1 | 1046 | soft_failure |
| dev-25 | 1 | True | 1 | 1054 | — |
| dev-26 | 1 | True | 1 | 1050 | — |
| dev-27 | 1 | True | 1 | 1051 | — |
| dev-28 | 1 | True | 1 | 1057 | — |
| dev-29 | 1 | True | 1 | 1060 | — |
| dev-30 | 1 | True | 1 | 1053 | — |
| dev-31 | 1 | True | 4 | 4661 | — |
| dev-32 | 1 | True | 4 | 4656 | — |
| dev-33 | 1 | True | 1 | 1052 | — |
| dev-34 | 1 | True | 4 | 4735 | — |
| dev-35 | 1 | True | 4 | 4760 | — |
| dev-01 | 2 | True | 3 | 4215 | — |
| dev-02 | 2 | True | 3 | 4190 | — |
| dev-03 | 2 | False | 4 | 5909 | cascading_soft_failure |
| dev-04 | 2 | True | 3 | 4230 | — |
| dev-05 | 2 | True | 3 | 4399 | — |
| dev-06 | 2 | False | 4 | 6164 | soft_failure |
| dev-07 | 2 | False | 4 | 6285 | soft_failure |
| dev-08 | 2 | False | 4 | 6162 | soft_failure |
| dev-09 | 2 | False | 1 | 1065 | soft_failure |
| dev-10 | 2 | True | 4 | 6165 | — |
| dev-11 | 2 | False | 4 | 6223 | soft_failure |
| dev-12 | 2 | False | 3 | 4320 | soft_failure |
| dev-13 | 2 | False | 1 | 1062 | soft_failure |
| dev-14 | 2 | False | 3 | 4327 | soft_failure |
| dev-15 | 2 | False | 1 | 1057 | soft_failure |
| dev-16 | 2 | True | 1 | 1049 | — |
| dev-17 | 2 | True | 4 | 6254 | — |
| dev-18 | 2 | True | 1 | 1051 | — |
| dev-19 | 2 | True | 1 | 1050 | — |
| dev-20 | 2 | True | 1 | 1050 | — |
| dev-21 | 2 | True | 1 | 1051 | — |
| dev-22 | 2 | False | 1 | 1050 | soft_failure |
| dev-23 | 2 | True | 1 | 1050 | — |
| dev-24 | 2 | False | 1 | 1046 | soft_failure |
| dev-25 | 2 | True | 1 | 1054 | — |
| dev-26 | 2 | True | 1 | 1050 | — |
| dev-27 | 2 | True | 1 | 1051 | — |
| dev-28 | 2 | True | 1 | 1057 | — |
| dev-29 | 2 | True | 1 | 1060 | — |
| dev-30 | 2 | True | 1 | 1053 | — |
| dev-31 | 2 | True | 4 | 4658 | — |
| dev-32 | 2 | True | 4 | 4656 | — |
| dev-33 | 2 | True | 1 | 1052 | — |
| dev-34 | 2 | True | 4 | 4730 | — |
| dev-35 | 2 | True | 4 | 4760 | — |
