#!/usr/bin/env python3
import argparse
import json

from sandbox_env import init_episode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", required=True, help="Episode ID, e.g. ep001")
    parser.add_argument(
        "--case",
        required=True,
        choices=["easy", "dependency_sensitive", "corruption_prone"],
        help="Hidden case type"
    )
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    result = init_episode(
        episode_id=args.episode,
        case_type=args.case,
        seed=args.seed,
        overwrite=True,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
