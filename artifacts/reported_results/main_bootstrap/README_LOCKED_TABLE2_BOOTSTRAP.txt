LOCKED RESULT: Table 2 paired bootstrap confidence intervals

Input:
../raw/revision_table2_dep300_exactTopB150_raw.csv

Comparison:
A = harm_aware_selective
B = uncertainty_only_matched_budget

Paired seeds:
300

Bootstrap:
10,000 paired bootstrap resamples over seed index
random.seed(123)

Result:
net_reward diff A-B = 0.245133
95% CI = [-0.625167, 1.162533]

success diff A-B = 0.003333
95% CI = [-0.026667, 0.033333]

irreversible_failure diff A-B = -0.003333
95% CI = [-0.033333, 0.026667]

Interpretation:
The exact-budget Table 2 result is directionally positive for harm-aware routing, but the 95% CI crosses zero. Therefore the manuscript should not claim statistical significance for this Table 2 net-reward difference.
