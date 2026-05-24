LOCKED RESULT: Table 4 cross-slice controlled OpenClaw-facing sandbox evaluation

Cases:
  easy
  dependency_sensitive
  corruption_prone

Policies:
  random_verify_matched_budget
  uncertainty_only_matched_budget
  harm_aware_selective

Seeds:
  20-319

Rows:
  2700 total
  3 cases x 3 policies x 300 seeds

Thresholds:
  uncertainty_threshold = 0.457
  harm_threshold = 0.28204125
  random_verify_prob = 0.5

Important interpretation:
This table is a cross-slice behavior table under shared routing thresholds.
It is not an exact-budget table across all slices.

Key results:
easy:
  harm-aware verifies 0/300 and achieves success 1.000.
  This shows the policy avoids unnecessary verification in benign cases.

dependency_sensitive:
  harm-aware verifies 150/300, success 0.817, avg_net_reward 3.700.
  uncertainty-only verifies 151/300, success 0.813, avg_net_reward 3.455.
  random verifies 157/300, success 0.807, avg_net_reward 3.204.

corruption_prone:
  harm-aware verifies 300/300, success 1.000, avg_net_reward 9.200.
  uncertainty-only verifies 261/300, success 0.890, avg_net_reward 5.020.
  random verifies 157/300, success 0.597, avg_net_reward -6.127.

Held-out note:
The attempted dep_sensitive_held_out case was blocked because the current oc_reset_and_hint.py supports only:
  easy
  dependency_sensitive
  corruption_prone

Therefore held-out should not be claimed unless the environment is extended.
