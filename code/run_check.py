#!/usr/bin/env python3
import argparse
import json

from sandbox_env import run_check


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", required=True)
    parser.add_argument("--branch", default="main")
    args = parser.parse_args()

    result = run_check(
        episode_id=args.episode,
        branch=args.branch,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
