# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.7778 |
| tool_call_correctness | 1.0000 |
| tool_argument_validity | 1.0000 |
| trajectory_length_mean | 3.6667 |
| tokens_per_query_mean | 6244.6667 |
| usage_complete | 1.0000 |
| latency_mean | 7.0076 |
| completion_spread | 0.0000 |
| hard_failure_rate | 0.0000 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| dev-07 | 0 | True | 7 | 14754 | — |
| dev-08 | 0 | True | 5 | 8485 | — |
| dev-10 | 0 | False | 7 | 13875 | cascading_soft_failure |
| dev-13 | 0 | False | 4 | 6840 | soft_failure |
| dev-16 | 0 | True | 2 | 2346 | — |
| dev-18 | 0 | True | 3 | 3863 | — |
| dev-21 | 0 | True | 2 | 2502 | — |
| dev-29 | 0 | True | 2 | 2411 | — |
| dev-32 | 0 | True | 1 | 1126 | — |
