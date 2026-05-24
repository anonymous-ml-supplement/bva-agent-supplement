import csv
import math
from collections import defaultdict, Counter

BASE_RAW = "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_raw.csv"
REPL_RAW = "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_replacements_raw.csv"
MISSING_RAW = "../artifacts/reported_results/joint_calibration/joint_calibration_missing_outcomes_raw.csv"

OUT_RAW = "../artifacts/reported_results/joint_calibration/joint_calibration_exactTopB100_eval_raw.csv"
OUT_DECISIONS = "../artifacts/reported_results/joint_calibration/joint_calibration_exactTopB100_eval_decisions.csv"
OUT_SUMMARY = "../artifacts/reported_results/joint_calibration/joint_calibration_exactTopB100_eval_summary.txt"

CAL_SEEDS = set(range(20, 120))
EVAL_SEEDS = set(range(120, 320))
BUDGET = 100
N_BINS = 10

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

all_rows = []
for p in [BASE_RAW, REPL_RAW, MISSING_RAW]:
    part = read_csv(p)
    print("Loaded", len(part), "rows from", p)
    all_rows.extend(part)

# Use p_times_H rows as the base feature table, one feature row per seed.
base_rows_all = read_csv(BASE_RAW)
feature_rows = {}
for r in base_rows_all:
    if r["policy"] == "p_times_H":
        feature_rows[int(r["seed"])] = r

assert all(s in feature_rows for s in CAL_SEEDS), "Missing calibration feature rows"
assert all(s in feature_rows for s in EVAL_SEEDS), "Missing evaluation feature rows"

# Build outcome pool by seed and verify state.
pool = defaultdict(lambda: defaultdict(list))
for r in all_rows:
    s = int(r["seed"])
    v = int(fl(r["verify_used"]))
    pool[s][v].append(r)

# Pick canonical outcome.
# Prefer explicit no_verify for unverified and always_verify for verified.
# Otherwise take a deterministic first row sorted by episode_id.
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

# Verify eval completeness.
missing = []
for s in sorted(EVAL_SEEDS):
    for v in [0, 1]:
        if v not in pool[s]:
            missing.append((s, v))
if missing:
    raise RuntimeError(f"Eval split missing outcomes: {missing[:20]}")

# Prepare calibration targets.
# p calibration target: empirical bad outcome from available unverified outcomes in cal split.
# H calibration target: exact realized branch harm normalized by max branch harm in cal split.
cal_p_pairs = []
cal_h_pairs = []

cal_h_max = max(fl(feature_rows[s]["branch_harm_exact"]) for s in CAL_SEEDS)
if cal_h_max <= 0:
    cal_h_max = 1.0

for s in sorted(CAL_SEEDS):
    fr = feature_rows[s]
    p_score = fl(fr["p_score"])
    h_score = fl(fr["harm_score"])
    exact_h = fl(fr["branch_harm_exact"]) / cal_h_max

    # H target is available for every feature row.
    cal_h_pairs.append((h_score, max(0.0, min(1.0, exact_h))))

    # p target uses available unverified outcome if present.
    if 0 in pool[s]:
        ur = canonical(s, 0)
        bad = 1.0 - fl(ur["success"])
        cal_p_pairs.append((p_score, bad))

print()
print("Calibration pairs:")
print("p pairs:", len(cal_p_pairs))
print("H pairs:", len(cal_h_pairs))
print("cal_h_max:", cal_h_max)

# Pure Python monotone binning calibrator.
# Sort by score, split into bins, average target, then enforce nondecreasing bin means.
def fit_monotone_binner(pairs, n_bins=10):
    pairs = sorted((float(x), float(y)) for x, y in pairs)
    n = len(pairs)
    if n == 0:
        raise RuntimeError("No calibration pairs")

    bins = []
    for b in range(n_bins):
        lo = int(round(b * n / n_bins))
        hi = int(round((b + 1) * n / n_bins))
        chunk = pairs[lo:hi]
        if not chunk:
            continue
        x_lo = chunk[0][0]
        x_hi = chunk[-1][0]
        y_mean = mean([y for _, y in chunk])
        bins.append([x_lo, x_hi, y_mean, len(chunk)])

    # Pool adjacent violators style merge for nondecreasing means.
    merged = []
    for b in bins:
        merged.append(b)
        while len(merged) >= 2 and merged[-2][2] > merged[-1][2]:
            b2 = merged.pop()
            b1 = merged.pop()
            n1, n2 = b1[3], b2[3]
            new = [
                b1[0],
                b2[1],
                (b1[2] * n1 + b2[2] * n2) / (n1 + n2),
                n1 + n2,
            ]
            merged.append(new)

    def predict(x):
        x = float(x)
        if x <= merged[0][0]:
            return merged[0][2]
        if x >= merged[-1][1]:
            return merged[-1][2]
        for lo, hi, y, nbin in merged:
            if lo <= x <= hi:
                return y
        return merged[-1][2]

    return merged, predict

p_bins, p_cal = fit_monotone_binner(cal_p_pairs, N_BINS)
h_bins, h_cal = fit_monotone_binner(cal_h_pairs, N_BINS)

print()
print("p calibration bins:")
for b in p_bins:
    print(b)
print()
print("H calibration bins:")
for b in h_bins:
    print(b)

# Score eval seeds.
eval_records = []
for s in sorted(EVAL_SEEDS):
    fr = feature_rows[s]
    p_score = fl(fr["p_score"])
    h_score = fl(fr["harm_score"])
    raw_prod = p_score * h_score
    pc = p_cal(p_score)
    hc = h_cal(h_score)
    cal_prod = pc * hc

    eval_records.append({
        "seed": s,
        "p_score": p_score,
        "harm_score": h_score,
        "p_times_H_score": raw_prod,
        "p_cal": pc,
        "H_cal": hc,
        "p_times_H_calibrated_score": cal_prod,
    })

policies = [
    ("p_only_eval", "p_score"),
    ("H_only_eval", "harm_score"),
    ("p_times_H_eval", "p_times_H_score"),
    ("p_times_H_calibrated_eval", "p_times_H_calibrated_score"),
]

raw_out = []
decisions_out = []
summary_lines = []

summary_lines.append("Joint calibration exact-top-B evaluation")
summary_lines.append("cal split: seeds 20-119")
summary_lines.append("eval split: seeds 120-319")
summary_lines.append("budget: exact top-B = 100 / 200")
summary_lines.append("calibrator: pure Python monotone binning, no sklearn")
summary_lines.append("")

for policy_name, score_col in policies:
    ranked = sorted(
        eval_records,
        key=lambda r: (-r[score_col], r["seed"])
    )
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
            "p_cal": rec["p_cal"],
            "H_cal": rec["H_cal"],
            "p_times_H_calibrated_score": rec["p_times_H_calibrated_score"],
        })

        chosen = canonical(s, 1 if is_sel else 0)
        chosen["policy"] = policy_name
        chosen["episode_id"] = f"revision_jointcal_eval_{policy_name}_s{s}"
        chosen["verify_used"] = str(is_sel)
        chosen["policy_score"] = str(rec[score_col])
        chosen["notes"] = (
            f"Joint calibration eval policy={policy_name}; "
            f"score_col={score_col}; exact top-B={BUDGET}/200; "
            f"selected={is_sel}."
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

# Write outputs.
raw_fieldnames = list(raw_out[0].keys())
with open(OUT_RAW, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=raw_fieldnames)
    w.writeheader()
    w.writerows(raw_out)

dec_fieldnames = list(decisions_out[0].keys())
with open(OUT_DECISIONS, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=dec_fieldnames)
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
