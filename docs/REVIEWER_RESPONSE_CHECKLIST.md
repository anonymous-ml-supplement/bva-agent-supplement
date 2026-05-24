# Reviewer-response checklist

This checklist maps the earlier reviewer concerns to the revised evidence and supplement artifacts.

| Reviewer concern | Where addressed |
|---|---|
| Four-episode pilot is too small. | Main tables now use controlled n=300 cells where applicable, plus n=200 held-out seed diagnostics and n=100 true held-out procedural stress test. |
| Selective policies had mismatched verify rates. | Exact-budget tables enforce the same top-B verification count across competing policies. |
| Practical estimation of p, H, and q was unclear. | Manuscript Section 3.5, Section 3.6, Table 1, plus `docs/OPENCLAW_INTERFACE_FLOW.md` and `config/example_config.yaml`. |
| Placeholders prevented verification. | Locked artifact folders, raw CSVs, summaries, bootstrap files, table-to-artifact index, and checksums are included. |
| OpenClaw usage was unclear. | `openclaw_interface/` and `docs/OPENCLAW_ARTIFACT_INDEX.md`. |
| Reproducibility was insufficient. | `README.md`, `docs/QUICK_START.md`, `docs/REPRODUCE_TABLES.md`, `docs/TABLE_TO_ARTIFACT_INDEX.csv`, `MANIFEST.txt`, and `SHA256SUMS.txt`. |
| Harm cue reliability was not stress-tested. | `adversarial_relabel` and `correlated_verifier`. |
| Claims were too strong relative to evidence. | `docs/CLAIM_TO_EVIDENCE_MAP.md` records the conservative interpretation for each diagnostic. |
