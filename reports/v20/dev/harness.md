# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.8095 |
| tool_call_correctness | 1.0000 |
| tool_argument_validity | 1.0000 |
| trajectory_length_mean | 1.7238 |
| tokens_per_query_mean | 1719.6286 |
| usage_complete | 0.0000 |
| latency_mean | 25.3635 |
| completion_spread | 0.0857 |
| hard_failure_rate | 0.0857 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| dev-01 | 0 | True | 2 | 2046 | — |
| dev-02 | 0 | True | 2 | 2082 | — |
| dev-03 | 0 | True | 2 | 2017 | — |
| dev-04 | 0 | True | 2 | 2048 | — |
| dev-05 | 0 | False | 2 | 833 | hard_failure |
| dev-06 | 0 | True | 2 | 2210 | — |
| dev-07 | 0 | True | 3 | 3730 | — |
| dev-08 | 0 | True | 3 | 3601 | — |
| dev-09 | 0 | False | 7 | 12354 | cascading_soft_failure |
| dev-10 | 0 | True | 3 | 3683 | — |
| dev-11 | 0 | True | 2 | 2191 | — |
| dev-12 | 0 | True | 2 | 2218 | — |
| dev-13 | 0 | True | 2 | 2258 | — |
| dev-14 | 0 | False | 2 | 2147 | soft_failure |
| dev-15 | 0 | True | 2 | 2265 | — |
| dev-16 | 0 | True | 2 | 2009 | — |
| dev-17 | 0 | True | 3 | 3339 | — |
| dev-18 | 0 | False | 1 | 837 | soft_failure |
| dev-19 | 0 | True | 2 | 2015 | — |
| dev-20 | 0 | True | 1 | 821 | — |
| dev-21 | 0 | True | 1 | 858 | — |
| dev-22 | 0 | True | 1 | 852 | — |
| dev-23 | 0 | True | 1 | 834 | — |
| dev-24 | 0 | False | 2 | 835 | hard_failure |
| dev-25 | 0 | True | 1 | 835 | — |
| dev-26 | 0 | True | 1 | 821 | — |
| dev-27 | 0 | True | 1 | 842 | — |
| dev-28 | 0 | True | 1 | 841 | — |
| dev-29 | 0 | True | 2 | 2124 | — |
| dev-30 | 0 | True | 1 | 846 | — |
| dev-31 | 0 | True | 1 | 819 | — |
| dev-32 | 0 | True | 1 | 816 | — |
| dev-33 | 0 | True | 1 | 820 | — |
| dev-34 | 0 | True | 1 | 819 | — |
| dev-35 | 0 | True | 1 | 822 | — |
| dev-01 | 1 | True | 2 | 2047 | — |
| dev-02 | 1 | True | 2 | 2082 | — |
| dev-03 | 1 | False | 2 | 820 | hard_failure |
| dev-04 | 1 | False | 2 | 821 | hard_failure |
| dev-05 | 1 | False | 2 | 833 | hard_failure |
| dev-06 | 1 | True | 2 | 2212 | — |
| dev-07 | 1 | True | 3 | 3733 | — |
| dev-08 | 1 | True | 3 | 3619 | — |
| dev-09 | 1 | False | 3 | 3749 | soft_failure |
| dev-10 | 1 | True | 3 | 3596 | — |
| dev-11 | 1 | True | 2 | 2191 | — |
| dev-12 | 1 | True | 2 | 2238 | — |
| dev-13 | 1 | True | 2 | 2254 | — |
| dev-14 | 1 | False | 2 | 2138 | soft_failure |
| dev-15 | 1 | True | 2 | 2293 | — |
| dev-16 | 1 | True | 2 | 2009 | — |
| dev-17 | 1 | False | 2 | 2005 | soft_failure |
| dev-18 | 1 | False | 1 | 849 | soft_failure |
| dev-19 | 1 | True | 1 | 845 | — |
| dev-20 | 1 | True | 1 | 838 | — |
| dev-21 | 1 | True | 1 | 858 | — |
| dev-22 | 1 | True | 1 | 850 | — |
| dev-23 | 1 | True | 1 | 828 | — |
| dev-24 | 1 | False | 2 | 831 | hard_failure |
| dev-25 | 1 | True | 1 | 834 | — |
| dev-26 | 1 | True | 1 | 821 | — |
| dev-27 | 1 | True | 1 | 836 | — |
| dev-28 | 1 | True | 1 | 841 | — |
| dev-29 | 1 | True | 2 | 842 | hard_failure |
| dev-30 | 1 | True | 1 | 842 | — |
| dev-31 | 1 | True | 1 | 819 | — |
| dev-32 | 1 | True | 1 | 816 | — |
| dev-33 | 1 | True | 1 | 820 | — |
| dev-34 | 1 | True | 1 | 820 | — |
| dev-35 | 1 | True | 1 | 822 | — |
| dev-01 | 2 | True | 2 | 2046 | — |
| dev-02 | 2 | True | 2 | 2082 | — |
| dev-03 | 2 | True | 2 | 2017 | — |
| dev-04 | 2 | True | 2 | 2052 | — |
| dev-05 | 2 | False | 2 | 833 | hard_failure |
| dev-06 | 2 | True | 2 | 2221 | — |
| dev-07 | 2 | True | 3 | 3717 | — |
| dev-08 | 2 | True | 3 | 3619 | — |
| dev-09 | 2 | False | 3 | 3698 | soft_failure |
| dev-10 | 2 | True | 3 | 3619 | — |
| dev-11 | 2 | True | 2 | 2184 | — |
| dev-12 | 2 | True | 2 | 2215 | — |
| dev-13 | 2 | True | 2 | 2251 | — |
| dev-14 | 2 | False | 2 | 2152 | soft_failure |
| dev-15 | 2 | True | 2 | 2265 | — |
| dev-16 | 2 | False | 2 | 2003 | soft_failure |
| dev-17 | 2 | False | 2 | 1992 | soft_failure |
| dev-18 | 2 | False | 1 | 856 | soft_failure |
| dev-19 | 2 | True | 2 | 2015 | — |
| dev-20 | 2 | True | 1 | 821 | — |
| dev-21 | 2 | True | 1 | 856 | — |
| dev-22 | 2 | True | 1 | 849 | — |
| dev-23 | 2 | True | 1 | 840 | — |
| dev-24 | 2 | False | 2 | 831 | hard_failure |
| dev-25 | 2 | True | 1 | 835 | — |
| dev-26 | 2 | True | 1 | 820 | — |
| dev-27 | 2 | True | 1 | 842 | — |
| dev-28 | 2 | True | 1 | 828 | — |
| dev-29 | 2 | True | 2 | 2114 | — |
| dev-30 | 2 | True | 1 | 846 | — |
| dev-31 | 2 | True | 1 | 819 | — |
| dev-32 | 2 | True | 1 | 816 | — |
| dev-33 | 2 | True | 1 | 820 | — |
| dev-34 | 2 | True | 1 | 825 | — |
| dev-35 | 2 | True | 1 | 822 | — |
