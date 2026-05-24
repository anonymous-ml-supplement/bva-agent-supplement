Locked joint calibration analysis for TMLR revision.

Purpose:
Diagnostic held-out split evaluation for calibrated p_times_H routing.

Setup:
Calibration split: dependency_sensitive seeds 20-119, n=100.
Evaluation split: dependency_sensitive seeds 120-319, n=200.
Budget: exact top-B = 100 / 200 verifications.
Calibration method: pure Python monotone binning calibrator, no sklearn dependency.

Policies compared:
p_only_eval
H_only_eval
p_times_H_eval
p_times_H_calibrated_eval

Outcome construction:
The eval split required both verified and unverified outcomes for each seed. Missing outcomes were generated using:
always_verify for missing verified outcomes
no_verify for missing unverified outcomes

Main result:
p_times_H_eval and p_times_H_calibrated_eval both achieve:
success = 0.795
irreversible_failure = 0.205
avg_net_reward = 3.1717

They directionally outperform p_only_eval and H_only_eval on average net reward in this held-out split, but paired bootstrap confidence intervals include zero.

Interpretation:
Calibration changes the selected top-B set, but does not improve aggregate outcome metrics over uncalibrated p_times_H in this split. This should be reported as diagnostic evidence, not as statistically significant evidence.
