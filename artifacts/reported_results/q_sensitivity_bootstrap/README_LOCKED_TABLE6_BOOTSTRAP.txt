Locked Table 6 bootstrap analysis.

Purpose:
Paired bootstrap confidence intervals for Table 6 q-sensitivity on dependency_sensitive.

Input files:
../artifacts/reported_results/q_sensitivity/revision_table6_qsens_dep300_q0p20_exactTopB150_raw.csv
../artifacts/reported_results/q_sensitivity/revision_table6_qsens_dep300_q0p35_exactTopB150_raw.csv
../artifacts/reported_results/q_sensitivity/revision_table6_qsens_dep300_q0p50_exactTopB150_raw.csv
../artifacts/reported_results/q_sensitivity/revision_table6_qsens_dep300_q0p80_exactTopB150_raw.csv

Policies:
harm_aware_selective
uncertainty_only_matched_budget

Seeds:
300 paired seeds for each q value.

Budget:
Exact top-B = 150 / 300 verifications for both policies.

Bootstrap:
10000 paired bootstrap resamples over seed index.

Interpretation:
Harm-aware routing has higher average net reward across all tested q values, but the paired bootstrap confidence intervals include zero. At q=0.20, harm-aware has slightly lower success and slightly higher irreversible failure than uncertainty-only. Therefore the manuscript should not claim that harm-aware improves all metrics at all q. The safe claim is that the reward direction is consistently positive, while success and irreversible-failure differences are small and not statistically significant in this controlled run.
