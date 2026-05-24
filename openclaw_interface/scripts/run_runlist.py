#!/usr/bin/env python3
import argparse
import csv
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runlist", required=True)
    parser.add_argument("--summary-csv", required=True)
    parser.add_argument("--random-verify-prob", type=float, default=0.5)
    parser.add_argument("--uncertainty-threshold", type=float, default=0.60)
    parser.add_argument("--harm-threshold", type=float, default=0.45)
    parser.add_argument("--max-runs", type=int, default=None)
    parser.add_argument("--skip-done", action="store_true")
    args = parser.parse_args()

    code_dir = Path(__file__).resolve().parent
    runlist = Path(args.runlist)
    summary_csv = Path(args.summary_csv)

    with open(runlist, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    n_run = 0
    for row in rows:
        if args.max_runs is not None and n_run >= args.max_runs:
            break

        if args.skip_done and row.get("status") == "done":
            continue

        episode_id = row["episode_id"]
        case = row["case"]
        policy = row["policy"]
        seed = row["seed"]

        cmd = [
            sys.executable,
            str(code_dir / "run_policy_episode.py"),
            "--episode", episode_id,
            "--case", case,
            "--policy", policy,
            "--seed", str(seed),
            "--summary-csv", str(summary_csv),
            "--runlist-csv", str(runlist),
            "--random-verify-prob", str(args.random_verify_prob),
        ]

        # These args will work after Step 3 patch.
        cmd += [
            "--uncertainty-threshold", str(args.uncertainty_threshold),
            "--harm-threshold", str(args.harm_threshold),
        ]

        print("\n=== RUNNING ===")
        print(" ".join(cmd))

        try:
            subprocess.run(cmd, check=True)
            n_run += 1
        except subprocess.CalledProcessError as e:
            print(f"\nERROR: run failed for {episode_id}", file=sys.stderr)
            print(e, file=sys.stderr)
            raise

    print(f"\nCompleted {n_run} runs.")

if __name__ == "__main__":
    main()
