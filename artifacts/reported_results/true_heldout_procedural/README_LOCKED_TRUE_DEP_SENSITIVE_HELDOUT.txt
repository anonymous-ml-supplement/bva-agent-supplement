Locked true dep_sensitive_held_out sandbox diagnostic for TMLR revision.

Purpose:
Provide a small true held-out procedural sandbox case, rather than only a held-out seed split within dependency_sensitive.

Code change:
sandbox_env.py was minimally patched to add a new case:
dep_sensitive_held_out

The patch adds:
1. CASE_RISK entry for dep_sensitive_held_out.
2. CASE_PROPERTIES entry for dep_sensitive_held_out.
3. A structural_harm_profile branch with shifted structural-harm cue distribution.
4. Hidden issue detection logic treats dep_sensitive_held_out like dependency_sensitive.

This does not change the already locked dependency_sensitive experiments.

Setup:
case: dep_sensitive_held_out
seeds: 400-499
policies initially run:
p_only
H_only
p_times_H
100 seeds per policy, 300 rows total.

Counterfactual pool:
unverified outcome source: p_only rows, verify_used = 0
verified outcome source: always_verify rows, verify_used = 1

Matched-budget evaluation:
budget: exact top-B = 50 / 100
policies:
p_only_exactTopB50
H_only_exactTopB50
p_times_H_exactTopB50

Main result:
p_only_exactTopB50:
success = 0.860
irreversible_failure = 0.140
avg_net_reward = 4.318

H_only_exactTopB50:
success = 0.840
irreversible_failure = 0.160
avg_net_reward = 4.023875

p_times_H_exactTopB50:
success = 0.840
irreversible_failure = 0.160
avg_net_reward = 3.922

Bootstrap interpretation:
All paired bootstrap confidence intervals cross zero.

p_times_H_exactTopB50 minus p_only_exactTopB50:
success diff = -0.020, 95% CI [-0.070, 0.030]
irreversible_failure diff = +0.020, 95% CI [-0.030, 0.070]
net_reward diff = -0.396, 95% CI [-1.89875, 1.09950]

p_times_H_exactTopB50 minus H_only_exactTopB50:
success diff = 0.000, 95% CI [-0.060, 0.060]
irreversible_failure diff = 0.000, 95% CI [-0.060, 0.060]
net_reward diff = -0.101875, 95% CI [-2.19525, 1.956625]

H_only_exactTopB50 minus p_only_exactTopB50:
success diff = -0.020, 95% CI [-0.100, 0.060]
irreversible_failure diff = +0.020, 95% CI [-0.060, 0.100]
net_reward diff = -0.294125, 95% CI [-2.748375, 2.264375]

Manuscript framing:
This is a small held-out procedural diagnostic. It should not be used to claim p_times_H generalizes best. The correct framing is that p_times_H remains close under a new held-out procedural variant, while p_only is directionally strongest and all differences are statistically inconclusive. This supports a limitation: the advantage of harm-aware routing depends on whether the held-out generator preserves alignment between public risk, harm cues, and downstream consequence.

Recommended wording:
We additionally implemented a small held-out procedural variant, dep_sensitive_held_out, with a shifted structural-harm cue distribution. Under an exact top-B=50/100 matched budget, p_only is directionally strongest, while H_only and p_times_H remain close; paired bootstrap intervals cross zero. We therefore treat this experiment as a diagnostic stress test rather than conclusive evidence of cross-generator dominance.
