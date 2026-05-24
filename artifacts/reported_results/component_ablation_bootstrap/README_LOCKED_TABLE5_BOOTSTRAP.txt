Locked Table 5 bootstrap analysis.

Purpose:
Paired bootstrap confidence intervals for the Table 5 component ablation on dependency_sensitive.

Input:
../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_raw.csv

Policies:
H_only
p_times_H
p_only

Seeds:
300 paired seeds.

Bootstrap:
10000 paired bootstrap resamples over seed index.

Interpretation:
H_only > p_times_H > p_only directionally in success and average net reward, but all reported paired bootstrap confidence intervals for success, irreversible failure, and net reward cross zero. Therefore this analysis should be described as directional rather than statistically significant.
