# Quick Start

The locked CSVs and summaries needed for the manuscript are already included. A reviewer can audit the revision at three levels.

## Level 1: Verify reported numbers from locked summaries

Open the table map:

```bash
cat docs/REPRODUCE_TABLES.md
```

Then inspect the corresponding `*_summary.txt` and `*_bootstrap_ci.txt` files under `artifacts/reported_results/`.

## Level 2: Inspect the controlled sandbox runner

```bash
python3 code/run_policy_episode.py --help
python3 code/run_runlist.py --help
```

These scripts implement the controlled OpenClaw-facing policy evaluation used by the runlists and raw outputs.

## Level 3: Inspect the OpenClaw-facing interface artifacts

```bash
cat docs/OPENCLAW_INTERFACE_FLOW.md
cat openclaw_interface/README_OPENCLAW_INTERFACE.md
ls openclaw_interface/scripts
ls openclaw_interface/trace_results
```

The OpenClaw-facing artifacts show the reset/hint/finalize workflow, prompts, episode template, runlists, and saved embedded traces used for interface validation.

## Optional live trace validation

The controlled tables do not require a live LLM API call. To run optional embedded trace validation, copy `.env.example` to `.env`, set a local API key, and adapt `config/example_config.yaml` to the local OpenClaw installation. Do not place private keys in files submitted for review.
