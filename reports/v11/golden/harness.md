# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.6296 |
| tool_call_correctness | 0.9659 |
| tool_argument_validity | 0.9951 |
| trajectory_length_mean | 4.8519 |
| tokens_per_query_mean | 6073.2222 |
| usage_complete | 1.0000 |
| latency_mean | 8.1223 |
| completion_spread | 0.1667 |
| hard_failure_rate | 0.0000 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| gold-01 | 0 | True | 3 | 3191 | — |
| gold-02 | 0 | True | 3 | 3161 | — |
| gold-03 | 0 | True | 4 | 4520 | — |
| gold-04 | 0 | True | 4 | 4892 | — |
| gold-05 | 0 | False | 4 | 4656 | soft_failure |
| gold-06 | 0 | False | 4 | 4774 | soft_failure |
| gold-07 | 0 | False | 4 | 4797 | soft_failure |
| gold-08 | 0 | False | 4 | 5111 | soft_failure |
| gold-09 | 0 | True | 4 | 4758 | — |
| gold-10 | 0 | True | 7 | 10415 | — |
| gold-11 | 0 | False | 5 | 8847 | soft_failure |
| gold-12 | 0 | False | 5 | 8498 | soft_failure |
| gold-13 | 0 | False | 7 | 8071 | cascading_soft_failure |
| gold-14 | 0 | False | 5 | 6392 | soft_failure |
| gold-15 | 0 | True | 7 | 10802 | — |
| gold-16 | 0 | True | 7 | 6477 | — |
| gold-17 | 0 | True | 7 | 8422 | — |
| gold-18 | 0 | True | 7 | 6538 | — |
| gold-01 | 1 | True | 3 | 3191 | — |
| gold-02 | 1 | True | 3 | 3155 | — |
| gold-03 | 1 | True | 4 | 4799 | — |
| gold-04 | 1 | True | 4 | 4899 | — |
| gold-05 | 1 | False | 4 | 4656 | soft_failure |
| gold-06 | 1 | True | 4 | 4776 | — |
| gold-07 | 1 | False | 4 | 4810 | soft_failure |
| gold-08 | 1 | False | 4 | 5111 | soft_failure |
| gold-09 | 1 | True | 4 | 4782 | — |
| gold-10 | 1 | True | 7 | 10413 | — |
| gold-11 | 1 | True | 5 | 8516 | — |
| gold-12 | 1 | False | 4 | 6740 | soft_failure |
| gold-13 | 1 | False | 2 | 1583 | soft_failure |
| gold-14 | 1 | True | 3 | 3117 | — |
| gold-15 | 1 | True | 7 | 11347 | — |
| gold-16 | 1 | True | 7 | 6477 | — |
| gold-17 | 1 | True | 7 | 6622 | — |
| gold-18 | 1 | True | 7 | 6566 | — |
| gold-01 | 2 | True | 3 | 3191 | — |
| gold-02 | 2 | True | 3 | 3161 | — |
| gold-03 | 2 | True | 4 | 4518 | — |
| gold-04 | 2 | True | 4 | 4901 | — |
| gold-05 | 2 | False | 4 | 4653 | soft_failure |
| gold-06 | 2 | False | 4 | 4769 | soft_failure |
| gold-07 | 2 | False | 4 | 4804 | soft_failure |
| gold-08 | 2 | False | 4 | 5112 | soft_failure |
| gold-09 | 2 | True | 4 | 4779 | — |
| gold-10 | 2 | True | 7 | 10413 | — |
| gold-11 | 2 | False | 5 | 9055 | soft_failure |
| gold-12 | 2 | False | 5 | 9781 | soft_failure |
| gold-13 | 2 | False | 2 | 1578 | soft_failure |
| gold-14 | 2 | True | 7 | 10489 | — |
| gold-15 | 2 | True | 7 | 11226 | — |
| gold-16 | 2 | True | 7 | 6454 | — |
| gold-17 | 2 | True | 7 | 6622 | — |
| gold-18 | 2 | True | 7 | 6566 | — |
