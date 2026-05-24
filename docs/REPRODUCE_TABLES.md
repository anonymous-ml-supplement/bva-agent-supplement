# Table-to-Artifact Reproduction Map

This file maps the manuscript tables to the locked artifacts included in this supplement. The table numbering follows the revised manuscript. Paths are relative to the package root.

## Main text tables

### Table 2: Exact-budget dependency-sensitive evaluation
- Locked artifact: `artifacts/reported_results/main_exact_budget/`
- Summary: `revision_table2_dep300_exactTopB150_summary.txt`
- Raw per-episode output: `revision_table2_dep300_exactTopB150_raw.csv`
- Bootstrap artifact: `artifacts/reported_results/main_bootstrap/`
- Bootstrap summary: `revision_table2_dep300_exactTopB150_bootstrap.txt`

### Table 3: Cross-slice behavior under shared thresholds
- Locked artifact: `artifacts/reported_results/cross_slice/`
- Runlist: `revision_table4_cross_slice_300_runlist.csv`
- Raw output: `revision_table4_cross_slice_300_raw.csv`
- Summary: `revision_table4_cross_slice_300_summary.txt`

### Table 4: Component ablation of routing signals
- Locked artifact: `artifacts/reported_results/component_ablation/`
- Runlist: `revision_table5_ablation_dep300_runlist.csv`
- Raw output: `revision_table5_ablation_exactTopB150_raw.csv`
- Summary: `revision_table5_ablation_exactTopB150_summary.txt`
- Bootstrap artifact: `artifacts/reported_results/component_ablation_bootstrap/`
- Bootstrap summary: `table5_ablation_bootstrap_ci.txt`

### Table 5: Verifier-quality sensitivity
- Locked artifact: `artifacts/reported_results/q_sensitivity/`
- Summary collection: `revision_table6_q_sensitivity_exactTopB150_all_summaries.txt`
- q-specific raw outputs: `revision_table6_qsens_dep300_q0p20_exactTopB150_raw.csv`, `revision_table6_qsens_dep300_q0p35_exactTopB150_raw.csv`, `revision_table6_qsens_dep300_q0p50_exactTopB150_raw.csv`, `revision_table6_qsens_dep300_q0p80_exactTopB150_raw.csv`
- Bootstrap artifact: `artifacts/reported_results/q_sensitivity_bootstrap/`
- Bootstrap summary: `table6_qsens_bootstrap_ci.txt`

### Table 6: Joint-calibration diagnostic
- Locked artifact: `artifacts/reported_results/joint_calibration/`
- Main script: `make_joint_calibration_table.py`
- Raw output: `joint_calibration_exactTopB100_eval_raw.csv`
- Decisions: `joint_calibration_exactTopB100_eval_decisions.csv`
- Summary: `joint_calibration_exactTopB100_eval_summary.txt`
- Bootstrap summary: `joint_calibration_exactTopB100_eval_bootstrap_ci.txt`

### Table 7: Learned PRM-style routing baselines
- Locked artifact: `artifacts/reported_results/prm_baseline/`
- Main script: `make_prm_baseline_table.py`
- Raw output: `prm_baseline_exactTopB100_eval_raw.csv`
- Decisions: `prm_baseline_exactTopB100_eval_decisions.csv`
- Summary: `prm_baseline_exactTopB100_eval_summary.txt`
- Bootstrap summary: `prm_baseline_exactTopB100_eval_bootstrap_ci.txt`

### Table 8: Small true held-out procedural diagnostic
- Locked artifact: `artifacts/reported_results/true_heldout_procedural/`
- Main script: `make_depheld_exactTopB50_table.py`
- Patched environment files: `sandbox_env_with_dep_sensitive_heldout.py`, `oc_reset_and_hint_with_dep_sensitive_heldout.py`
- Raw output: `depheld_exactTopB50_eval_raw.csv`
- Decisions: `depheld_exactTopB50_eval_decisions.csv`
- Summary: `depheld_exactTopB50_eval_summary.txt`
- Bootstrap summary: `depheld_exactTopB50_eval_bootstrap_ci.txt`

### Table 9: Adversarial relabel stress test
- Locked artifact: `artifacts/reported_results/adversarial_relabel/`
- Main script: `make_adversarial_relabel_table.py`
- Raw output: `adversarial_relabel_exactTopB100_eval_raw.csv`
- Decisions: `adversarial_relabel_exactTopB100_eval_decisions.csv`
- Summary: `adversarial_relabel_exactTopB100_eval_summary.txt`
- Bootstrap summary: `adversarial_relabel_exactTopB100_eval_bootstrap_ci.txt`

### Table 10: Correlated verifier-failure sensitivity
- Locked artifact: `artifacts/reported_results/correlated_verifier/`
- Main script: `make_correlated_verifier_table.py`
- Raw output: `correlated_verifier_exactTopB100_eval_raw.csv`
- Decisions: `correlated_verifier_exactTopB100_eval_decisions.csv`
- Summary: `correlated_verifier_exactTopB100_eval_summary.txt`
- Bootstrap summary: `correlated_verifier_exactTopB100_eval_bootstrap_ci.txt`

## Appendix tables and diagnostics

### Held-out seed-split diagnostic
- Locked artifact: `artifacts/reported_results/heldout_seed_split/`
- Script: `make_heldout_seed_split_table.py`
- Table CSV: `heldout_seed_split_exactTopB100_table.csv`
- Summary: `heldout_seed_split_exactTopB100_summary.txt`

### Tight-budget corruption-prone diagnostic
- Locked artifact: `artifacts/reported_results/corruption_tight_budget/`
- Raw output: `revision_table7_corruption_tightB150_exactTopB150_raw.csv`
- Summary: `revision_table7_corruption_tightB150_exactTopB150_summary.txt`

### Embedded OpenClaw trace validation
- Interface directory: `openclaw_interface/`
- Reset/finalize scripts: `openclaw_interface/scripts/oc_reset_and_hint.py`, `openclaw_interface/scripts/oc_finalize_episode.py`
- Episode template: `openclaw_interface/episode_template/ep_oc_harm_smoke_001/`
- Trace results: `openclaw_interface/trace_results/`
- Trace notes: `openclaw_interface/trace_notes/`
