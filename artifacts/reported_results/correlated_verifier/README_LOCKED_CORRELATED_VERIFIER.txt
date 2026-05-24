Locked correlated verifier failure analysis for TMLR revision.

Purpose:
Stress-test whether average verifier quality is sufficient when verifier failures are correlated with high-harm cases.

Setup:
Evaluation split: dependency_sensitive seeds 120-319, n=200.
Budget: exact top-B = 100 / 200 by clean p_times_H.
Uniform verifier: q = 0.35.
Correlated verifier:
- hard selected cases are the top 25% selected seeds by branch_harm_exact
- hard selected cases use q_low = 0.10
- other selected cases use q_high = 0.60

Policies compared:
p_times_H_uniform_q0p35
p_times_H_correlated_qhard0p10_qeasy0p60

Main result:
Uniform q=0.35:
corrected_n = 38
detected_rate = 0.380
success = 0.685
irreversible_failure = 0.315
avg_net_reward = -0.70685

Correlated verifier:
corrected_n = 43
detected_rate = 0.430
success = 0.640
irreversible_failure = 0.360
avg_net_reward = -2.12510

Bootstrap interpretation:
Correlated verifier failure is worse than uniform verifier despite a higher overall corrected count.
Paired bootstrap differences, correlated minus uniform:
success diff = -0.045, 95% CI [-0.090, -0.005]
irreversible_failure diff = +0.045, 95% CI [0.005, 0.085]
net_reward diff = -1.41825, 95% CI [-2.73745, -0.12930]
corrected diff = +0.025, 95% CI [-0.045, 0.095]

Manuscript framing:
Use this as a robustness/limitation table. Average verifier detection rate is not enough. If verifier failures are correlated with high-harm cases, consequence-aware routing can degrade even when the overall correction rate is comparable or higher.
