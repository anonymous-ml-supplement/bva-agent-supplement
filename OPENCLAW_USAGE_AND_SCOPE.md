# OpenClaw Usage and Evidence Scope

The paper is about budgeted verification for tool-using agents, not a generic toy simulation. OpenClaw enters the package in two ways.

First, the controlled quantitative evaluation uses an OpenClaw-facing sandbox runner. Episodes expose agent-level tool-use structure: persistent workspace state, proposed risky tool actions, hidden execution issues, verifier interventions, corrected actions, downstream rollouts, and reward consequences. This controlled setup is used for the main tables because it enables paired seeds, exact matched verification budgets, and counterfactual branch-harm diagnostics.

Second, the package includes embedded OpenClaw-style trace-validation artifacts. These are collected under `openclaw_interface/`, `agent_results/`, `agent_notes/`, `agent_prompts/`, and `agent_runlists/`. They show how the reset/hint/finalize interface is exercised as an agent workflow with prompts and workspace state.

The manuscript claims a controlled OpenClaw-facing agent evaluation, not a generic toy simulation. The included interface artifacts make OpenClaw's role explicit, while the locked CSVs and scripts make the matched-budget quantitative tables inspectable. A full gateway-paired benchmark over unconstrained natural tasks would be a larger external-validity benchmark. The present claim is narrower and more inspectable: the reported tables reproduce a controlled OpenClaw-facing agent evaluation designed to isolate verification allocation under scarce budget.
