LOCKED RESULT: Table 5 component ablation, dependency_sensitive, exact-top-B150

Case:
  dependency_sensitive

Policies:
  p_only
  H_only
  p_times_H

Seeds:
  20-319

Budget:
  exact B = 150 / 300 for every policy

Construction:
  p_only selects top 150 by p_score.
  H_only selects top 150 by harm_score.
  p_times_H selects top 150 by p_times_H_score.
  Boundary and excess verified rows were corrected by deterministic top-B replacement.

Replacement rows:
  total replacements = 142
  H_only replacements = 141
  p_only replacements = 1
  p_times_H replacements = 0
  all replacements had verify_used = 0

Final result:
H_only:
  n = 300
  verify_n = 150
  verify_rate = 0.500
  success_rate = 0.827
  irreversible_failure_rate = 0.173
  avg_net_reward = 4.065
  avg_verification_cost = 0.250
  avg_selected_branch_harm = 12.320
  avg_skipped_branch_harm = 10.269

p_only:
  n = 300
  verify_n = 150
  verify_rate = 0.500
  success_rate = 0.813
  irreversible_failure_rate = 0.187
  avg_net_reward = 3.455
  avg_verification_cost = 0.250
  avg_selected_branch_harm = 11.100
  avg_skipped_branch_harm = 11.490

p_times_H:
  n = 300
  verify_n = 150
  verify_rate = 0.500
  success_rate = 0.817
  irreversible_failure_rate = 0.183
  avg_net_reward = 3.700
  avg_verification_cost = 0.250
  avg_selected_branch_harm = 11.590
  avg_skipped_branch_harm = 10.999

Interpretation:
Under an exact matched verification budget, H_only performs best in this sandbox.
p_times_H improves over p_only, but does not outperform H_only.
The manuscript should state that downstream harm is the dominant routing signal in this controlled setting, and that the available uncertainty estimate adds limited marginal ranking value beyond harm.
