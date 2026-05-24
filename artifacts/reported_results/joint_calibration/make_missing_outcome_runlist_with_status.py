import csv
from collections import defaultdict

IN_FILES = [
    "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_raw.csv",
    "../artifacts/reported_results/component_ablation/revision_table5_ablation_exactTopB150_replacements_raw.csv",
]

OUT = "../artifacts/reported_results/joint_calibration/joint_calibration_missing_outcomes_runlist.csv"

rows = []
for p in IN_FILES:
    with open(p, newline="", encoding="utf-8") as f:
        rows.extend(list(csv.DictReader(f)))

pool = defaultdict(lambda: defaultdict(list))
for r in rows:
    seed = int(r["seed"])
    verify = int(float(r["verify_used"]))
    pool[seed][verify].append(r)

eval_seeds = list(range(120, 320))

jobs = []
for s in eval_seeds:
    if 1 not in pool[s]:
        jobs.append({
            "episode_id": f"revision_jointcal_missing_verified_s{s}",
            "case": "dependency_sensitive",
            "policy": "always_verify",
            "seed": str(s),
            "notes": "Joint calibration missing verified outcome for eval split.",
            "status": "",
        })
    if 0 not in pool[s]:
        jobs.append({
            "episode_id": f"revision_jointcal_missing_unverified_s{s}",
            "case": "dependency_sensitive",
            "policy": "no_verify",
            "seed": str(s),
            "notes": "Joint calibration missing unverified outcome for eval split.",
            "status": "",
        })

fieldnames = ["episode_id", "case", "policy", "seed", "notes", "status"]

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(jobs)

print("Wrote:", OUT)
print("jobs:", len(jobs))
print("always_verify jobs:", sum(1 for j in jobs if j["policy"] == "always_verify"))
print("no_verify jobs:", sum(1 for j in jobs if j["policy"] == "no_verify"))
print("columns:", fieldnames)
