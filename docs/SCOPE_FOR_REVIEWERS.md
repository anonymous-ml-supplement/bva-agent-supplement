# Evidence Scope for Reviewers

This supplement is intended to make the revised empirical claims inspectable.

The manuscript's quantitative claims are based on a controlled OpenClaw-facing agent evaluation. The controlled setting is used because the empirical question is allocation under scarce verification: policies must be compared on paired seeds, matched verification budgets, and common outcome definitions. The setup preserves the agent-level structure relevant to the paper, including persistent workspace state, proposed tool actions, hidden execution issues, verifier interventions, corrected actions, downstream rollouts, and reward consequences.

The package also includes an `openclaw_interface/` folder with reset/hint/finalize scripts, prompts, an episode template, runlists, and saved embedded trace outputs. These artifacts document how OpenClaw-style agent workflow enters the evaluation.

The supplement does not claim to be a full gateway-paired benchmark over unconstrained natural tasks. Such a benchmark would be valuable for external validity, but it would answer a broader question. The present revision focuses on the mechanism and reproducibility of budgeted verification allocation under controlled, matched-budget conditions.
