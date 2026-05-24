LOCKED RESULT: Table 2 dependency_sensitive exact-budget B=150, n=300 per policy

Final raw CSV:
revision_table2_dep300_exactTopB150_raw.csv

Final summary:
revision_table2_dep300_exactTopB150_summary.txt

Final result:
harm_aware_selective:
  n = 300
  verify_n = 150
  verify_rate = 0.500
  success_rate = 0.817
  irreversible_failure_rate = 0.183
  avg_net_reward = 3.700
  avg_verification_cost = 0.250
  avg_selected_branch_harm = 11.590
  avg_skipped_branch_harm = 10.999

uncertainty_only_matched_budget:
  n = 300
  verify_n = 150
  verify_rate = 0.500
  success_rate = 0.813
  irreversible_failure_rate = 0.187
  avg_net_reward = 3.455
  avg_verification_cost = 0.250
  avg_selected_branch_harm = 11.100
  avg_skipped_branch_harm = 11.490

Interpretation:
Under the same exact verification budget, harm-aware selective verification has higher average net reward and slightly higher success rate than uncertainty-only verification.

Provenance:
1. Initial diagnostic run used thresholds:
   uncertainty_threshold = 0.422000
   harm_threshold = 0.291537
   This produced non-exact budgets:
   harm-aware = 143/300
   uncertainty-only = 171/300

2. Near-budget rerun used:
   uncertainty_threshold = 0.457
   harm_threshold = 0.28204125
   This produced:
   harm-aware = 150/300
   uncertainty-only = 151/300

3. Exact top-B correction:
   uncertainty-only had a boundary tie at p_score = 0.457.
   Rank 150 = seed 110, selected.
   Rank 151 = seed 194, excluded by deterministic tie-break.
   Seed 194 was rerun with uncertainty_threshold = 0.463 to create an unverified replacement row.
   The final exactTopB150 CSV replaces only the uncertainty-only seed 194 row from the near-B150 CSV.

Important:
Use revision_table2_dep300_exactTopB150_raw.csv and revision_table2_dep300_exactTopB150_summary.txt as the final locked Table 2 source.
Do not use revision_table2_dep300_exactB150_raw.csv as final Table 2 because it is only the old-threshold diagnostic run.
Do not use revision_table2_dep300_nearB150_raw.csv as final Table 2 because uncertainty-only verifies 151/300.

3. Exact top-B correction:
   uncertainty-only had a boundary tie at p_score = 0.457.
   Rank 150 = seed 110, selected.
   Rank 151 = seed 194, excluded by deterministic tie-break.
   Seed 194 was rerun with uncertainty_threshold = 0.463 to create an unverified replacement row.
   The final exactTopB150 CSV replaces only the uncertainty-only seed 194 row from the near-B150 CSV.

Important:
Use revision_table2_dep300_exactTopB150_raw.csv and revision_table2_dep300_exactTopB150_summary.txt as the final locked Table 2 source.
Do not use revision_table2_dep300_exactB150_raw.csv as final Table 2 because it is only the old-threshold diagnostic run.
Do not use revision_table2_dep300_nearB150_raw.csv as final Table 2 because uncertainty-only verifies 151/300.
