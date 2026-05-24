import csv
import random
from collections import defaultdict

random.seed(123)

BASE = "../artifacts/reported_results/q_sensitivity"
OUT = "../artifacts/reported_results/table6_qsens_bootstrap_ci.txt"

N_BOOT = 10000
METRICS = [
    "success",
    "irreversible_failure",
    "net_reward",
    "branch_harm_exact",
]

FILES = [
    ("0.20", f"{BASE}/revision_table6_qsens_dep300_q0p20_exactTopB150_raw.csv"),
    ("0.35", f"{BASE}/revision_table6_qsens_dep300_q0p35_exactTopB150_raw.csv"),
    ("0.50", f"{BASE}/revision_table6_qsens_dep300_q0p50_exactTopB150_raw.csv"),
    ("0.80", f"{BASE}/revision_table6_qsens_dep300_q0p80_exactTopB150_raw.csv"),
]

A = "harm_aware_selective"
B = "uncertainty_only_matched_budget"

def fl(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def percentile(xs, q):
    xs = sorted(xs)
    idx = int(round((len(xs) - 1) * q))
    return xs[idx]

def mean_metric(by_policy_seed, policy, seeds, metric):
    return sum(fl(by_policy_seed[policy][s][metric]) for s in seeds) / len(seeds)

def diff_metric(by_policy_seed, seeds, metric):
    return mean_metric(by_policy_seed, A, seeds, metric) - mean_metric(by_policy_seed, B, seeds, metric)

lines = []
lines.append("Table 6 q-sensitivity bootstrap CI")
lines.append("Difference = harm_aware_selective minus uncertainty_only_matched_budget")
lines.append(f"Bootstrap resamples: {N_BOOT}")
lines.append("")

for q, path in FILES:
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))

    by_policy_seed = defaultdict(dict)
    for r in rows:
        by_policy_seed[r["policy"]][int(r["seed"])] = r

    common_seeds = sorted(set(by_policy_seed[A].keys()) & set(by_policy_seed[B].keys()))
    n = len(common_seeds)

    lines.append("=" * 72)
    lines.append(f"q = {q}")
    lines.append(f"Input: {path}")
    lines.append(f"Common paired seeds: {n}")
    lines.append("")

    for pol in [A, B]:
        verify_n = sum(int(fl(by_policy_seed[pol][s]["verify_used"])) for s in common_seeds)
        success = mean_metric(by_policy_seed, pol, common_seeds, "success")
        irrev = mean_metric(by_policy_seed, pol, common_seeds, "irreversible_failure")
        reward = mean_metric(by_policy_seed, pol, common_seeds, "net_reward")

        selected = [
            fl(by_policy_seed[pol][s]["branch_harm_exact"])
            for s in common_seeds
            if int(fl(by_policy_seed[pol][s]["verify_used"])) == 1
        ]
        sel_harm = sum(selected) / len(selected) if selected else 0.0

        lines.append(
            f"{pol}: verify_n={verify_n}, "
            f"success={success:.6f}, "
            f"irrev={irrev:.6f}, "
            f"net_reward={reward:.6f}, "
            f"selected_branch_harm={sel_harm:.6f}"
        )

    lines.append("")
    lines.append("Paired bootstrap differences:")
    for metric in METRICS:
        obs = diff_metric(by_policy_seed, common_seeds, metric)
        boots = []
        for _ in range(N_BOOT):
            sample = [common_seeds[random.randrange(n)] for __ in range(n)]
            boots.append(diff_metric(by_policy_seed, sample, metric))
        lo = percentile(boots, 0.025)
        hi = percentile(boots, 0.975)
        lines.append(f"  {metric}: diff={obs:.6f}, 95% CI=[{lo:.6f}, {hi:.6f}]")

    lines.append("")

open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
print("Wrote:", OUT)
