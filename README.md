# Anonymous Supplementary Package

This package contains the artifacts used for the revised manuscript, **Verify What Matters: Budgeted Verification for Tool-Using Agents under Counterfactual Downstream Harm**.

The package is organized to make the OpenClaw-facing part of the evaluation explicit. The main quantitative tables are reproduced from a controlled agent evaluation with persistent workspace state, proposed tool actions, verifier interventions, downstream rollouts, and matched verification budgets. The `openclaw_interface/` directory contains reset and finalize scripts, prompts, episode templates, runlists, saved embedded trace outputs, and notes documenting the agent-facing workflow.

## Reviewer quick path

Start with these files:

- `docs/REVIEWER_START_HERE.md`: overview of the package and evidence scope.
- `docs/OPENCLAW_ARTIFACT_INDEX.md`: where the OpenClaw-facing interface code and trace artifacts appear.
- `docs/TABLE_TO_ARTIFACT_INDEX.csv`: map from each manuscript table to the corresponding locked artifact folder.
- `docs/CLAIM_TO_EVIDENCE_MAP.md`: map from the revised claims to the completed diagnostics.
- `docs/REPRODUCE_TABLES.md`: table-level reproduction notes.
- `docs/SCOPE_FOR_REVIEWERS.md`: what the controlled OpenClaw-facing evaluation does and does not claim.

## Package structure

- `code/`: sandbox runner, policy runner, aggregation utilities, and OpenClaw-facing helper scripts.
- `runlists/`: policy runlists used for controlled runs.
- `artifacts/reported_results/`: locked artifacts used for the reported manuscript tables.
  - `raw/`: raw per-episode outputs for the main controlled tables.
  - `summaries/`: text summaries for the locked controlled runs.
  - `bootstrap/` and `reported_results/`: bootstrap scripts and confidence-interval summaries.
  - `heldout_seed_split/`: disjoint held-out seed-split diagnostic.
  - `joint_calibration/`: monotone-binning calibration diagnostic.
  - `prm_baseline/`: learned PRM-style routing baselines.
  - `adversarial_relabel/`: harm-cue corruption stress test.
  - `correlated_verifier/`: correlated verifier-failure stress test.
  - `true_heldout_procedural/` and `locked/true_heldout_procedural/`: small true held-out procedural diagnostic.
- `openclaw_interface/`: explicit OpenClaw-facing reset/finalize interface, episode template, prompts, trace results, and trace notes.
- `agent_results/`, `agent_notes/`, `agent_prompts/`, `agent_runlists/`: embedded OpenClaw trace-validation artifacts mirrored for convenience.
- `SHA256SUMS.txt`: checksums for all files in this package.
- `MANIFEST.txt`: complete file list.

## Minimal environment

The controlled diagnostics were implemented with Python 3 and the Python standard library. Some optional plotting scripts may require common scientific Python packages, but the locked tables and summaries are included directly.

A minimal reproduction flow is:

```bash
python3 code/run_policy_episode.py --help
python3 code/run_runlist.py --help
python3 artifacts/reported_results/joint_calibration/make_joint_calibration_table.py --help
```

The exact commands used for individual locked artifacts are recorded in the corresponding logs, README files, and summaries inside each artifact folder. The manuscript tables were produced from the raw CSVs and locked summaries rather than from large intermediate workspace data, which is intentionally not included.

## Scope note

This package supports reproducibility for the controlled OpenClaw-facing agent evaluation used in the manuscript. It includes OpenClaw-facing interface code and embedded trace-validation artifacts. It does not claim to be a full gateway-paired OpenClaw benchmark over unconstrained natural tasks; that broader benchmark is outside the scope of the present revision.
