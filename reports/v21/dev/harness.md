# Harness results

| Metric | Value |
|---|---|
| task_completion_rate | 0.8190 |
| tool_call_correctness | 0.9894 |
| tool_argument_validity | 0.9894 |
| trajectory_length_mean | 1.7619 |
| tokens_per_query_mean | 1902.3810 |
| usage_complete | 0.0000 |
| latency_mean | 25.8995 |
| completion_spread | 0.0571 |
| hard_failure_rate | 0.0095 |
| failure_injection_safe | 1.0000 |

| Case | Repeat | Complete | Steps | Tokens | Failure |
|---|---|---|---|---|---|
| dev-01 | 0 | True | 2 | 2045 | — |
| dev-02 | 0 | True | 2 | 2082 | — |
| dev-03 | 0 | True | 2 | 1998 | — |
| dev-04 | 0 | True | 2 | 2052 | — |
| dev-05 | 0 | True | 2 | 2090 | — |
| dev-06 | 0 | True | 2 | 2225 | — |
| dev-07 | 0 | True | 3 | 3686 | — |
| dev-08 | 0 | True | 3 | 3625 | — |
| dev-09 | 0 | False | 3 | 3687 | soft_failure |
| dev-10 | 0 | True | 3 | 3681 | — |
| dev-11 | 0 | True | 2 | 2179 | — |
| dev-12 | 0 | True | 2 | 2228 | — |
| dev-13 | 0 | True | 2 | 2234 | — |
| dev-14 | 0 | False | 2 | 2166 | soft_failure |
| dev-15 | 0 | True | 2 | 2265 | — |
| dev-16 | 0 | True | 2 | 2013 | — |
| dev-17 | 0 | False | 2 | 1994 | soft_failure |
| dev-18 | 0 | False | 1 | 837 | soft_failure |
| dev-19 | 0 | False | 1 | 878 | soft_failure |
| dev-20 | 0 | True | 1 | 821 | — |
| dev-21 | 0 | True | 1 | 857 | — |
| dev-22 | 0 | True | 1 | 862 | — |
| dev-23 | 0 | True | 1 | 840 | — |
| dev-24 | 0 | False | 2 | 2165 | soft_failure |
| dev-25 | 0 | True | 1 | 835 | — |
| dev-26 | 0 | True | 1 | 826 | — |
| dev-27 | 0 | True | 1 | 836 | — |
| dev-28 | 0 | True | 1 | 828 | — |
| dev-29 | 0 | False | 2 | 2262 | soft_failure |
| dev-30 | 0 | True | 1 | 849 | — |
| dev-31 | 0 | True | 1 | 819 | — |
| dev-32 | 0 | True | 1 | 816 | — |
| dev-33 | 0 | True | 1 | 820 | — |
| dev-34 | 0 | True | 1 | 825 | — |
| dev-35 | 0 | True | 1 | 822 | — |
| dev-01 | 1 | True | 2 | 2045 | — |
| dev-02 | 1 | True | 2 | 2080 | — |
| dev-03 | 1 | True | 2 | 2017 | — |
| dev-04 | 1 | True | 2 | 2025 | — |
| dev-05 | 1 | True | 2 | 2090 | — |
| dev-06 | 1 | True | 2 | 2219 | — |
| dev-07 | 1 | True | 3 | 3694 | — |
| dev-08 | 1 | True | 3 | 3681 | — |
| dev-09 | 1 | False | 7 | 12708 | cascading_soft_failure |
| dev-10 | 1 | True | 3 | 3738 | — |
| dev-11 | 1 | True | 2 | 2179 | — |
| dev-12 | 1 | True | 2 | 2238 | — |
| dev-13 | 1 | False | 2 | 2145 | soft_failure |
| dev-14 | 1 | False | 2 | 2144 | soft_failure |
| dev-15 | 1 | True | 2 | 2206 | — |
| dev-16 | 1 | False | 2 | 2003 | soft_failure |
| dev-17 | 1 | True | 3 | 3333 | — |
| dev-18 | 1 | False | 1 | 837 | soft_failure |
| dev-19 | 1 | False | 2 | 1999 | soft_failure |
| dev-20 | 1 | True | 1 | 839 | — |
| dev-21 | 1 | True | 1 | 858 | — |
| dev-22 | 1 | True | 1 | 860 | — |
| dev-23 | 1 | True | 1 | 840 | — |
| dev-24 | 1 | False | 2 | 2167 | soft_failure |
| dev-25 | 1 | True | 1 | 835 | — |
| dev-26 | 1 | True | 1 | 821 | — |
| dev-27 | 1 | True | 1 | 841 | — |
| dev-28 | 1 | True | 1 | 828 | — |
| dev-29 | 1 | True | 2 | 2142 | — |
| dev-30 | 1 | True | 1 | 855 | — |
| dev-31 | 1 | True | 1 | 819 | — |
| dev-32 | 1 | True | 1 | 816 | — |
| dev-33 | 1 | True | 1 | 820 | — |
| dev-34 | 1 | True | 1 | 823 | — |
| dev-35 | 1 | True | 1 | 822 | — |
| dev-01 | 2 | True | 2 | 2046 | — |
| dev-02 | 2 | True | 2 | 2082 | — |
| dev-03 | 2 | False | 2 | 1997 | soft_failure |
| dev-04 | 2 | True | 2 | 2025 | — |
| dev-05 | 2 | True | 2 | 2090 | — |
| dev-06 | 2 | True | 2 | 2221 | — |
| dev-07 | 2 | True | 3 | 3708 | — |
| dev-08 | 2 | True | 3 | 3692 | — |
| dev-09 | 2 | True | 7 | 11515 | — |
| dev-10 | 2 | True | 3 | 3707 | — |
| dev-11 | 2 | True | 2 | 2189 | — |
| dev-12 | 2 | True | 2 | 2242 | — |
| dev-13 | 2 | True | 2 | 2227 | — |
| dev-14 | 2 | False | 2 | 2147 | soft_failure |
| dev-15 | 2 | True | 2 | 2301 | — |
| dev-16 | 2 | False | 2 | 2003 | soft_failure |
| dev-17 | 2 | True | 3 | 3333 | — |
| dev-18 | 2 | False | 1 | 837 | soft_failure |
| dev-19 | 2 | True | 1 | 0 | hard_failure |
| dev-20 | 2 | True | 1 | 839 | — |
| dev-21 | 2 | True | 1 | 858 | — |
| dev-22 | 2 | True | 1 | 856 | — |
| dev-23 | 2 | True | 1 | 828 | — |
| dev-24 | 2 | False | 2 | 2199 | soft_failure |
| dev-25 | 2 | True | 1 | 834 | — |
| dev-26 | 2 | True | 1 | 821 | — |
| dev-27 | 2 | True | 1 | 834 | — |
| dev-28 | 2 | True | 1 | 834 | — |
| dev-29 | 2 | True | 2 | 2132 | — |
| dev-30 | 2 | True | 1 | 837 | — |
| dev-31 | 2 | True | 1 | 819 | — |
| dev-32 | 2 | True | 1 | 816 | — |
| dev-33 | 2 | True | 1 | 821 | — |
| dev-34 | 2 | True | 1 | 823 | — |
| dev-35 | 2 | True | 1 | 822 | — |
