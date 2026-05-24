import csv

OUT = "../artifacts/reported_results/true_heldout_procedural/dep_sensitive_heldout_policies_runlist.csv"

POLICIES = ["p_only", "H_only", "p_times_H"]
SEEDS = range(400, 500)

rows = []
for policy in POLICIES:
    for seed in SEEDS:
        rows.append({
            "episode_id": f"revision_depheld_{policy}_s{seed}",
            "case": "dep_sensitive_held_out",
            "policy": policy,
            "seed": str(seed),
            "notes": "Small true held-out procedural sandbox diagnostic.",
            "status": "",
        })

fieldnames = ["episode_id", "case", "policy", "seed", "notes", "status"]

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

print("Wrote:", OUT)
print("rows:", len(rows))
print("policies:", POLICIES)
print("seeds:", min(SEEDS), max(SEEDS))
print()
print("First 10:")
for r in rows[:10]:
    print(r)
