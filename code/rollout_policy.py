#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from typing import Dict, Any, List

from sandbox_env import apply_action, run_check, load_state


def run_default_rollout(episode_id: str) -> Dict[str, Any]:
    """
    A simple fixed continuation policy used for branch comparison.

    Policy:
    1. run_check
    2. if check fails:
         - restore_backup
         - safe_edit
         - run_check again
    3. submit
    """
    trace: List[Dict[str, Any]] = []

    check_1 = run_check(episode_id)
    trace.append({
        "stage": "run_check_1",
        "result": check_1,
    })

    state = load_state(episode_id)

    if state["done"] == 1:
        return {
            "status": "ok",
            "episode_id": episode_id,
            "trace": trace,
            "final_state": state,
            "final_total_reward": state["total_reward"],
        }

    if state["check_passed"] == 0:
        restore = apply_action(episode_id, "restore_backup")
        trace.append({
            "stage": "restore_backup",
            "result": restore,
        })

        state = load_state(episode_id)
        if state["done"] == 0:
            safe = apply_action(episode_id, "safe_edit")
            trace.append({
                "stage": "safe_edit",
                "result": safe,
            })

        state = load_state(episode_id)
        if state["done"] == 0:
            check_2 = run_check(episode_id)
            trace.append({
                "stage": "run_check_2",
                "result": check_2,
            })

    state = load_state(episode_id)
    if state["done"] == 0:
        submit = apply_action(episode_id, "submit")
        trace.append({
            "stage": "submit",
            "result": submit,
        })

    final_state = load_state(episode_id)
    return {
        "status": "ok",
        "episode_id": episode_id,
        "trace": trace,
        "final_state": final_state,
        "final_total_reward": final_state["total_reward"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", required=True)
    args = parser.parse_args()

    result = run_default_rollout(args.episode)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
