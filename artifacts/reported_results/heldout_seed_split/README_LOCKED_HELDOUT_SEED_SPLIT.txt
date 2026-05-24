Locked held-out seed-split diagnostic for TMLR revision.

Purpose:
Provide a small, honest held-out diagnostic without inventing a new dep_sensitive_held_out sandbox case.

Setup:
Case: dependency_sensitive.
Calibration/training split: seeds 20-119.
Held-out evaluation split: seeds 120-319.
Budget: exact top-B = 100 / 200 verifications.
Source: locked PRM baseline raw table.

Important wording:
This is a disjoint held-out seed-split diagnostic within the dependency-sensitive sandbox.
It is not a separately implemented dep_sensitive_held_out sandbox case.

Policies included:
p_only_eval
H_only_eval
p_times_H_eval
PRM_task_fail_eval
PRM_value_gain_eval

Main result:
p_only_eval:
success = 0.790
irreversible_failure = 0.210
avg_net_reward = 2.87075

H_only_eval:
success = 0.790
irreversible_failure = 0.210
avg_net_reward = 3.09155

p_times_H_eval:
success = 0.795
irreversible_failure = 0.205
avg_net_reward = 3.17170

PRM_task_fail_eval:
success = 0.805
irreversible_failure = 0.195
avg_net_reward = 3.25550

PRM_value_gain_eval:
success = 0.805
irreversible_failure = 0.195
avg_net_reward = 3.32390

Interpretation:
On the disjoint held-out seed split, p_times_H is directionally better than p_only and H_only under the same exact budget. Learned PRM baselines are directionally stronger than fixed p_times_H, but paired bootstrap confidence intervals from the locked PRM baseline analysis cross zero. This should be reported as diagnostic held-out evidence, not as statistically conclusive evidence.

Recommended manuscript framing:
We additionally evaluate on a disjoint held-out seed split within the dependency-sensitive sandbox. Seeds 20-119 are used for calibration or PRM fitting, while seeds 120-319 are reserved for evaluation. This diagnostic does not introduce a new held-out sandbox case, but checks whether the routing trends persist on seeds not used for calibration.
