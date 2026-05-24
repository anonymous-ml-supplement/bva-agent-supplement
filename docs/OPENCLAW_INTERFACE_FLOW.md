# OpenClaw-Facing Interface Flow

This supplement is organized so that the agent-facing part of the evaluation is inspectable rather than hidden behind the manuscript text. The main quantitative tables use a controlled OpenClaw-facing sandbox, and the package also includes embedded OpenClaw trace-validation artifacts.

The evaluation flow is:

1. **Reset workspace and inject an episode hint.**
   `openclaw_interface/scripts/oc_reset_and_hint.py` prepares a persistent workspace state and writes the task hint visible to the agent.

2. **Expose an agent-style tool-use decision.**
   Each episode contains a proposed state-changing action, a public uncertainty/risk signal, declared tool metadata, downstream dependency structure, rollback information, and hidden execution issues.

3. **Apply a verification routing policy.**
   The policy chooses whether to verify the eligible action under a fixed verification budget. The implemented policies include uncertainty-only, harm-aware, component ablations, calibrated product routing, PRM-style learned routers, and stress-test variants.

4. **Intervene when verification succeeds.**
   If verification is used and the verifier catches the hidden issue, the proposed action is replaced by the corrected action encoded by the episode.

5. **Finalize and score the trajectory.**
   `openclaw_interface/scripts/oc_finalize_episode.py` evaluates success, irreversible failure, exact branch harm, verification cost, and net reward. The exact branch harm is recorded only for analysis and is not read by the online routing policy.

6. **Aggregate paired, matched-budget results.**
   The runlists and locked summaries preserve paired seeds and exact verification budgets so that policy comparisons isolate allocation quality rather than verification volume.

This design is not a generic toy simulation. It preserves the agent-level structure needed for the paper's question: persistent workspace state, tool actions, hidden execution issues, verifier interventions, corrected actions, downstream rollouts, and reward consequences. A larger gateway-paired OpenClaw benchmark over unconstrained natural tasks is a separate external-validity extension.
