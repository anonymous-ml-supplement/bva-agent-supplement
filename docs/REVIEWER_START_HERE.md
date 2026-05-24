# Reviewer start here

This supplement is organized so that the OpenClaw-facing pieces, table artifacts, and claim boundaries can be inspected without guessing where they are located.

## What this package supports

This package supports the controlled OpenClaw-facing agent evaluation used for the quantitative tables in the manuscript. The evaluation preserves the agent-level structure relevant to the paper: persistent workspace state, proposed tool actions, hidden execution issues, verifier interventions, corrected actions, downstream rollouts, and reward consequences.

The controlled design is intentional. It makes paired-seed and matched-budget comparisons possible, which is the empirical question of the paper. A larger gateway-paired OpenClaw benchmark over unconstrained natural tasks is outside the claim of the revision.

## Fast review path

1. Read `docs/SCOPE_FOR_REVIEWERS.md` for the evidence scope.
2. Read `docs/OPENCLAW_ARTIFACT_INDEX.md` for where OpenClaw-facing interface code and trace artifacts appear.
3. Read `docs/TABLE_TO_ARTIFACT_INDEX.csv` to map each manuscript table to locked artifacts.
4. Use `docs/CLAIM_TO_EVIDENCE_MAP.md` to check that the manuscript claims are bounded by the completed diagnostics.
5. Use `docs/REPRODUCE_TABLES.md` for table-level reproduction notes.

## Main directories

- `code/`: controlled sandbox runner, policy runner, aggregation utilities, and OpenClaw-facing helper scripts.
- `openclaw_interface/`: reset/hint/finalize scripts, episode template, prompts, runlists, saved embedded traces, and interface notes.
- `artifacts/reported_results/`: locked raw CSVs, summaries, and bootstrap outputs for each reported diagnostic.
- `docs/`: reviewer navigation, table-to-artifact mapping, OpenClaw scope, and reproduction notes.
- `config/` and `.env.example`: placeholder configuration files. No private key is included.
