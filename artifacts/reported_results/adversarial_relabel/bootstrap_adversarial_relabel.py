import csv
import random
from collections import defaultdict

random.seed(123)

IN = "../artifacts/reported_results/adversarial_relabel/adversarial_relabel_exactTopB100_eval_raw.csv"
OUT = "../artifacts/reported_results/adversarial_relabel/adversarial_relabel_exactTopB100_eval_bootstrap_ci.txt"

N_BOOT = 10000

POLICIES = [
    "p_only_eval",
    "p_times_H_clean_eval",
    "adv_relabel_p_times_H_rho_0.00",
    "adv_relabel_p_times_H_rho_0.10",
    "adv_relabel_p_times_H_rho_0.25",
    "adv_relabel_p_times_H_rho_0.50",
]

PAIRS = [
    ("p_times_H_clean_eval", "p_only_eval"),
    ("adv_relabel_p_times_H_rho_0.10", "p_times_H_clean_eval"),
    ("adv_relabel_p_times_H_rho_0.25", "p_times_H_clean_eval"),
    ("adv_relabel_p_times_H_rho_0.50", "p_times_H_clean_eval"),
    ("adv_relabel_p_times_H_rho_0.10", "p_only_eval"),
    ("adv_relabel_p_times_H_rho_0.25", "p_only_eval"),
    ("adv_relabel_p_times_H_rho_0.50", "p_only_eval"),
]

METRICS = [
    "success",
    "irreversible_failure",
    "net_reward",
    "branch_harm_exact",
]

def fl(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def percentile(xs, q):
    xs = sorted(xs)
    idx = int(round((len(xs) - 1) * q))
    return xs[idx]

rows = list(csv.DictReader(open(IN, newline="", encoding="utf-8")))

by_policy_seed = defaultdict(dict)
for r in rows:
    by_policy_seed[r["policy"]][int(r["seed"])] = r

common_seeds = sorted(set.intersection(*(set(by_policy_seed[p].keys()) for p in POLICIES)))

def mean_metric(policy, seeds, metric):
    return sum(fl(by_policy_seed[policy][s][metric]) for s in seeds) / len(seeds)

def diff_metric(pa, pb, seeds, metric):
    return mean_metric(pa, seeds, metric) - mean_metric(pb, seeds, metric)

lines = []
lines.append("Adversarial relabel exactTopB100 eval bootstrap CI")
lines.append(f"Input: {IN}")
lines.append("eval split: seeds 120-319")
lines.append("budget: exact top-B = 100 / 200")
lines.append("attack: highest branch_harm_exact seeds have harm_score relabeled to minimum eval harm_score")
lines.append(f"Common paired seeds: {len(common_seeds)}")
lines.append(f"Bootstrap resamples: {N_BOOT}")
lines.append("")

lines.append("Raw policy means:")
for p in POLICIES:
    verify_n = sum(int(fl(by_policy_seed[p][s]["verify_used"])) for s in common_seeds)
    success = mean_metric(p, common_seeds, "success")
    irrev = mean_metric(p, common_seeds, "irreversible_failure")
    reward = mean_metric(p, common_seeds, "net_reward")
    harm = mean_metric(p, common_seeds, "branch_harm_exact")
    lines.append(
        f"{p}: verify_n={verify_n}, success={success:.6f}, "
        f"irrev={irrev:.6f}, net_reward={reward:.6f}, branch_harm={harm:.6f}"
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
        for _ in range(N_BOOT):
            sample = [common_seeds[random.randrange(n)] for __ in range(n)]
            boots.append(diff_metric(pa, pb, sample, metric))
        lo = percentile(boots, 0.025)
        hi = percentile(boots, 0.975)
        lines.append(f"  {metric}: diff={obs:.6f}, 95% CI=[{lo:.6f}, {hi:.6f}]")

open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
print("")
print("Wrote:", OUT)
