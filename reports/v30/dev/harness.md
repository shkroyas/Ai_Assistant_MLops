# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.6667 |
| tool_call_correctness | 1.0000 |
| tool_argument_validity | 1.0000 |
| trajectory_length_mean | 4.1111 |
| tokens_per_query_mean | 7825.4444 |
| usage_complete | 1.0000 |
| latency_mean | 7.8691 |
| completion_spread | 0.0000 |
| hard_failure_rate | 0.0000 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| dev-07 | 0 | True | 6 | 13165 | — |
| dev-08 | 0 | False | 5 | 9139 | soft_failure |
| dev-10 | 0 | False | 7 | 15701 | cascading_soft_failure |
| dev-13 | 0 | False | 4 | 7122 | soft_failure |
| dev-16 | 0 | True | 3 | 4267 | — |
| dev-18 | 0 | True | 2 | 2702 | — |
| dev-21 | 0 | True | 2 | 2734 | — |
| dev-29 | 0 | True | 7 | 14324 | — |
| dev-32 | 0 | True | 1 | 1275 | — |
