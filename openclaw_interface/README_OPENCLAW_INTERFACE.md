# OpenClaw-facing Interface Artifacts

This directory makes explicit where OpenClaw enters the evaluation package.
The manuscript studies verification allocation for tool-using agents, and the experiments use an OpenClaw-facing agent interface rather than a generic scalar simulator.

## What is included

- `scripts/oc_reset_and_hint.py`: initializes an episode and exposes the agent-visible public risk and structural metadata. This is the reset/hint interface used before the agent or policy decides whether to verify.
- `scripts/oc_finalize_episode.py`: applies the proposed tool action or the verified/corrected action, runs the continuation, and logs success, irreversible failure, reward, verification cost, and exact branch-harm diagnostics.
- `episode_template/ep_oc_harm_smoke_001/`: a minimal OpenClaw-style workspace episode with `main/`, `_env/`, metadata, task text, and state files.
- `prompts/`: prompts used to run embedded OpenClaw-agent trace validation under no-verify, always-verify, uncertainty-only, and harm-aware policies.
- `trace_results/` and `trace_notes/`: saved embedded trace outputs showing that the interface can be exercised through the OpenClaw-style agent workflow.
- `runlists/`: runlists for the embedded trace subset.

## How OpenClaw is used

Each episode is a tool-using agent episode with persistent workspace state. The reset script creates the episode state and returns the agent-visible signals. The policy then chooses whether to call verification before finalizing the risky action. The finalize script applies either the risky action or the corrected action, continues the episode, and records downstream consequences. This is the same interface logic used by the controlled evaluation tables.

The controlled design is intentional. It makes paired-seed, matched-budget comparisons possible, which is the central empirical question of the paper. The package therefore separates two roles:

1. **Quantitative controlled evaluation:** all reported manuscript tables are reproduced from `artifacts/reported_results/`, using the controlled OpenClaw-facing sandbox runner and locked raw outputs.
2. **OpenClaw interface validation:** the files in this directory show how the same reset/finalize interface is exercised in an OpenClaw-style agent workflow with prompts, workspace state, and saved trace outputs.

The revision does not claim to release a full gateway-paired OpenClaw benchmark over unconstrained natural tasks. That broader benchmark is an external-validity extension. The present package is meant to make the OpenClaw-facing controlled evaluation and the embedded OpenClaw trace interface inspectable.

## Minimal interface reproduction

From the package root:

```bash
python3 code/oc_reset_and_hint.py --episode demo_ep --case dependency_sensitive --seed 20
python3 code/oc_finalize_episode.py --episode demo_ep --mode verify_then_decide --action risky_patch --compute-branch-diagnostics always
```

For the embedded trace subset:

```bash
python3 openclaw_interface/scripts/run_agenttrace_dep20_batch.py
```

The exact locked manuscript tables are generated from the artifact folders under `artifacts/reported_results/`; see the top-level README and the artifact-specific README files.
