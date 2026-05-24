import csv
import random
from collections import defaultdict

random.seed(123)

BASE_RAW = "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_raw.csv"
REPL_RAW = "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_replacements_raw.csv"
JOINT_MISSING_RAW = "../artifacts/reported_results/joint_calibration/joint_calibration_missing_outcomes_raw.csv"
PRM_CAL_MISSING_RAW = "../artifacts/reported_results/prm_baseline/prm_cal_missing_outcomes_raw.csv"

OUT_RAW = "../artifacts/reported_results/correlated_verifier/correlated_verifier_exactTopB100_eval_raw.csv"
OUT_DECISIONS = "../artifacts/reported_results/correlated_verifier/correlated_verifier_exactTopB100_eval_decisions.csv"
OUT_SUMMARY = "../artifacts/reported_results/correlated_verifier/correlated_verifier_exactTopB100_eval_summary.txt"

EVAL_SEEDS = list(range(120, 320))
BUDGET = 100

# Verifier settings.
UNIFORM_Q = 0.35
Q_HIGH = 0.60
Q_LOW = 0.10
HIGH_HARM_FRAC = 0.25

def fl(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def read_csv(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0

def stable_u(seed, tag):
    # deterministic pseudo-random number in [0,1)
    rnd = random.Random(f"{tag}_{seed}_revision")
    return rnd.random()

all_rows = []
for p in [BASE_RAW, REPL_RAW, JOINT_MISSING_RAW, PRM_CAL_MISSING_RAW]:
    part = read_csv(p)
    print("Loaded", len(part), "rows from", p)
    all_rows.extend(part)

base_rows = read_csv(BASE_RAW)
feature_rows = {}
for r in base_rows:
    if r["policy"] == "p_times_H":
        feature_rows[int(r["seed"])] = r

pool = defaultdict(lambda: defaultdict(list))
for r in all_rows:
    s = int(r["seed"])
    v = int(fl(r["verify_used"]))
    pool[s][v].append(r)

def canonical(seed, verify):
    rows = pool[seed][verify]
    if not rows:
        raise RuntimeError(f"Missing outcome for seed={seed}, verify={verify}")

    if verify == 0:
        preferred = [r for r in rows if r["policy"] == "no_verify"]
    else:
        preferred = [r for r in rows if r["policy"] == "always_verify"]

    cand = preferred if preferred else rows
    cand = sorted(cand, key=lambda r: r.get("episode_id", ""))
    return dict(cand[0])

for s in EVAL_SEEDS:
    if s not in feature_rows:
        raise RuntimeError(f"Missing feature row for seed {s}")
    if 0 not in pool[s] or 1 not in pool[s]:
        raise RuntimeError(f"Missing outcome pair for seed {s}")

eval_records = []
for s in EVAL_SEEDS:
    fr = feature_rows[s]
    eval_records.append({
        "seed": s,
        "p_score": fl(fr["p_score"]),
        "harm_score": fl(fr["harm_score"]),
        "p_times_H_score": fl(fr["p_times_H_score"]),
        "branch_harm_exact": fl(fr["branch_harm_exact"]),
    })

# First select by clean p_times_H exact top-B.
ranked_clean = sorted(eval_records, key=lambda r: (-r["p_times_H_score"], r["seed"]))
selected_clean = set(r["seed"] for r in ranked_clean[:BUDGET])

# Define hard/high-harm subset among selected seeds.
selected_records = [r for r in eval_records if r["seed"] in selected_clean]
n_hard = int(round(HIGH_HARM_FRAC * len(selected_records)))
hard_selected = set(
    r["seed"] for r in sorted(selected_records, key=lambda r: (-r["branch_harm_exact"], r["seed"]))[:n_hard]
)

policy_specs = [
    ("p_times_H_uniform_q0p35", "uniform"),
    ("p_times_H_correlated_qhard0p10_qeasy0p60", "correlated"),
]

raw_out = []
decisions_out = []
summary_lines = []

summary_lines.append("Correlated verifier failure exact-top-B evaluation")
summary_lines.append("eval split: seeds 120-319")
summary_lines.append("budget: exact top-B = 100 / 200 by clean p_times_H")
summary_lines.append(f"uniform verifier q = {UNIFORM_Q}")
summary_lines.append(f"correlated verifier: hard selected top {HIGH_HARM_FRAC:.2f} by branch_harm_exact use q_low={Q_LOW}, others use q_high={Q_HIGH}")
summary_lines.append("")

for policy_name, mode in policy_specs:
    for rank, rec in enumerate(ranked_clean, start=1):
        s = rec["seed"]
        selected = 1 if s in selected_clean else 0

        if selected:
            if mode == "uniform":
                q = UNIFORM_Q
            else:
                q = Q_LOW if s in hard_selected else Q_HIGH
            detected = 1 if stable_u(s, policy_name) < q else 0
        else:
            q = 0.0
            detected = 0

        # If selected and verifier detects the issue, use verified/corrected outcome.
        # If selected but verifier misses, fall back to unverified outcome while still paying verification cost.
        if selected and detected:
            chosen = canonical(s, 1)
        else:
            chosen = canonical(s, 0)

        chosen = dict(chosen)
        chosen["policy"] = policy_name
        chosen["episode_id"] = f"revision_corrver_eval_{policy_name}_s{s}"
        chosen["verify_used"] = str(selected)
        chosen["corrected"] = str(detected)
        chosen["verification_cost"] = "0.5" if selected else "0.0"
        chosen["net_reward"] = str(fl(chosen["realized_reward"]) - (0.5 if selected else 0.0))
        chosen["policy_score"] = str(rec["p_times_H_score"])
        chosen["random_verify_prob"] = str(q)
        chosen["notes"] = (
            f"Correlated verifier eval policy={policy_name}; selected={selected}; "
            f"detected={detected}; q={q}; hard_selected={1 if s in hard_selected else 0}."
        )
        raw_out.append(chosen)

        decisions_out.append({
            "policy": policy_name,
            "seed": s,
            "rank": rank,
            "selected_topB": selected,
            "detected": detected,
            "q": q,
            "hard_selected": 1 if s in hard_selected else 0,
            "p_score": rec["p_score"],
            "harm_score": rec["harm_score"],
            "p_times_H_score": rec["p_times_H_score"],
            "branch_harm_exact": rec["branch_harm_exact"],
        })

    pol_rows = [r for r in raw_out if r["policy"] == policy_name]
    n = len(pol_rows)
    verify_n = sum(int(fl(r["verify_used"])) for r in pol_rows)
    corrected_n = sum(int(fl(r["corrected"])) for r in pol_rows)
    success = mean([fl(r["success"]) for r in pol_rows])
    irrev = mean([fl(r["irreversible_failure"]) for r in pol_rows])
    reward = mean([fl(r["net_reward"]) for r in pol_rows])
    detected_rate = corrected_n / verify_n if verify_n else 0.0

    hard_rows = [d for d in decisions_out if d["policy"] == policy_name and int(d["hard_selected"]) == 1]
    hard_detected = sum(int(d["detected"]) for d in hard_rows)
    hard_detect_rate = hard_detected / len(hard_rows) if hard_rows else 0.0

    summary_lines.append(
        f"{policy_name}: n={n}, verify_n={verify_n}, corrected_n={corrected_n}, "
        f"detected_rate={detected_rate:.3f}, hard_detect_rate={hard_detect_rate:.3f}, "
        f"success={success:.3f}, irreversible_failure={irrev:.3f}, avg_net_reward={reward:.3f}"
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

print()
print("\n".join(summary_lines))
print()
print("Wrote:")
print(OUT_RAW)
print(OUT_DECISIONS)
print(OUT_SUMMARY)
