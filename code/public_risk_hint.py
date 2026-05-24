#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from typing import Dict, Any

from sandbox_env import load_state, save_state


def attach_public_risk_hint(episode_id: str) -> Dict[str, Any]:
    state = load_state(episode_id)
    rng = random.Random(state["seed"] + 10007)

    case_type = state["case_type"]

    if case_type == "corruption_prone":
        base = 0.68
    elif case_type == "dependency_sensitive":
        base = 0.50
    else:
        base = 0.32

    noise = rng.uniform(-0.28, 0.28)

    public_risk_hint = max(0.0, min(1.0, base + noise))

    state["public_risk_hint"] = round(public_risk_hint, 3)

    if public_risk_hint >= 0.7:
        label = "high"
    elif public_risk_hint >= 0.4:
        label = "medium"
    else:
        label = "low"

    state["public_risk_label"] = label
    save_state(episode_id, state)

    return {
        "status": "ok",
        "episode_id": episode_id,
        "public_risk_hint": state["public_risk_hint"],
        "public_risk_label": state["public_risk_label"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", required=True)
    args = parser.parse_args()

    result = attach_public_risk_hint(args.episode)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
