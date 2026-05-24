#!/usr/bin/env python3
import argparse
import csv
import math
from collections import defaultdict

def fl(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def threshold_for_top_budget(scores, target_rate):
    """
    Return threshold so approximately target_rate fraction of scores verify.
    verify iff score >= threshold.
    """
    scores = sorted(scores, reverse=True)
    n = len(scores)
    if n == 0:
        return 1.0
    k = max(1, int(round(target_rate * n)))
    k = min(k, n)
    return scores[k - 1]

def verify_rate(scores, threshold):
    if not scores:
        return 0.0
    return sum(1 for s in scores if s >= threshold) / len(scores)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-csv", required=True)
    parser.add_argument("--target-rate", type=float, default=0.50)
    args = parser.parse_args()

    rows = []
    with open(args.summary_csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Use all rows, but de-duplicate by episode_id base information if repeated policies exist.
    # Scores are reset-derived, so p_score and p_times_H_score are identical across policies
    # for the same seed/case.
    seen = set()
    examples = []
    for r in rows:
        key = (r.get("case"), r.get("seed"))
        if key in seen:
            continue
        seen.add(key)
        examples.append(r)

    p_scores = [fl(r["p_score"]) for r in examples]
    ph_scores = [fl(r["p_times_H_score"]) for r in examples]

    u_thr = threshold_for_top_budget(p_scores, args.target_rate)
    h_thr = threshold_for_top_budget(ph_scores, args.target_rate)

    print("Calibration examples:", len(examples))
    print(f"Target verify rate: {args.target_rate:.3f}")
    print(f"uncertainty_threshold={u_thr:.6f}")
    print(f"harm_threshold={h_thr:.6f}")
    print(f"random_verify_prob={args.target_rate:.6f}")
    print(f"actual_uncertainty_verify_rate={verify_rate(p_scores, u_thr):.3f}")
    print(f"actual_harm_verify_rate={verify_rate(ph_scores, h_thr):.3f}")

if __name__ == "__main__":
    main()
