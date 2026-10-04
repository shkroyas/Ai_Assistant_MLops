# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.6667 |
| tool_call_correctness | 1.0000 |
| tool_argument_validity | 1.0000 |
| trajectory_length_mean | 3.8889 |
| tokens_per_query_mean | 6040.1111 |
| usage_complete | 1.0000 |
| latency_mean | 6.1239 |
| completion_spread | 0.0000 |
| hard_failure_rate | 0.0000 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| dev-07 | 0 | True | 5 | 9102 | — |
| dev-08 | 0 | False | 5 | 8340 | soft_failure |
| dev-10 | 0 | True | 5 | 8661 | — |
| dev-13 | 0 | False | 4 | 6688 | soft_failure |
| dev-16 | 0 | True | 3 | 3772 | — |
| dev-18 | 0 | True | 4 | 5450 | — |
| dev-21 | 0 | True | 4 | 5774 | — |
| dev-29 | 0 | False | 4 | 5448 | cascading_soft_failure |
| dev-32 | 0 | True | 1 | 1126 | — |
