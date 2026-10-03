# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.6571 |
| tool_call_correctness | 0.9142 |
| tool_argument_validity | 0.9201 |
| trajectory_length_mean | 4.7048 |
| tokens_per_query_mean | 5926.1238 |
| usage_complete | 1.0000 |
| latency_mean | 9.6627 |
| completion_spread | 0.0857 |
| hard_failure_rate | 0.0095 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| dev-01 | 0 | True | 3 | 3143 | — |
| dev-02 | 0 | True | 3 | 3129 | — |
| dev-03 | 0 | True | 3 | 3141 | — |
| dev-04 | 0 | True | 3 | 3158 | — |
| dev-05 | 0 | True | 3 | 3340 | — |
| dev-06 | 0 | True | 4 | 4867 | — |
| dev-07 | 0 | False | 3 | 3105 | soft_failure |
| dev-08 | 0 | True | 3 | 5285 | — |
| dev-09 | 0 | True | 4 | 4766 | — |
| dev-10 | 0 | False | 7 | 11876 | cascading_soft_failure |
| dev-11 | 0 | True | 4 | 4760 | — |
| dev-12 | 0 | False | 7 | 12004 | cascading_soft_failure |
| dev-13 | 0 | False | 4 | 5048 | soft_failure |
| dev-14 | 0 | False | 3 | 3228 | soft_failure |
| dev-15 | 0 | True | 4 | 4778 | — |
| dev-16 | 0 | True | 2 | 1499 | — |
| dev-17 | 0 | False | 5 | 6506 | soft_failure |
| dev-18 | 0 | True | 7 | 10260 | — |
| dev-19 | 0 | True | 2 | 1499 | — |
| dev-20 | 0 | True | 2 | 1707 | — |
| dev-21 | 0 | False | 5 | 5123 | cascading_soft_failure |
| dev-22 | 0 | False | 7 | 10713 | cascading_soft_failure |
| dev-23 | 0 | False | 2 | 1586 | soft_failure |
| dev-24 | 0 | False | 4 | 4685 | soft_failure |
| dev-25 | 0 | False | 7 | 18974 | cascading_soft_failure |
| dev-26 | 0 | True | 7 | 7799 | — |
| dev-27 | 0 | False | 5 | 6979 | soft_failure |
| dev-28 | 0 | False | 5 | 6151 | soft_failure |
| dev-29 | 0 | False | 6 | 7546 | soft_failure |
| dev-30 | 0 | True | 4 | 4723 | — |
| dev-31 | 0 | True | 7 | 6429 | — |
| dev-32 | 0 | True | 7 | 6559 | — |
| dev-33 | 0 | True | 7 | 6455 | — |
| dev-34 | 0 | True | 7 | 6617 | — |
| dev-35 | 0 | True | 7 | 6607 | — |
| dev-01 | 1 | True | 3 | 3200 | — |
| dev-02 | 1 | True | 3 | 3115 | — |
| dev-03 | 1 | True | 3 | 3147 | — |
| dev-04 | 1 | True | 3 | 3173 | — |
| dev-05 | 1 | True | 3 | 3340 | — |
| dev-06 | 1 | True | 4 | 4874 | — |
| dev-07 | 1 | False | 3 | 3105 | soft_failure |
| dev-08 | 1 | False | 3 | 5211 | soft_failure |
| dev-09 | 1 | True | 4 | 4791 | — |
| dev-10 | 1 | False | 7 | 12500 | cascading_soft_failure |
| dev-11 | 1 | True | 4 | 4747 | — |
| dev-12 | 1 | True | 4 | 5372 | — |
| dev-13 | 1 | False | 4 | 4987 | soft_failure |
| dev-14 | 1 | False | 4 | 5010 | soft_failure |
| dev-15 | 1 | True | 4 | 4777 | — |
| dev-16 | 1 | True | 2 | 1517 | — |
| dev-17 | 1 | True | 5 | 6516 | — |
| dev-18 | 1 | True | 7 | 11577 | — |
| dev-19 | 1 | True | 2 | 1509 | — |
| dev-20 | 1 | True | 7 | 8183 | — |
| dev-21 | 1 | False | 7 | 8187 | cascading_soft_failure |
| dev-22 | 1 | False | 7 | 10721 | cascading_soft_failure |
| dev-23 | 1 | False | 2 | 1592 | soft_failure |
| dev-24 | 1 | False | 4 | 4688 | soft_failure |
| dev-25 | 1 | False | 7 | 18839 | cascading_soft_failure |
| dev-26 | 1 | True | 7 | 6216 | — |
| dev-27 | 1 | True | 6 | 7539 | — |
| dev-28 | 1 | True | 7 | 12649 | — |
| dev-29 | 1 | False | 6 | 7546 | soft_failure |
| dev-30 | 1 | True | 4 | 4723 | — |
| dev-31 | 1 | True | 7 | 6414 | — |
| dev-32 | 1 | True | 7 | 6559 | — |
| dev-33 | 1 | True | 7 | 6451 | — |
| dev-34 | 1 | True | 7 | 6613 | — |
| dev-35 | 1 | True | 7 | 6607 | — |
| dev-01 | 2 | True | 3 | 3142 | — |
| dev-02 | 2 | True | 3 | 3121 | — |
| dev-03 | 2 | True | 3 | 3140 | — |
| dev-04 | 2 | True | 3 | 3173 | — |
| dev-05 | 2 | True | 3 | 3411 | — |
| dev-06 | 2 | True | 4 | 4872 | — |
| dev-07 | 2 | True | 5 | 7185 | — |
| dev-08 | 2 | False | 3 | 5145 | soft_failure |
| dev-09 | 2 | True | 4 | 4791 | — |
| dev-10 | 2 | False | 3 | 6564 | soft_failure |
| dev-11 | 2 | False | 4 | 4757 | soft_failure |
| dev-12 | 2 | True | 4 | 5377 | — |
| dev-13 | 2 | False | 4 | 5045 | soft_failure |
| dev-14 | 2 | False | 3 | 3226 | soft_failure |
| dev-15 | 2 | True | 4 | 4786 | — |
| dev-16 | 2 | True | 2 | 1499 | — |
| dev-17 | 2 | True | 4 | 4663 | — |
| dev-18 | 2 | True | 7 | 12701 | — |
| dev-19 | 2 | True | 2 | 1510 | — |
| dev-20 | 2 | True | 7 | 8183 | — |
| dev-21 | 2 | False | 7 | 7919 | cascading_soft_failure |
| dev-22 | 2 | False | 7 | 10780 | cascading_soft_failure |
| dev-23 | 2 | False | 2 | 2707 | hard_failure |
| dev-24 | 2 | False | 4 | 4680 | soft_failure |
| dev-25 | 2 | False | 7 | 19448 | cascading_soft_failure |
| dev-26 | 2 | True | 3 | 2501 | — |
| dev-27 | 2 | True | 6 | 7684 | — |
| dev-28 | 2 | True | 7 | 10119 | — |
| dev-29 | 2 | False | 3 | 2769 | soft_failure |
| dev-30 | 2 | True | 4 | 4723 | — |
| dev-31 | 2 | True | 7 | 6443 | — |
| dev-32 | 2 | True | 7 | 6559 | — |
| dev-33 | 2 | True | 7 | 6366 | — |
| dev-34 | 2 | True | 7 | 6616 | — |
| dev-35 | 2 | True | 7 | 6598 | — |
