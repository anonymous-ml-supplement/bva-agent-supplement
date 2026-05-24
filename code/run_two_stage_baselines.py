#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from sandbox_env import EPISODES_DIR, init_episode, apply_action, load_state
from rollout_policy import run_default_rollout
from branch_replay import run_branch_replay
from public_risk_hint import attach_public_risk_hint


BRANCH_VERIFY_COST = 1.0


def cleanup_branch_clones(source_episode: str) -> None:
    for suffix in ["__branch_unverified", "__branch_verified"]:
        path = EPISODES_DIR / f"{source_episode}{suffix}"
        if path.exists():
            shutil.rmtree(path)


def summarize_policy(records: List[Dict[str, Any]], policy_name: str) -> Dict[str, Any]:
    n = len(records)
    avg_net_reward = sum(r["net_reward"] for r in records) / n
    avg_realized_reward = sum(r["realized_reward"] for r in records) / n
    success_rate = sum(r["success"] for r in records) / n
    failure_rate = 1.0 - success_rate
    irreversible_failure_rate = sum(r["irreversible_failure"] for r in records) / n
    gate_trigger_rate = sum(r["gate_triggered"] for r in records) / n
    verify_rate = sum(r["verified"] for r in records) / n
    avg_verification_cost = sum(r["verification_cost"] for r in records) / n
    correction_rate = sum(r["corrected"] for r in records) / n
    avg_public_risk_hint = sum(r["public_risk_hint"] for r in records) / n
    avg_impact_estimate = sum(r["impact_estimate"] for r in records) / n

    return {
        "policy": policy_name,
        "episodes": n,
        "avg_net_reward": round(avg_net_reward, 4),
        "avg_realized_reward": round(avg_realized_reward, 4),
        "success_rate": round(success_rate, 4),
        "failure_rate": round(failure_rate, 4),
        "irreversible_failure_rate": round(irreversible_failure_rate, 4),
        "gate_trigger_rate": round(gate_trigger_rate, 4),
        "verify_rate": round(verify_rate, 4),
        "avg_verification_cost": round(avg_verification_cost, 4),
        "correction_rate": round(correction_rate, 4),
        "avg_public_risk_hint": round(avg_public_risk_hint, 4),
        "avg_impact_estimate": round(avg_impact_estimate, 4),
    }


def format_summary_table(rows: List[Dict[str, Any]]) -> str:
    headers = [
        "policy",
        "episodes",
        "avg_net_reward",
        "avg_realized_reward",
        "success_rate",
        "failure_rate",
        "irreversible_failure_rate",
        "gate_trigger_rate",
        "verify_rate",
        "avg_verification_cost",
        "correction_rate",
        "avg_public_risk_hint",
        "avg_impact_estimate",
    ]

    widths = {}
    for h in headers:
        widths[h] = max(len(h), max(len(str(row[h])) for row in rows))

    def fmt_row(row: Dict[str, Any]) -> str:
        return " | ".join(str(row[h]).ljust(widths[h]) for h in headers)

    sep = "-+-".join("-" * widths[h] for h in headers)
    lines = [fmt_row({h: h for h in headers}), sep]
    for row in rows:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def run_single_episode(
    policy_name: str,
    case_type: str,
    seed: int,
    episode_id: str,
    gate_threshold: float,
    impact_threshold: float,
) -> Dict[str, Any]:
    init_episode(episode_id=episode_id, case_type=case_type, seed=seed, overwrite=True)

    apply_action(episode_id, "inspect_files")

    hint_info = attach_public_risk_hint(episode_id)
    public_risk_hint = float(hint_info["public_risk_hint"])
    gate_triggered = int(public_risk_hint >= gate_threshold)

    verified = 0
    verification_cost = 0.0
    corrected = 0
    impact_estimate = 0.0

    # Default candidate proposed by the agent/environment
    chosen_action = "risky_patch"

    if policy_name == "no_verify":
        chosen_action = "risky_patch"

    elif policy_name == "always_branch_verify":
        verified = 1
        verification_cost = BRANCH_VERIFY_COST

        replay = run_branch_replay(
            source_episode=episode_id,
            candidate_action="risky_patch",
            corrected_action="safe_edit",
        )
        impact_estimate = float(replay["impact_summary"]["impact"])

        if impact_estimate > impact_threshold:
            chosen_action = "safe_edit"
            corrected = 1
        else:
            chosen_action = "risky_patch"

        cleanup_branch_clones(episode_id)

    elif policy_name == "cheap_gate_then_branch_harm":
        if gate_triggered:
            verified = 1
            verification_cost = BRANCH_VERIFY_COST

            replay = run_branch_replay(
                source_episode=episode_id,
                candidate_action="risky_patch",
                corrected_action="safe_edit",
            )
            impact_estimate = float(replay["impact_summary"]["impact"])

            if impact_estimate > impact_threshold:
                chosen_action = "safe_edit"
                corrected = 1
            else:
                chosen_action = "risky_patch"

            cleanup_branch_clones(episode_id)
        else:
            chosen_action = "risky_patch"

    else:
        raise ValueError(f"Unknown policy: {policy_name}")

    apply_action(episode_id, chosen_action)
    rollout = run_default_rollout(episode_id)
    final_state = load_state(episode_id)

    realized_reward = float(final_state["total_reward"])
    net_reward = realized_reward - verification_cost

    return {
        "policy": policy_name,
        "episode_id": episode_id,
        "case_type": case_type,
        "seed": seed,
        "public_risk_hint": public_risk_hint,
        "gate_triggered": gate_triggered,
        "verified": verified,
        "verification_cost": verification_cost,
        "impact_estimate": impact_estimate,
        "chosen_action": chosen_action,
        "corrected": corrected,
        "realized_reward": realized_reward,
        "net_reward": net_reward,
        "success": int(final_state["success"]),
        "done": int(final_state["done"]),
        "metadata_corrupted": int(final_state["metadata_corrupted"]),
        "irreversible_failure": int(final_state["irreversible_failure"]),
        "final_state": final_state,
        "rollout": rollout,
    }


def build_case_list(case_mode: str) -> List[str]:
    if case_mode == "mixed":
        return ["easy", "dependency_sensitive", "corruption_prone"]
    if case_mode in {"easy", "dependency_sensitive", "corruption_prone"}:
        return [case_mode]
    raise ValueError(f"Unsupported case_mode: {case_mode}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes-per-case", type=int, default=20)
    parser.add_argument(
        "--case-mode",
        default="mixed",
        choices=["mixed", "easy", "dependency_sensitive", "corruption_prone"],
    )
    parser.add_argument(
        "--policies",
        nargs="+",
        default=[
            "no_verify",
            "always_branch_verify",
            "cheap_gate_then_branch_harm",
        ],
        choices=[
            "no_verify",
            "always_branch_verify",
            "cheap_gate_then_branch_harm",
        ],
    )
    parser.add_argument("--gate-threshold", type=float, default=0.40)
    parser.add_argument("--impact-threshold", type=float, default=3.0)
    parser.add_argument("--seed-start", type=int, default=0)
    args = parser.parse_args()

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"two_stage_baselines_{timestamp}"
    run_dir = logs_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    cases = build_case_list(args.case_mode)

    all_records: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []

    for policy_name in args.policies:
        policy_records: List[Dict[str, Any]] = []

        for case_type in cases:
            for i in range(args.episodes_per_case):
                seed = args.seed_start + i
                episode_id = f"{run_name}__{policy_name}__{case_type}__{i:03d}"

                record = run_single_episode(
                    policy_name=policy_name,
                    case_type=case_type,
                    seed=seed,
                    episode_id=episode_id,
                    gate_threshold=args.gate_threshold,
                    impact_threshold=args.impact_threshold,
                )
                policy_records.append(record)
                all_records.append(record)

        summary_rows.append(summarize_policy(policy_records, policy_name))

    summary_table = format_summary_table(summary_rows)
    print(summary_table)
    print()
    print(json.dumps(summary_rows, indent=2))

    with (run_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary_rows, f, indent=2)

    with (run_dir / "records.json").open("w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)

    with (run_dir / "summary.txt").open("w", encoding="utf-8") as f:
        f.write(summary_table + "\n\n")
        f.write(json.dumps(summary_rows, indent=2))

    print()
    print(f"Saved outputs to: {run_dir}")


if __name__ == "__main__":
    main()
