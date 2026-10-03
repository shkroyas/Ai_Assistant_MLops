# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.6095 |
| tool_call_correctness | 0.9599 |
| tool_argument_validity | 0.9722 |
| trajectory_length_mean | 4.2476 |
| tokens_per_query_mean | 5254.8762 |
| usage_complete | 1.0000 |
| latency_mean | 8.7287 |
| completion_spread | 0.0571 |
| hard_failure_rate | 0.0095 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| dev-01 | 0 | True | 3 | 3142 | — |
| dev-02 | 0 | True | 3 | 3127 | — |
| dev-03 | 0 | True | 3 | 3147 | — |
| dev-04 | 0 | True | 3 | 3173 | — |
| dev-05 | 0 | True | 3 | 3340 | — |
| dev-06 | 0 | True | 3 | 6756 | — |
| dev-07 | 0 | False | 3 | 3105 | soft_failure |
| dev-08 | 0 | False | 3 | 5123 | soft_failure |
| dev-09 | 0 | True | 4 | 4766 | — |
| dev-10 | 0 | False | 3 | 5885 | hard_failure |
| dev-11 | 0 | False | 4 | 4741 | soft_failure |
| dev-12 | 0 | False | 3 | 3333 | soft_failure |
| dev-13 | 0 | False | 4 | 4967 | soft_failure |
| dev-14 | 0 | False | 3 | 3242 | soft_failure |
| dev-15 | 0 | True | 4 | 4756 | — |
| dev-16 | 0 | True | 2 | 1499 | — |
| dev-17 | 0 | True | 4 | 4675 | — |
| dev-18 | 0 | True | 4 | 5198 | — |
| dev-19 | 0 | True | 2 | 1509 | — |
| dev-20 | 0 | True | 2 | 1598 | — |
| dev-21 | 0 | False | 6 | 6762 | cascading_soft_failure |
| dev-22 | 0 | False | 4 | 4443 | soft_failure |
| dev-23 | 0 | False | 2 | 1586 | soft_failure |
| dev-24 | 0 | False | 4 | 4680 | soft_failure |
| dev-25 | 0 | False | 7 | 24053 | cascading_soft_failure |
| dev-26 | 0 | True | 3 | 2509 | — |
| dev-27 | 0 | True | 6 | 7786 | — |
| dev-28 | 0 | False | 5 | 6073 | soft_failure |
| dev-29 | 0 | True | 7 | 9857 | — |
| dev-30 | 0 | True | 4 | 4723 | — |
| dev-31 | 0 | True | 7 | 6387 | — |
| dev-32 | 0 | True | 7 | 6559 | — |
| dev-33 | 0 | True | 7 | 6455 | — |
| dev-34 | 0 | True | 7 | 6614 | — |
| dev-35 | 0 | True | 7 | 6637 | — |
| dev-01 | 1 | True | 3 | 3152 | — |
| dev-02 | 1 | True | 3 | 3127 | — |
| dev-03 | 1 | True | 3 | 3141 | — |
| dev-04 | 1 | True | 3 | 3158 | — |
| dev-05 | 1 | True | 3 | 3336 | — |
| dev-06 | 1 | True | 4 | 4870 | — |
| dev-07 | 1 | False | 3 | 3105 | soft_failure |
| dev-08 | 1 | True | 3 | 5255 | — |
| dev-09 | 1 | True | 4 | 4766 | — |
| dev-10 | 1 | False | 4 | 4865 | soft_failure |
| dev-11 | 1 | True | 4 | 4768 | — |
| dev-12 | 1 | False | 3 | 3337 | soft_failure |
| dev-13 | 1 | False | 4 | 4987 | soft_failure |
| dev-14 | 1 | False | 3 | 3222 | soft_failure |
| dev-15 | 1 | True | 4 | 4756 | — |
| dev-16 | 1 | True | 2 | 1517 | — |
| dev-17 | 1 | True | 4 | 4663 | — |
| dev-18 | 1 | True | 7 | 11270 | — |
| dev-19 | 1 | True | 2 | 1519 | — |
| dev-20 | 1 | True | 2 | 1598 | — |
| dev-21 | 1 | False | 2 | 1571 | soft_failure |
| dev-22 | 1 | False | 6 | 7445 | cascading_soft_failure |
| dev-23 | 1 | False | 2 | 1580 | soft_failure |
| dev-24 | 1 | False | 4 | 4671 | soft_failure |
| dev-25 | 1 | False | 7 | 20534 | cascading_soft_failure |
| dev-26 | 1 | True | 6 | 8339 | — |
| dev-27 | 1 | False | 5 | 6932 | soft_failure |
| dev-28 | 1 | True | 7 | 10119 | — |
| dev-29 | 1 | False | 6 | 7546 | soft_failure |
| dev-30 | 1 | False | 4 | 4766 | soft_failure |
| dev-31 | 1 | True | 7 | 6414 | — |
| dev-32 | 1 | True | 7 | 6559 | — |
| dev-33 | 1 | True | 7 | 6467 | — |
| dev-34 | 1 | True | 7 | 6531 | — |
| dev-35 | 1 | True | 7 | 6604 | — |
| dev-01 | 2 | True | 3 | 3149 | — |
| dev-02 | 2 | True | 3 | 3127 | — |
| dev-03 | 2 | True | 3 | 3143 | — |
| dev-04 | 2 | True | 3 | 3158 | — |
| dev-05 | 2 | True | 3 | 3367 | — |
| dev-06 | 2 | True | 4 | 4880 | — |
| dev-07 | 2 | False | 3 | 3105 | soft_failure |
| dev-08 | 2 | False | 3 | 5167 | soft_failure |
| dev-09 | 2 | True | 4 | 4791 | — |
| dev-10 | 2 | False | 5 | 7025 | soft_failure |
| dev-11 | 2 | False | 4 | 4757 | soft_failure |
| dev-12 | 2 | False | 3 | 3337 | soft_failure |
| dev-13 | 2 | False | 4 | 5017 | soft_failure |
| dev-14 | 2 | False | 3 | 3222 | soft_failure |
| dev-15 | 2 | True | 4 | 4762 | — |
| dev-16 | 2 | True | 2 | 1499 | — |
| dev-17 | 2 | True | 5 | 6539 | — |
| dev-18 | 2 | True | 7 | 12786 | — |
| dev-19 | 2 | True | 2 | 1509 | — |
| dev-20 | 2 | True | 2 | 1707 | — |
| dev-21 | 2 | False | 2 | 1571 | soft_failure |
| dev-22 | 2 | False | 4 | 4425 | soft_failure |
| dev-23 | 2 | False | 2 | 1601 | soft_failure |
| dev-24 | 2 | False | 3 | 3209 | soft_failure |
| dev-25 | 2 | False | 7 | 22388 | cascading_soft_failure |
| dev-26 | 2 | True | 7 | 9357 | — |
| dev-27 | 2 | False | 5 | 6789 | soft_failure |
| dev-28 | 2 | False | 4 | 4461 | soft_failure |
| dev-29 | 2 | False | 5 | 5845 | soft_failure |
| dev-30 | 2 | True | 4 | 4723 | — |
| dev-31 | 2 | True | 7 | 6421 | — |
| dev-32 | 2 | True | 7 | 6559 | — |
| dev-33 | 2 | True | 7 | 6467 | — |
| dev-34 | 2 | True | 7 | 6602 | — |
| dev-35 | 2 | True | 7 | 6601 | — |
