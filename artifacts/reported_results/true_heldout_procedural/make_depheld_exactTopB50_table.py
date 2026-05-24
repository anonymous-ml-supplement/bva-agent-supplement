import csv
from collections import defaultdict

POLICY_RAW = "../artifacts/reported_results/true_heldout_procedural/dep_sensitive_heldout_policies_raw.csv"
ALWAYS_RAW = "../artifacts/reported_results/true_heldout_procedural/depheld_always_verify_raw.csv"

OUT_RAW = "../artifacts/reported_results/true_heldout_procedural/depheld_exactTopB50_eval_raw.csv"
OUT_DECISIONS = "../artifacts/reported_results/true_heldout_procedural/depheld_exactTopB50_eval_decisions.csv"
OUT_SUMMARY = "../artifacts/reported_results/true_heldout_procedural/depheld_exactTopB50_eval_summary.txt"

SEEDS = list(range(400, 500))
BUDGET = 50

POLICIES = [
    ("p_only_exactTopB50", "p_score"),
    ("H_only_exactTopB50", "harm_score"),
    ("p_times_H_exactTopB50", "p_times_H_score"),
]

def fl(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0

def read_csv(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

policy_rows = read_csv(POLICY_RAW)
always_rows = read_csv(ALWAYS_RAW)

# feature rows use p_times_H rows, because each seed has all relevant score columns.
feature_rows = {}
for r in policy_rows:
    if r["policy"] == "p_times_H":
        feature_rows[int(r["seed"])] = r

# unverified outcome from p_only, verified outcome from always_verify
unverified = {}
for r in policy_rows:
    if r["policy"] == "p_only":
        unverified[int(r["seed"])] = r

verified = {}
for r in always_rows:
    if r["policy"] == "always_verify":
        verified[int(r["seed"])] = r

missing = []
for s in SEEDS:
    if s not in feature_rows:
        missing.append((s, "feature"))
    if s not in unverified:
        missing.append((s, "unverified"))
    if s not in verified:
        missing.append((s, "verified"))

if missing:
    raise RuntimeError(f"Missing entries: {missing[:20]}")

records = []
for s in SEEDS:
    fr = feature_rows[s]
    records.append({
        "seed": s,
        "p_score": fl(fr["p_score"]),
        "harm_score": fl(fr["harm_score"]),
        "p_times_H_score": fl(fr["p_times_H_score"]),
        "branch_harm_exact": fl(fr["branch_harm_exact"]),
    })

raw_out = []
decisions_out = []
summary_lines = []

summary_lines.append("dep_sensitive_held_out exact-top-B evaluation")
summary_lines.append("case: dep_sensitive_held_out")
summary_lines.append("seeds: 400-499")
summary_lines.append("budget: exact top-B = 50 / 100")
summary_lines.append("comparison: p_only, H_only, p_times_H under matched verification budget")
summary_lines.append("verified outcome source: always_verify")
summary_lines.append("unverified outcome source: p_only")
summary_lines.append("")

for policy_name, score_col in POLICIES:
    ranked = sorted(records, key=lambda r: (-r[score_col], r["seed"]))
    selected = set(r["seed"] for r in ranked[:BUDGET])

    for rank, rec in enumerate(ranked, start=1):
        s = rec["seed"]
        is_sel = 1 if s in selected else 0
        chosen = dict(verified[s] if is_sel else unverified[s])

        chosen["episode_id"] = f"revision_depheld_exactTopB50_{policy_name}_s{s}"
        chosen["case"] = "dep_sensitive_held_out"
        chosen["policy"] = policy_name
        chosen["verify_used"] = str(is_sel)
        chosen["policy_score"] = str(rec[score_col])
        chosen["notes"] = (
            f"dep_sensitive_held_out exact top-B={BUDGET}/100; "
            f"policy={policy_name}; score_col={score_col}; selected={is_sel}."
        )
        raw_out.append(chosen)

        decisions_out.append({
            "policy": policy_name,
            "seed": s,
            "rank": rank,
            "score_col": score_col,
            "score": rec[score_col],
            "selected_topB": is_sel,
            "p_score": rec["p_score"],
            "harm_score": rec["harm_score"],
            "p_times_H_score": rec["p_times_H_score"],
            "branch_harm_exact": rec["branch_harm_exact"],
        })

    pol_rows = [r for r in raw_out if r["policy"] == policy_name]
    n = len(pol_rows)
    verify_n = sum(int(fl(r["verify_used"])) for r in pol_rows)
    success = mean([fl(r["success"]) for r in pol_rows])
    irrev = mean([fl(r["irreversible_failure"]) for r in pol_rows])
    reward = mean([fl(r["net_reward"]) for r in pol_rows])
    cost = mean([fl(r["verification_cost"]) for r in pol_rows])
    selected_harm = mean([fl(r["branch_harm_exact"]) for r in pol_rows if int(fl(r["verify_used"])) == 1])
    skipped_harm = mean([fl(r["branch_harm_exact"]) for r in pol_rows if int(fl(r["verify_used"])) == 0])

    summary_lines.append(
        f"{policy_name}: n={n}, verify_n={verify_n}, verify_rate={verify_n/n:.3f}, "
        f"success={success:.3f}, irreversible_failure={irrev:.3f}, "
        f"avg_net_reward={reward:.3f}, avg_verification_cost={cost:.3f}, "
        f"avg_selected_branch_harm={selected_harm:.3f}, avg_skipped_branch_harm={skipped_harm:.3f}"
    )

with open(OUT_RAW, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(raw_out[0].keys()))
    w.writeheader()
    w.writerows(raw_out)

with open(OUT_DECISIONS, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(decisions_out[0].keys()))
    w.writeheader()
    w.writerows(decisions_out)

with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines) + "\n")

print("\n".join(summary_lines))
print()
print("Wrote:")
print(OUT_RAW)
print(OUT_DECISIONS)
print(OUT_SUMMARY)
