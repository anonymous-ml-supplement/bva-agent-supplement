import csv
import random
from collections import defaultdict

random.seed(123)

IN = "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_raw.csv"
OUT = "../artifacts/reported_results/table5_ablation_bootstrap_ci.txt"

B = 10000
POLICIES = ["H_only", "p_times_H", "p_only"]
PAIRS = [
    ("H_only", "p_only"),
    ("p_times_H", "p_only"),
    ("H_only", "p_times_H"),
]
METRICS = ["success", "irreversible_failure", "net_reward", "branch_harm_exact"]

def fl(x):
    try:
        return float(x)
    except Exception:
        return 0.0

rows = list(csv.DictReader(open(IN, newline="", encoding="utf-8")))

by_policy_seed = defaultdict(dict)
for r in rows:
    pol = r["policy"]
    seed = int(r["seed"])
    by_policy_seed[pol][seed] = r

common_seeds = sorted(set.intersection(*(set(by_policy_seed[p].keys()) for p in POLICIES)))

def mean_metric(policy, seeds, metric):
    return sum(fl(by_policy_seed[policy][s][metric]) for s in seeds) / len(seeds)

def diff_metric(pa, pb, seeds, metric):
    return mean_metric(pa, seeds, metric) - mean_metric(pb, seeds, metric)

def percentile(xs, q):
    xs = sorted(xs)
    idx = int(round((len(xs)-1) * q))
    return xs[idx]

lines = []
lines.append("Table 5 ablation bootstrap CI")
lines.append(f"Input: {IN}")
lines.append(f"Common paired seeds: {len(common_seeds)}")
lines.append(f"Bootstrap resamples: {B}")
lines.append("")

lines.append("Raw policy means:")
for p in POLICIES:
    verify_n = sum(int(fl(by_policy_seed[p][s]["verify_used"])) for s in common_seeds)
    vals = {m: mean_metric(p, common_seeds, m) for m in METRICS}
    lines.append(
        f"{p}: verify_n={verify_n}, "
        f"success={vals['success']:.6f}, "
        f"irrev={vals['irreversible_failure']:.6f}, "
        f"net_reward={vals['net_reward']:.6f}, "
        f"branch_harm={vals['branch_harm_exact']:.6f}"
    )

lines.append("")
lines.append("Paired bootstrap differences: A - B")
for pa, pb in PAIRS:
    lines.append("")
    lines.append(f"{pa} minus {pb}")
    for metric in METRICS:
        obs = diff_metric(pa, pb, common_seeds, metric)
        boots = []
        n = len(common_seeds)
        for _ in range(B):
            sample = [common_seeds[random.randrange(n)] for __ in range(n)]
            boots.append(diff_metric(pa, pb, sample, metric))
        lo = percentile(boots, 0.025)
        hi = percentile(boots, 0.975)
        lines.append(f"  {metric}: diff={obs:.6f}, 95% CI=[{lo:.6f}, {hi:.6f}]")

open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
print("")
print("Wrote:", OUT)
