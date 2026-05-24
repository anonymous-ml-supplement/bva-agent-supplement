import csv
from collections import defaultdict

PRM_RAW = "../artifacts/reported_results/prm_baseline/prm_baseline_exactTopB100_eval_raw.csv"
PRM_BOOT = "../artifacts/reported_results/prm_baseline/prm_baseline_exactTopB100_eval_bootstrap_ci.txt"

OUT_SUMMARY = "../artifacts/reported_results/heldout_seed_split/heldout_seed_split_exactTopB100_summary.txt"
OUT_TABLE = "../artifacts/reported_results/heldout_seed_split/heldout_seed_split_exactTopB100_table.csv"
OUT_README = "../artifacts/reported_results/heldout_seed_split/README_HELDOUT_SEED_SPLIT.txt"

POLICIES = [
    "p_only_eval",
    "H_only_eval",
    "p_times_H_eval",
    "PRM_task_fail_eval",
    "PRM_value_gain_eval",
]

def fl(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0

rows = list(csv.DictReader(open(PRM_RAW, newline="", encoding="utf-8")))

by_policy = defaultdict(list)
for r in rows:
    by_policy[r["policy"]].append(r)

table_rows = []
lines = []

lines.append("Held-out seed-split diagnostic")
lines.append("case: dependency_sensitive")
lines.append("cal/training split: seeds 20-119")
lines.append("held-out eval split: seeds 120-319")
lines.append("budget: exact top-B = 100 / 200")
lines.append("source: locked PRM baseline raw table")
lines.append("")
lines.append("Important wording:")
lines.append("This is a disjoint held-out seed-split diagnostic within the dependency-sensitive sandbox.")
lines.append("It is not a separately implemented dep_sensitive_held_out sandbox case.")
lines.append("")

for p in POLICIES:
    rs = by_policy[p]
    if not rs:
        raise RuntimeError(f"Missing policy: {p}")

    n = len(rs)
    verify_n = sum(int(fl(r["verify_used"])) for r in rs)
    success = mean([fl(r["success"]) for r in rs])
    irrev = mean([fl(r["irreversible_failure"]) for r in rs])
    reward = mean([fl(r["net_reward"]) for r in rs])
    cost = mean([fl(r["verification_cost"]) for r in rs])
    selected_harm = mean([fl(r["branch_harm_exact"]) for r in rs if int(fl(r["verify_used"])) == 1])
    skipped_harm = mean([fl(r["branch_harm_exact"]) for r in rs if int(fl(r["verify_used"])) == 0])

    row = {
        "policy": p,
        "n": n,
        "verify_n": verify_n,
        "verify_rate": verify_n / n,
        "success": success,
        "irreversible_failure": irrev,
        "avg_net_reward": reward,
        "avg_verification_cost": cost,
        "avg_selected_branch_harm": selected_harm,
        "avg_skipped_branch_harm": skipped_harm,
    }
    table_rows.append(row)

    lines.append(
        f"{p}: n={n}, verify_n={verify_n}, verify_rate={verify_n/n:.3f}, "
        f"success={success:.3f}, irreversible_failure={irrev:.3f}, "
        f"avg_net_reward={reward:.3f}, avg_verification_cost={cost:.3f}, "
        f"avg_selected_branch_harm={selected_harm:.3f}, avg_skipped_branch_harm={skipped_harm:.3f}"
    )

lines.append("")
lines.append("Interpretation:")
lines.append("On the disjoint held-out seed split, p_times_H_eval is directionally better than p_only_eval and H_only_eval under the same exact budget.")
lines.append("The learned PRM baselines are directionally stronger than fixed p_times_H, but paired bootstrap confidence intervals in the locked PRM baseline analysis cross zero.")
lines.append("Therefore this table should be reported as diagnostic held-out evidence, not as statistically conclusive evidence.")
lines.append("")
lines.append("Recommended manuscript wording:")
lines.append("We additionally evaluate on a disjoint held-out seed split within the dependency-sensitive sandbox. Seeds 20-119 are used for calibration or PRM fitting, while seeds 120-319 are reserved for evaluation. This diagnostic does not introduce a new held-out sandbox case, but checks whether the routing trends persist on seeds not used for calibration.")
lines.append("")

with open(OUT_TABLE, "w", newline="", encoding="utf-8") as f:
    fieldnames = list(table_rows[0].keys())
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(table_rows)

with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

with open(OUT_README, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
    f.write("\nSource bootstrap file:\n")
    f.write(PRM_BOOT + "\n")

print("\n".join(lines))
print("Wrote:")
print(OUT_TABLE)
print(OUT_SUMMARY)
print(OUT_README)
