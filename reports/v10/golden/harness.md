# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.6852 |
| tool_call_correctness | 0.9487 |
| tool_argument_validity | 0.9872 |
| trajectory_length_mean | 3.8148 |
| tokens_per_query_mean | 4375.7963 |
| usage_complete | 1.0000 |
| latency_mean | 6.3324 |
| completion_spread | 0.0556 |
| hard_failure_rate | 0.0000 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| gold-01 | 0 | True | 3 | 3191 | — |
| gold-02 | 0 | True | 3 | 3161 | — |
| gold-03 | 0 | True | 4 | 4796 | — |
| gold-04 | 0 | True | 4 | 4893 | — |
| gold-05 | 0 | False | 4 | 4645 | soft_failure |
| gold-06 | 0 | False | 4 | 4770 | soft_failure |
| gold-07 | 0 | False | 4 | 4810 | soft_failure |
| gold-08 | 0 | False | 4 | 5136 | soft_failure |
| gold-09 | 0 | True | 4 | 4765 | — |
| gold-10 | 0 | True | 4 | 5071 | — |
| gold-11 | 0 | True | 4 | 4422 | — |
| gold-12 | 0 | False | 4 | 6280 | soft_failure |
| gold-13 | 0 | False | 4 | 3812 | cascading_soft_failure |
| gold-14 | 0 | True | 4 | 4651 | — |
| gold-15 | 0 | True | 4 | 4815 | — |
| gold-16 | 0 | True | 4 | 3315 | — |
| gold-17 | 0 | True | 4 | 3334 | — |
| gold-18 | 0 | True | 4 | 3312 | — |
| gold-01 | 1 | True | 3 | 3194 | — |
| gold-02 | 1 | True | 3 | 3164 | — |
| gold-03 | 1 | True | 4 | 4799 | — |
| gold-04 | 1 | True | 4 | 4892 | — |
| gold-05 | 1 | False | 4 | 4656 | soft_failure |
| gold-06 | 1 | True | 4 | 4771 | — |
| gold-07 | 1 | False | 4 | 4810 | soft_failure |
| gold-08 | 1 | False | 4 | 5111 | soft_failure |
| gold-09 | 1 | True | 4 | 4792 | — |
| gold-10 | 1 | True | 4 | 5071 | — |
| gold-11 | 1 | True | 4 | 6121 | — |
| gold-12 | 1 | False | 4 | 6555 | soft_failure |
| gold-13 | 1 | False | 2 | 1595 | soft_failure |
| gold-14 | 1 | True | 3 | 3117 | — |
| gold-15 | 1 | True | 4 | 4853 | — |
| gold-16 | 1 | True | 4 | 3315 | — |
| gold-17 | 1 | True | 4 | 3334 | — |
| gold-18 | 1 | True | 4 | 3304 | — |
| gold-01 | 2 | True | 3 | 3191 | — |
| gold-02 | 2 | True | 3 | 3161 | — |
| gold-03 | 2 | True | 4 | 4520 | — |
| gold-04 | 2 | True | 4 | 4791 | — |
| gold-05 | 2 | False | 4 | 4656 | soft_failure |
| gold-06 | 2 | False | 3 | 3331 | soft_failure |
| gold-07 | 2 | False | 4 | 4808 | soft_failure |
| gold-08 | 2 | False | 4 | 5112 | soft_failure |
| gold-09 | 2 | True | 4 | 4788 | — |
| gold-10 | 2 | True | 4 | 5071 | — |
| gold-11 | 2 | True | 4 | 6317 | — |
| gold-12 | 2 | False | 4 | 6651 | soft_failure |
| gold-13 | 2 | False | 4 | 3792 | cascading_soft_failure |
| gold-14 | 2 | True | 4 | 4601 | — |
| gold-15 | 2 | True | 4 | 4906 | — |
| gold-16 | 2 | True | 4 | 3315 | — |
| gold-17 | 2 | True | 4 | 3334 | — |
| gold-18 | 2 | True | 4 | 3315 | — |
