Locked adversarial relabel analysis for TMLR revision.

Purpose:
Stress-test consequence-aware routing when harm estimates are adversarially corrupted.

Setup:
Evaluation split: dependency_sensitive seeds 120-319, n=200.
Budget: exact top-B = 100 / 200 verifications.
Attack: highest branch_harm_exact seeds have harm_score relabeled to the minimum harm_score in the eval split.
Corruption levels: rho = 0.00, 0.10, 0.25, 0.50.

Policies compared:
p_only_eval
p_times_H_clean_eval
adv_relabel_p_times_H_rho_0.00
adv_relabel_p_times_H_rho_0.10
adv_relabel_p_times_H_rho_0.25
adv_relabel_p_times_H_rho_0.50

Main result:
Clean p_times_H:
success = 0.795
irreversible_failure = 0.205
avg_net_reward = 3.1717

rho = 0.10:
success = 0.740
irreversible_failure = 0.260
avg_net_reward = 1.27275

rho = 0.25:
success = 0.655
irreversible_failure = 0.345
avg_net_reward = -1.276

rho = 0.50:
success = 0.665
irreversible_failure = 0.335
avg_net_reward = -1.06365

Bootstrap interpretation:
Compared with clean p_times_H, all adversarial relabel settings show negative reward differences with 95% confidence intervals below zero. Therefore this table provides strong diagnostic evidence that consequence-aware routing depends on reliable harm estimation.

Manuscript framing:
Use this as a robustness/limitation table. Do not frame it as a failure of the main method under normal conditions. The correct framing is that p_times_H is effective when harm estimates are meaningful, but can degrade sharply under systematic high-harm mislabeling.
