import csv
from collections import defaultdict

BASE_RAW = "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_raw.csv"
REPL_RAW = "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_replacements_raw.csv"
JOINT_MISSING_RAW = "../artifacts/reported_results/joint_calibration/joint_calibration_missing_outcomes_raw.csv"
PRM_CAL_MISSING_RAW = "../artifacts/reported_results/prm_baseline/prm_cal_missing_outcomes_raw.csv"

OUT_RAW = "../artifacts/reported_results/adversarial_relabel/adversarial_relabel_exactTopB100_eval_raw.csv"
OUT_DECISIONS = "../artifacts/reported_results/adversarial_relabel/adversarial_relabel_exactTopB100_eval_decisions.csv"
OUT_SUMMARY = "../artifacts/reported_results/adversarial_relabel/adversarial_relabel_exactTopB100_eval_summary.txt"

EVAL_SEEDS = list(range(120, 320))
BUDGET = 100
RHOS = [0.00, 0.10, 0.25, 0.50]

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

min_harm_score = min(r["harm_score"] for r in eval_records)

raw_out = []
decisions_out = []
summary_lines = []

summary_lines.append("Adversarial relabel exact-top-B evaluation")
summary_lines.append("eval split: seeds 120-319")
summary_lines.append("budget: exact top-B = 100 / 200")
summary_lines.append("attack: highest branch_harm_exact seeds have harm_score relabeled to minimum eval harm_score")
summary_lines.append("")

# Baseline p_only and clean p_times_H.
policy_specs = [
    ("p_only_eval", "p_score", None),
    ("p_times_H_clean_eval", "p_times_H_score", None),
]

# Add adversarial relabel variants.
for rho in RHOS:
    policy_specs.append((f"adv_relabel_p_times_H_rho_{rho:.2f}", "adv_score", rho))

for policy_name, score_col, rho in policy_specs:
    records = []
    attacked = set()

    if rho is not None:
        k_attack = int(round(rho * len(eval_records)))
        attacked = set(
            r["seed"] for r in sorted(eval_records, key=lambda x: (-x["branch_harm_exact"], x["seed"]))[:k_attack]
        )

    for r in eval_records:
        rr = dict(r)
        if rho is None:
            rr["adv_harm_score"] = rr["harm_score"]
            rr["adv_score"] = rr.get(score_col, rr["p_score"] * rr["harm_score"])
            rr["attacked"] = 0
        else:
            rr["attacked"] = 1 if rr["seed"] in attacked else 0
            rr["adv_harm_score"] = min_harm_score if rr["attacked"] else rr["harm_score"]
            rr["adv_score"] = rr["p_score"] * rr["adv_harm_score"]
        records.append(rr)

    ranked = sorted(records, key=lambda r: (-r[score_col], r["seed"]))
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
            "attacked": rec.get("attacked", 0),
            "p_score": rec["p_score"],
            "harm_score": rec["harm_score"],
            "adv_harm_score": rec.get("adv_harm_score", rec["harm_score"]),
            "p_times_H_score": rec["p_times_H_score"],
            "adv_score": rec.get("adv_score", rec["p_times_H_score"]),
            "branch_harm_exact": rec["branch_harm_exact"],
        })

        chosen = canonical(s, 1 if is_sel else 0)
        chosen["policy"] = policy_name
        chosen["episode_id"] = f"revision_advr_eval_{policy_name}_s{s}"
        chosen["verify_used"] = str(is_sel)
        chosen["policy_score"] = str(rec[score_col])
        chosen["notes"] = (
            f"Adversarial relabel eval policy={policy_name}; "
            f"rho={rho}; exact top-B={BUDGET}/200; selected={is_sel}; attacked={rec.get('attacked',0)}."
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

    attacked_n = sum(1 for d in decisions_out if d["policy"] == policy_name and int(d["attacked"]) == 1)
    attacked_selected = sum(1 for d in decisions_out if d["policy"] == policy_name and int(d["attacked"]) == 1 and int(d["selected_topB"]) == 1)

    summary_lines.append(
        f"{policy_name}: n={n}, verify_n={verify_n}, verify_rate={verify_n/n:.3f}, "
        f"success={success:.3f}, irreversible_failure={irrev:.3f}, "
        f"avg_net_reward={reward:.3f}, avg_verification_cost={cost:.3f}, "
        f"avg_selected_branch_harm={selected_harm:.3f}, avg_skipped_branch_harm={skipped_harm:.3f}, "
        f"attacked_n={attacked_n}, attacked_selected={attacked_selected}"
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
