#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

SLICE_ABBR = {
    "dependency_sensitive": "dep",
    "discordant": "disc",
    "concordant": "con",
    "low_risk": "low",
    "corruption_prone": "cor",
}

POLICY_ABBR = {
    "no_verify": "noverify",
    "always_verify": "always",
    "uncertainty_only": "uncertainty",
    "uncertainty_only_default": "uncertainty_default",
    "uncertainty_only_matched_budget": "uncertainty_matched",
    "harm_aware_selective": "harm",
    "random_matched_cost": "random",
    "random_verify_matched_budget": "random_matched",
    "p_only": "p_only",
    "H_only": "H_only",
    "p_times_H": "pH",
    "p_times_H_minus_cost": "pH_cost",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slices", nargs="+", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--policies", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--prefix", default="oc")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "episode_id",
        "case",
        "slice_name",
        "seed",
        "policy",
        "status",
    ]

    rows = []
    for slice_name in args.slices:
        s_abbr = SLICE_ABBR.get(slice_name, slice_name[:4])
        for seed in args.seeds:
            for policy in args.policies:
                p_abbr = POLICY_ABBR.get(policy, policy)
                episode_id = f"{args.prefix}_{s_abbr}_s{seed}_{p_abbr}"
                rows.append({
                    "episode_id": episode_id,
                    "case": slice_name,
                    "slice_name": slice_name,
                    "seed": seed,
                    "policy": policy,
                    "status": "pending",
                })

    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out}")

if __name__ == "__main__":
    main()
