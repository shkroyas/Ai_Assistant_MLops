# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.6857 |
| tool_call_correctness | 0.9350 |
| tool_argument_validity | 0.9458 |
| trajectory_length_mean | 3.5714 |
| tokens_per_query_mean | 4082.2381 |
| usage_complete | 1.0000 |
| latency_mean | 7.3934 |
| completion_spread | 0.0571 |
| hard_failure_rate | 0.0095 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| dev-01 | 0 | True | 3 | 3156 | — |
| dev-02 | 0 | True | 3 | 3127 | — |
| dev-03 | 0 | True | 3 | 3140 | — |
| dev-04 | 0 | True | 3 | 3158 | — |
| dev-05 | 0 | True | 3 | 3340 | — |
| dev-06 | 0 | True | 3 | 6653 | — |
| dev-07 | 0 | False | 3 | 3105 | soft_failure |
| dev-08 | 0 | False | 3 | 6316 | hard_failure |
| dev-09 | 0 | True | 4 | 4766 | — |
| dev-10 | 0 | False | 3 | 6691 | soft_failure |
| dev-11 | 0 | False | 4 | 4743 | soft_failure |
| dev-12 | 0 | True | 4 | 5372 | — |
| dev-13 | 0 | False | 4 | 4988 | soft_failure |
| dev-14 | 0 | False | 3 | 3237 | soft_failure |
| dev-15 | 0 | True | 4 | 4783 | — |
| dev-16 | 0 | True | 2 | 1499 | — |
| dev-17 | 0 | True | 4 | 4763 | — |
| dev-18 | 0 | True | 4 | 5561 | — |
| dev-19 | 0 | True | 2 | 1510 | — |
| dev-20 | 0 | True | 2 | 1709 | — |
| dev-21 | 0 | False | 4 | 3921 | cascading_soft_failure |
| dev-22 | 0 | False | 4 | 4425 | cascading_soft_failure |
| dev-23 | 0 | False | 2 | 1586 | soft_failure |
| dev-24 | 0 | False | 4 | 4665 | soft_failure |
| dev-25 | 0 | False | 4 | 7853 | cascading_soft_failure |
| dev-26 | 0 | True | 3 | 2509 | — |
| dev-27 | 0 | True | 4 | 4701 | — |
| dev-28 | 0 | True | 4 | 4436 | — |
| dev-29 | 0 | True | 4 | 4046 | — |
| dev-30 | 0 | True | 4 | 4723 | — |
| dev-31 | 0 | True | 4 | 3289 | — |
| dev-32 | 0 | True | 4 | 3304 | — |
| dev-33 | 0 | True | 4 | 3257 | — |
| dev-34 | 0 | True | 4 | 3349 | — |
| dev-35 | 0 | True | 4 | 3327 | — |
| dev-01 | 1 | True | 3 | 3143 | — |
| dev-02 | 1 | True | 3 | 3127 | — |
| dev-03 | 1 | True | 3 | 3147 | — |
| dev-04 | 1 | True | 3 | 3173 | — |
| dev-05 | 1 | True | 3 | 3331 | — |
| dev-06 | 1 | True | 4 | 4874 | — |
| dev-07 | 1 | False | 3 | 3105 | soft_failure |
| dev-08 | 1 | True | 3 | 5262 | — |
| dev-09 | 1 | True | 4 | 4766 | — |
| dev-10 | 1 | False | 4 | 4700 | soft_failure |
| dev-11 | 1 | False | 4 | 4757 | soft_failure |
| dev-12 | 1 | True | 4 | 5372 | — |
| dev-13 | 1 | False | 4 | 5078 | soft_failure |
| dev-14 | 1 | False | 3 | 3220 | soft_failure |
| dev-15 | 1 | True | 4 | 4771 | — |
| dev-16 | 1 | True | 2 | 1499 | — |
| dev-17 | 1 | True | 4 | 4676 | — |
| dev-18 | 1 | True | 4 | 5391 | — |
| dev-19 | 1 | True | 2 | 1509 | — |
| dev-20 | 1 | True | 4 | 3788 | — |
| dev-21 | 1 | False | 4 | 3746 | cascading_soft_failure |
| dev-22 | 1 | False | 4 | 3814 | soft_failure |
| dev-23 | 1 | False | 4 | 4287 | cascading_soft_failure |
| dev-24 | 1 | False | 3 | 3217 | soft_failure |
| dev-25 | 1 | False | 4 | 8714 | cascading_soft_failure |
| dev-26 | 1 | True | 4 | 4260 | — |
| dev-27 | 1 | True | 4 | 4797 | — |
| dev-28 | 1 | True | 4 | 4417 | — |
| dev-29 | 1 | True | 4 | 4046 | — |
| dev-30 | 1 | True | 4 | 4723 | — |
| dev-31 | 1 | True | 4 | 3286 | — |
| dev-32 | 1 | True | 4 | 3304 | — |
| dev-33 | 1 | True | 4 | 3295 | — |
| dev-34 | 1 | True | 4 | 3349 | — |
| dev-35 | 1 | True | 4 | 3378 | — |
| dev-01 | 2 | True | 3 | 3153 | — |
| dev-02 | 2 | True | 3 | 3127 | — |
| dev-03 | 2 | True | 3 | 3140 | — |
| dev-04 | 2 | True | 3 | 3158 | — |
| dev-05 | 2 | True | 3 | 3340 | — |
| dev-06 | 2 | True | 4 | 4873 | — |
| dev-07 | 2 | False | 4 | 5054 | soft_failure |
| dev-08 | 2 | False | 3 | 5168 | soft_failure |
| dev-09 | 2 | True | 4 | 4766 | — |
| dev-10 | 2 | False | 4 | 9072 | soft_failure |
| dev-11 | 2 | False | 4 | 4757 | soft_failure |
| dev-12 | 2 | False | 3 | 3339 | soft_failure |
| dev-13 | 2 | False | 4 | 5011 | soft_failure |
| dev-14 | 2 | False | 4 | 5017 | soft_failure |
| dev-15 | 2 | True | 4 | 4788 | — |
| dev-16 | 2 | True | 2 | 1515 | — |
| dev-17 | 2 | True | 4 | 4663 | — |
| dev-18 | 2 | True | 4 | 5802 | — |
| dev-19 | 2 | True | 2 | 1508 | — |
| dev-20 | 2 | True | 4 | 3788 | — |
| dev-21 | 2 | False | 4 | 3782 | cascading_soft_failure |
| dev-22 | 2 | False | 4 | 4372 | soft_failure |
| dev-23 | 2 | False | 2 | 1578 | soft_failure |
| dev-24 | 2 | False | 4 | 4684 | soft_failure |
| dev-25 | 2 | False | 4 | 7988 | cascading_soft_failure |
| dev-26 | 2 | True | 4 | 4224 | — |
| dev-27 | 2 | True | 4 | 4899 | — |
| dev-28 | 2 | True | 4 | 4436 | — |
| dev-29 | 2 | True | 4 | 4044 | — |
| dev-30 | 2 | True | 4 | 4723 | — |
| dev-31 | 2 | True | 4 | 3268 | — |
| dev-32 | 2 | True | 4 | 3304 | — |
| dev-33 | 2 | True | 4 | 3295 | — |
| dev-34 | 2 | True | 4 | 3349 | — |
| dev-35 | 2 | True | 4 | 3320 | — |
