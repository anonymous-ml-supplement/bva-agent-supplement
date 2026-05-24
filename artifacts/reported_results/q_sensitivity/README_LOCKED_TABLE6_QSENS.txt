LOCKED RESULT: Table 6 q sensitivity, dependency_sensitive, exact-top-B150

Case:
  dependency_sensitive

Policies:
  harm_aware_selective
  uncertainty_only_matched_budget

Seeds:
  20-319

q values:
  0.20
  0.35
  0.50
  0.80

Budget:
  exact B = 150 / 300 for both policies at every q value

Thresholds:
  uncertainty_threshold = 0.457
  harm_threshold = 0.28204125
  random_verify_prob = 0.5

Exact-top-B correction:
  The threshold-based q-sensitivity runs produced:
    harm-aware = 150/300
    uncertainty-only = 151/300
  For each q value, uncertainty-only seed 194 was rerun with:
    uncertainty_threshold = 0.463
  This creates an unverified replacement row and excludes the rank-151 boundary-tie item.
  The final exactTopB150 files should be used for the paper table.

Final exactTopB150 results:

q = 0.20
  harm-aware:
    verify_n = 150
    success_rate = 0.790
    irreversible_failure_rate = 0.210
    avg_net_reward = 3.047
  uncertainty-only:
    verify_n = 150
    success_rate = 0.797
    irreversible_failure_rate = 0.203
    avg_net_reward = 3.007
  reward difference = +0.040

q = 0.35
  harm-aware:
    verify_n = 150
    success_rate = 0.817
    irreversible_failure_rate = 0.183
    avg_net_reward = 3.700
  uncertainty-only:
    verify_n = 150
    success_rate = 0.813
    irreversible_failure_rate = 0.187
    avg_net_reward = 3.455
  reward difference = +0.245

q = 0.50
  harm-aware:
    verify_n = 150
    success_rate = 0.860
    irreversible_failure_rate = 0.140
    avg_net_reward = 4.774
  uncertainty-only:
    verify_n = 150
    success_rate = 0.847
    irreversible_failure_rate = 0.153
    avg_net_reward = 4.302
  reward difference = +0.472

q = 0.80
  harm-aware:
    verify_n = 150
    success_rate = 0.957
    irreversible_failure_rate = 0.043
    avg_net_reward = 7.209
  uncertainty-only:
    verify_n = 150
    success_rate = 0.953
    irreversible_failure_rate = 0.047
    avg_net_reward = 7.093
  reward difference = +0.116

Interpretation:
As verifier quality q increases, both policies improve.
Across all tested q values, harm-aware routing has higher average net reward than uncertainty-only under the same exact verification budget.
The effect is directional and should be reported as robustness/sensitivity evidence, not as a universal significance claim unless bootstrap intervals are later added.
