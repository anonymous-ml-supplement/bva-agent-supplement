Locked PRM baseline analysis for TMLR revision.

Purpose:
Diagnostic learned baseline comparing fixed transparent p_times_H routing against lightweight PRM-style learned scores.

Setup:
Calibration split: dependency_sensitive seeds 20-119, n=100.
Evaluation split: dependency_sensitive seeds 120-319, n=200.
Budget: exact top-B = 100 / 200 verifications.
Model: pure Python logistic regression with standardized tabular features, no sklearn dependency.

Features:
p_score
harm_score
p_times_H_score
downstream_dependency_count
rollback_difficulty
persistent_state_risk
downstream_failure_penalty

Policies compared:
p_only_eval
H_only_eval
p_times_H_eval
PRM_task_fail_eval
PRM_value_gain_eval

PRM targets:
PRM_task_fail predicts unverified failure.
PRM_value_gain predicts normalized positive reward gain from verification.

Main result:
p_times_H_eval:
success = 0.795
irreversible_failure = 0.205
avg_net_reward = 3.1717

PRM_task_fail_eval:
success = 0.805
irreversible_failure = 0.195
avg_net_reward = 3.2555

PRM_value_gain_eval:
success = 0.805
irreversible_failure = 0.195
avg_net_reward = 3.3239

Interpretation:
The learned PRM baselines directionally outperform fixed p_times_H on this held-out split, but paired bootstrap confidence intervals include zero. This should be reported as diagnostic evidence. The manuscript should not claim that p_times_H is stronger than learned PRM baselines. The safer framing is that p_times_H is transparent, non-learned, and competitive, while learned PRM can improve directionally when counterfactual calibration labels are available.
