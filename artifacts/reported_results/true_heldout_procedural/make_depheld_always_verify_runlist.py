import csv

OUT = "../artifacts/reported_results/true_heldout_procedural/depheld_always_verify_runlist.csv"

rows = []
for seed in range(400, 500):
    rows.append({
        "episode_id": f"revision_depheld_always_verify_s{seed}",
        "case": "dep_sensitive_held_out",
        "policy": "always_verify",
        "seed": str(seed),
        "notes": "Counterfactual verified outcome for exact top-B held-out sandbox table.",
        "status": "",
    })

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["episode_id", "case", "policy", "seed", "notes", "status"])
    w.writeheader()
    w.writerows(rows)

print("Wrote:", OUT)
print("rows:", len(rows))
print("seeds:", 400, 499)
