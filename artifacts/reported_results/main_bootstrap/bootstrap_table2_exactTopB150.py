import csv
import random
from collections import defaultdict

random.seed(123)

path = "../artifacts/reported_results/raw/revision_table2_dep300_exactTopB150_raw.csv"
out_path = "../artifacts/reported_results/bootstrap/revision_table2_dep300_exactTopB150_bootstrap.txt"

rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))

A = "harm_aware_selective"
B = "uncertainty_only_matched_budget"

by_seed = defaultdict(dict)
for r in rows:
    by_seed[int(r["seed"])][r["policy"]] = r

valid = sorted([s for s in by_seed if A in by_seed[s] and B in by_seed[s]])

def fl(x):
    return float(x)

def paired_diff(metric, seeds):
    vals = []
    for s in seeds:
        vals.append(fl(by_seed[s][A][metric]) - fl(by_seed[s][B][metric]))
    return sum(vals) / len(vals)

def bootstrap(metric, R=10000):
    obs = paired_diff(metric, valid)
    vals = []
    n = len(valid)
    for _ in range(R):
        sample = [random.choice(valid) for _ in range(n)]
        vals.append(paired_diff(metric, sample))
    vals.sort()
    lo = vals[int(0.025 * R)]
    hi = vals[int(0.975 * R)]
    return obs, lo, hi

metrics = [
    "net_reward",
    "success",
    "irreversible_failure",
    "verification_cost",
    "branch_harm_exact",
]

lines = []
lines.append(f"paired seeds = {len(valid)}")
lines.append(f"A = {A}")
lines.append(f"B = {B}")
lines.append("")
lines.append("metric,obs_diff_A_minus_B,ci95_low,ci95_high")

for m in metrics:
    obs, lo, hi = bootstrap(m)
    lines.append(f"{m},{obs:.6f},{lo:.6f},{hi:.6f}")

text = "\n".join(lines)
print(text)

with open(out_path, "w", encoding="utf-8") as f:
    f.write(text + "\n")
