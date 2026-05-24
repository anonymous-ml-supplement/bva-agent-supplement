import csv
import math
from collections import defaultdict

BASE_RAW = "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_raw.csv"
REPL_RAW = "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_replacements_raw.csv"
JOINT_MISSING_RAW = "../artifacts/reported_results/joint_calibration/joint_calibration_missing_outcomes_raw.csv"
PRM_CAL_MISSING_RAW = "../artifacts/reported_results/prm_baseline/prm_cal_missing_outcomes_raw.csv"

OUT_RAW = "../artifacts/reported_results/prm_baseline/prm_baseline_exactTopB100_eval_raw.csv"
OUT_DECISIONS = "../artifacts/reported_results/prm_baseline/prm_baseline_exactTopB100_eval_decisions.csv"
OUT_SUMMARY = "../artifacts/reported_results/prm_baseline/prm_baseline_exactTopB100_eval_summary.txt"

CAL_SEEDS = set(range(20, 120))
EVAL_SEEDS = set(range(120, 320))
BUDGET = 100

FEATURES = [
    "p_score",
    "harm_score",
    "p_times_H_score",
    "downstream_dependency_count",
    "rollback_difficulty",
    "persistent_state_risk",
    "downstream_failure_penalty",
]

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

def sigmoid(z):
    if z < -40:
        return 0.0
    if z > 40:
        return 1.0
    return 1.0 / (1.0 + math.exp(-z))

def standardize_train_eval(X_train, X_eval):
    cols = len(X_train[0])
    mu, sd = [], []
    for j in range(cols):
        vals = [x[j] for x in X_train]
        m = mean(vals)
        v = mean([(x - m) ** 2 for x in vals])
        s = math.sqrt(v) if v > 1e-12 else 1.0
        mu.append(m)
        sd.append(s)

    def trans(X):
        return [[(row[j] - mu[j]) / sd[j] for j in range(cols)] for row in X]

    return trans(X_train), trans(X_eval), mu, sd

def fit_logistic_soft(X, y, lr=0.05, epochs=3000, l2=1e-3):
    n = len(X)
    d = len(X[0])
    w = [0.0] * (d + 1)  # bias + features

    for _ in range(epochs):
        grad = [0.0] * (d + 1)
        for xi, yi in zip(X, y):
            z = w[0] + sum(w[j+1] * xi[j] for j in range(d))
            p = sigmoid(z)
            err = p - yi
            grad[0] += err
            for j in range(d):
                grad[j+1] += err * xi[j]

        grad[0] /= n
        for j in range(1, d + 1):
            grad[j] = grad[j] / n + l2 * w[j]

        for j in range(d + 1):
            w[j] -= lr * grad[j]

    return w

def predict_logistic(w, X):
    d = len(w) - 1
    out = []
    for xi in X:
        z = w[0] + sum(w[j+1] * xi[j] for j in range(d))
        out.append(sigmoid(z))
    return out

# Load data.
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

# outcome pool
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

# completeness check
for name, seeds in [("cal", CAL_SEEDS), ("eval", EVAL_SEEDS)]:
    miss = []
    for s in sorted(seeds):
        if s not in feature_rows:
            miss.append((s, "feature"))
        if 0 not in pool[s]:
            miss.append((s, "unverified"))
        if 1 not in pool[s]:
            miss.append((s, "verified"))
    if miss:
        raise RuntimeError(f"{name} split missing entries: {miss[:20]}")
    print(name, "split complete:", len(seeds), "seeds")

# Build train/eval features.
def get_features(seed):
    r = feature_rows[seed]
    return [fl(r[c]) for c in FEATURES]

train_seeds = sorted(CAL_SEEDS)
eval_seeds = sorted(EVAL_SEEDS)

X_train_raw = [get_features(s) for s in train_seeds]
X_eval_raw = [get_features(s) for s in eval_seeds]
X_train, X_eval, mu, sd = standardize_train_eval(X_train_raw, X_eval_raw)

# Labels:
# PRM_task_fail predicts whether the unverified path fails.
# PRM_value_gain predicts normalized reward gain from verification over no verification as a soft label.
task_fail_y = []
value_gain_raw = []
for s in train_seeds:
    u = canonical(s, 0)
    v = canonical(s, 1)
    task_fail_y.append(1.0 - fl(u["success"]))
    value_gain_raw.append(max(0.0, fl(v["net_reward"]) - fl(u["net_reward"])))

max_gain = max(value_gain_raw) if value_gain_raw else 1.0
if max_gain <= 1e-12:
    max_gain = 1.0
value_gain_y = [g / max_gain for g in value_gain_raw]

w_task = fit_logistic_soft(X_train, task_fail_y)
w_value = fit_logistic_soft(X_train, value_gain_y)

score_task_eval = predict_logistic(w_task, X_eval)
score_value_eval = predict_logistic(w_value, X_eval)

eval_records = []
for s, st, sv in zip(eval_seeds, score_task_eval, score_value_eval):
    fr = feature_rows[s]
    eval_records.append({
        "seed": s,
        "p_score": fl(fr["p_score"]),
        "harm_score": fl(fr["harm_score"]),
        "p_times_H_score": fl(fr["p_times_H_score"]),
        "prm_task_fail_score": st,
        "prm_value_gain_score": sv,
    })

policies = [
    ("p_only_eval", "p_score"),
    ("H_only_eval", "harm_score"),
    ("p_times_H_eval", "p_times_H_score"),
    ("PRM_task_fail_eval", "prm_task_fail_score"),
    ("PRM_value_gain_eval", "prm_value_gain_score"),
]

raw_out = []
decisions_out = []
summary_lines = []

summary_lines.append("PRM baseline exact-top-B evaluation")
summary_lines.append("cal split: seeds 20-119")
summary_lines.append("eval split: seeds 120-319")
summary_lines.append("budget: exact top-B = 100 / 200")
summary_lines.append("model: pure Python logistic regression with standardized tabular features")
summary_lines.append("features: " + ",".join(FEATURES))
summary_lines.append("PRM_task_fail target: unverified failure label")
summary_lines.append("PRM_value_gain target: normalized positive reward gain from verification")
summary_lines.append("")

for policy_name, score_col in policies:
    ranked = sorted(eval_records, key=lambda r: (-r[score_col], r["seed"]))
    selected = set(r["seed"] for r in ranked[:BUDGET])

    for rank, rec in enumerate(ranked, start=1):
        s = rec["seed"]
        is_sel = 1 if s in selected else 0

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
            "prm_task_fail_score": rec["prm_task_fail_score"],
            "prm_value_gain_score": rec["prm_value_gain_score"],
        })

        chosen = canonical(s, 1 if is_sel else 0)
        chosen["policy"] = policy_name
        chosen["episode_id"] = f"revision_prm_eval_{policy_name}_s{s}"
        chosen["verify_used"] = str(is_sel)
        chosen["policy_score"] = str(rec[score_col])
        chosen["notes"] = (
            f"PRM baseline eval policy={policy_name}; "
            f"score_col={score_col}; exact top-B={BUDGET}/200; selected={is_sel}."
        )
        raw_out.append(chosen)

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

# write
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
