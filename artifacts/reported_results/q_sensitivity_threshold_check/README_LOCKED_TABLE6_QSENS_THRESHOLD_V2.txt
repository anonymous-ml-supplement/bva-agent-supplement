LOCKED RESULT: Table 6 q sensitivity threshold-based v2 results before exact-top-B correction

Case:
  dependency_sensitive

Policies:
  uncertainty_only_matched_budget
  harm_aware_selective

Seeds:
  20-319

q values:
  0.20
  0.35
  0.50
  0.80

Thresholds:
  uncertainty_threshold = 0.457
  harm_threshold = 0.28204125
  random_verify_prob = 0.5

Important:
These are threshold-based near-budget results, not final exact-budget results.
In each q setting:
  harm-aware verifies 150/300
  uncertainty-only verifies 151/300

These files are preserved as pre-exact-correction provenance.
Final paper table should use the later exactTopB150 q sensitivity files after deterministic seed-194 replacement.

Near-budget summary:
q=0.20:
  harm-aware reward = 3.047, success = 0.790
  uncertainty-only reward = 3.007, success = 0.797

q=0.35:
  harm-aware reward = 3.700, success = 0.817
  uncertainty-only reward = 3.455, success = 0.813

q=0.50:
  harm-aware reward = 4.774, success = 0.860
  uncertainty-only reward = 4.302, success = 0.847

q=0.80:
  harm-aware reward = 7.209, success = 0.957
  uncertainty-only reward = 7.093, success = 0.953

Interpretation:
Across q values, harm-aware routing is directionally better in average net reward, but this locked folder is only the threshold-based pre-exact-correction record.
