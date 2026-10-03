# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.6476 |
| tool_call_correctness | 0.9349 |
| tool_argument_validity | 0.9497 |
| trajectory_length_mean | 3.7429 |
| tokens_per_query_mean | 4368.0857 |
| usage_complete | 1.0000 |
| latency_mean | 8.0185 |
| completion_spread | 0.0286 |
| hard_failure_rate | 0.0190 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| dev-01 | 0 | True | 3 | 3164 | — |
| dev-02 | 0 | True | 3 | 3127 | — |
| dev-03 | 0 | True | 3 | 3141 | — |
| dev-04 | 0 | True | 3 | 3173 | — |
| dev-05 | 0 | True | 3 | 3340 | — |
| dev-06 | 0 | False | 3 | 7568 | hard_failure |
| dev-07 | 0 | False | 3 | 3105 | soft_failure |
| dev-08 | 0 | False | 3 | 5103 | soft_failure |
| dev-09 | 0 | True | 4 | 4791 | — |
| dev-10 | 0 | False | 4 | 10022 | cascading_soft_failure |
| dev-11 | 0 | False | 4 | 4743 | soft_failure |
| dev-12 | 0 | False | 3 | 3339 | soft_failure |
| dev-13 | 0 | False | 4 | 4792 | soft_failure |
| dev-14 | 0 | False | 4 | 4847 | cascading_soft_failure |
| dev-15 | 0 | True | 4 | 4769 | — |
| dev-16 | 0 | True | 4 | 5456 | — |
| dev-17 | 0 | True | 4 | 4640 | — |
| dev-18 | 0 | True | 4 | 5260 | — |
| dev-19 | 0 | True | 4 | 4642 | — |
| dev-20 | 0 | True | 4 | 3754 | — |
| dev-21 | 0 | False | 4 | 5415 | cascading_soft_failure |
| dev-22 | 0 | False | 4 | 4166 | cascading_soft_failure |
| dev-23 | 0 | False | 4 | 4264 | cascading_soft_failure |
| dev-24 | 0 | False | 4 | 4689 | soft_failure |
| dev-25 | 0 | False | 4 | 3962 | soft_failure |
| dev-26 | 0 | True | 4 | 4254 | — |
| dev-27 | 0 | True | 4 | 4800 | — |
| dev-28 | 0 | True | 4 | 4433 | — |
| dev-29 | 0 | True | 4 | 4046 | — |
| dev-30 | 0 | True | 4 | 4703 | — |
| dev-31 | 0 | True | 4 | 3268 | — |
| dev-32 | 0 | True | 4 | 3304 | — |
| dev-33 | 0 | True | 4 | 3295 | — |
| dev-34 | 0 | True | 4 | 3349 | — |
| dev-35 | 0 | True | 4 | 3344 | — |
| dev-01 | 1 | True | 3 | 3149 | — |
| dev-02 | 1 | True | 3 | 3127 | — |
| dev-03 | 1 | True | 3 | 3147 | — |
| dev-04 | 1 | True | 3 | 3158 | — |
| dev-05 | 1 | True | 3 | 3340 | — |
| dev-06 | 1 | True | 4 | 4870 | — |
| dev-07 | 1 | False | 3 | 3105 | soft_failure |
| dev-08 | 1 | False | 3 | 5145 | soft_failure |
| dev-09 | 1 | True | 4 | 4766 | — |
| dev-10 | 1 | False | 4 | 4943 | soft_failure |
| dev-11 | 1 | False | 4 | 4757 | soft_failure |
| dev-12 | 1 | False | 4 | 5113 | soft_failure |
| dev-13 | 1 | False | 4 | 4922 | soft_failure |
| dev-14 | 1 | False | 3 | 3240 | soft_failure |
| dev-15 | 1 | True | 4 | 4769 | — |
| dev-16 | 1 | True | 4 | 5456 | — |
| dev-17 | 1 | True | 4 | 4678 | — |
| dev-18 | 1 | True | 4 | 5645 | — |
| dev-19 | 1 | True | 4 | 5131 | — |
| dev-20 | 1 | True | 4 | 5948 | — |
| dev-21 | 1 | False | 4 | 3836 | cascading_soft_failure |
| dev-22 | 1 | False | 4 | 3456 | cascading_soft_failure |
| dev-23 | 1 | False | 4 | 4166 | soft_failure |
| dev-24 | 1 | False | 3 | 3228 | soft_failure |
| dev-25 | 1 | False | 4 | 3968 | soft_failure |
| dev-26 | 1 | True | 4 | 4238 | — |
| dev-27 | 1 | True | 4 | 4773 | — |
| dev-28 | 1 | True | 4 | 4436 | — |
| dev-29 | 1 | True | 4 | 4046 | — |
| dev-30 | 1 | True | 4 | 4723 | — |
| dev-31 | 1 | True | 4 | 3286 | — |
| dev-32 | 1 | True | 4 | 3304 | — |
| dev-33 | 1 | True | 4 | 3256 | — |
| dev-34 | 1 | True | 4 | 3349 | — |
| dev-35 | 1 | True | 4 | 3327 | — |
| dev-01 | 2 | True | 3 | 3149 | — |
| dev-02 | 2 | True | 3 | 3119 | — |
| dev-03 | 2 | True | 3 | 3141 | — |
| dev-04 | 2 | True | 3 | 3173 | — |
| dev-05 | 2 | True | 3 | 3331 | — |
| dev-06 | 2 | False | 4 | 12762 | hard_failure |
| dev-07 | 2 | False | 3 | 3105 | soft_failure |
| dev-08 | 2 | False | 3 | 5138 | soft_failure |
| dev-09 | 2 | True | 4 | 4791 | — |
| dev-10 | 2 | False | 4 | 10058 | cascading_soft_failure |
| dev-11 | 2 | True | 4 | 4830 | — |
| dev-12 | 2 | False | 3 | 3337 | soft_failure |
| dev-13 | 2 | False | 4 | 4837 | soft_failure |
| dev-14 | 2 | False | 3 | 3252 | soft_failure |
| dev-15 | 2 | True | 4 | 4785 | — |
| dev-16 | 2 | True | 4 | 5497 | — |
| dev-17 | 2 | True | 4 | 4677 | — |
| dev-18 | 2 | True | 4 | 5621 | — |
| dev-19 | 2 | True | 4 | 4937 | — |
| dev-20 | 2 | True | 4 | 3749 | — |
| dev-21 | 2 | False | 4 | 5351 | cascading_soft_failure |
| dev-22 | 2 | False | 4 | 4175 | cascading_soft_failure |
| dev-23 | 2 | False | 4 | 5509 | cascading_soft_failure |
| dev-24 | 2 | False | 4 | 4685 | soft_failure |
| dev-25 | 2 | False | 4 | 4010 | soft_failure |
| dev-26 | 2 | True | 4 | 3186 | — |
| dev-27 | 2 | True | 4 | 4843 | — |
| dev-28 | 2 | True | 4 | 4432 | — |
| dev-29 | 2 | True | 4 | 4046 | — |
| dev-30 | 2 | True | 4 | 4723 | — |
| dev-31 | 2 | True | 4 | 3268 | — |
| dev-32 | 2 | True | 4 | 3304 | — |
| dev-33 | 2 | True | 4 | 3283 | — |
| dev-34 | 2 | True | 4 | 3349 | — |
| dev-35 | 2 | True | 4 | 3327 | — |
