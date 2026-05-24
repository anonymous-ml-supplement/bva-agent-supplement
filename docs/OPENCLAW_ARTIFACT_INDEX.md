# OpenClaw-facing artifact index

This file makes explicit where OpenClaw-facing components appear in the supplement.

## Interface folder

`openclaw_interface/` contains the reviewer-facing interface artifacts:

- `README_OPENCLAW_INTERFACE.md`: explains how the OpenClaw-facing workflow is used.
- `scripts/oc_reset_and_hint.py`: resets an episode workspace and injects the task hint.
- `scripts/oc_finalize_episode.py`: finalizes an episode and computes success, irreversible failure, exact branch harm, and reward.
- `scripts/run_agenttrace_dep20_batch.py`: runs the embedded trace validation batch.
- `scripts/run_policy_episode.py` and `scripts/run_runlist.py`: connect policy selection to the controlled episode runner.
- `episode_template/ep_oc_harm_smoke_001/`: representative OpenClaw-facing episode template.
- `prompts/`: policy prompts used by the agent-facing workflow.
- `trace_results/` and `trace_notes/`: saved embedded trace outputs and notes.
- `runlists/`: runlists for the interface validation traces.

## Code mirror

Some of the same scripts also appear under `code/` because the controlled sandbox runner imports them from that location. The duplicated placement is intentional: `openclaw_interface/` is for reviewer navigation, while `code/` is for direct execution from the original runner layout.

## Evidence boundary

The quantitative tables are produced by the controlled OpenClaw-facing evaluation artifacts, not by a full gateway-paired OpenClaw benchmark over unconstrained natural tasks. The embedded OpenClaw trace is included to validate interface compatibility and to show where the agent-facing reset, hint, and finalize hooks enter the workflow.
