# Claim-to-evidence map

This file summarizes how the revised manuscript claims should be read against the completed artifacts.

| Manuscript claim | Evidence in package | Safe interpretation |
|---|---|---|
| Local uncertainty alone is an incomplete allocation signal. | Main exact-budget table, component ablation, selected-versus-skipped harm summaries. | Supported as controlled diagnostic evidence in the dependency-sensitive sandbox. |
| Harm-aware routing improves allocation under a fixed budget. | `main_exact_budget` and `main_bootstrap`. | Directional evidence only, because outcome intervals cross zero. |
| Downstream consequence is the dominant signal in this sandbox. | `component_ablation` and `component_ablation_bootstrap`. | H-only is directionally strongest; the uncalibrated product is not claimed to dominate H-only. |
| Verifier quality matters. | `q_sensitivity` and `q_sensitivity_bootstrap`. | Sensitivity diagnostic, not universal dominance. |
| Calibration and PRM-style learned routers are meaningful practical variants. | `table_joint_calibration` and `prm_baseline`. | Calibration changes ranking; PRM-style routers are directional learned baselines with intervals crossing zero. |
| True held-out procedural generalization is limited. | `true_heldout_procedural`. | Small stress test. It is not framed as p times H generalizing best. |
| Harm-cue corruption and correlated verifier failure are real failure modes. | `adversarial_relabel` and `correlated_verifier`. | Supported limitation and stress-test evidence, with degradation intervals excluding zero where reported. |
| The study is OpenClaw-facing agent evaluation rather than a generic toy. | `openclaw_interface/`, embedded trace artifacts, reset/hint/finalize scripts, episode template. | The quantitative evidence is controlled and agent-facing. A larger gateway-paired benchmark is future work. |
