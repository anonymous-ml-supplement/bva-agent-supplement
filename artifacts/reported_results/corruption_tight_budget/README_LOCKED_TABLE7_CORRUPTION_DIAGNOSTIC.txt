LOCKED RESULT: Table 7 corruption-prone tight-budget diagnostic, exact-top-B150

Case:
  corruption_prone

Policies:
  harm_aware_selective
  uncertainty_only_matched_budget

Seeds:
  20-319

Budget:
  exact B = 150 / 300 for both policies

Purpose:
  This experiment tests whether the corruption_prone slice remains favorable to harm-aware routing under a scarce exact budget.
  It was added because the shared-threshold cross-slice table made harm-aware verify 300/300 in corruption_prone.

Threshold diagnostic result:
  harm-aware verified 300/300 and achieved avg_net_reward 9.200.
  uncertainty-only verified 261/300 and achieved avg_net_reward 5.020.
  This is not a scarce-budget comparison.

Exact-top-B150 construction:
  harm-aware selects top 150 by p_times_H_score.
  uncertainty-only selects top 150 by p_score.
  Tie-break rule: seed ascending.
  Non-selected verified rows were replaced using high thresholds:
    uncertainty_threshold = 1.1
    harm_threshold = 1.1

Replacement rows:
  total = 261
  harm-aware = 150
  uncertainty-only = 111
  all replacements had verify_used = 0

Top-B overlap diagnostic:
  harm selected = 150
  uncertainty selected = 150
  intersection = 150
  union = 150
  Jaccard = 1.0
  Therefore the exact-top-B selected seed sets are identical.

Final exactTopB150 result:
  harm-aware:
    n = 300
    verify_n = 150
    verify_rate = 0.500
    success_rate = 0.590
    irreversible_failure_rate = 0.410
    avg_net_reward = -6.380
    avg_verification_cost = 0.250
    avg_selected_branch_harm = 31.160
    avg_skipped_branch_harm = 31.160

  uncertainty-only:
    n = 300
    verify_n = 150
    verify_rate = 0.500
    success_rate = 0.590
    irreversible_failure_rate = 0.410
    avg_net_reward = -6.380
    avg_verification_cost = 0.250
    avg_selected_branch_harm = 31.160
    avg_skipped_branch_harm = 31.160

Interpretation:
  Under exact tight budget in corruption_prone, harm-aware and uncertainty-only are tied because they select the same top-B seed set.
  This should be reported as a diagnostic or limitation, not as evidence of improvement.
  The likely reason is that corruption_prone makes harm nearly uniformly high, reducing ranking separation for consequence-aware routing.
