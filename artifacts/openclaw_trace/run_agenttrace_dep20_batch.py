import subprocess
from pathlib import Path

code_dir = Path("./ANONYMIZED_PATH")
runlist = Path("./ANONYMIZED_PATH")
summary = Path("./ANONYMIZED_PATH")

runlist.parent.mkdir(parents=True, exist_ok=True)
summary.parent.mkdir(parents=True, exist_ok=True)

seeds = ["20", "21", "23", "30", "34", "36", "58", "62", "68", "69"]

subprocess.run([
    "python3",
    str(code_dir / "make_matched_budget_runlist.py"),
    "--slices", "dependency_sensitive",
    "--seeds", *seeds,
    "--policies", "uncertainty_only_matched_budget", "harm_aware_selective",
    "--out", str(runlist),
    "--prefix", "agenttrace",
], check=True)

subprocess.run([
    "python3",
    str(code_dir / "run_runlist.py"),
    "--runlist", str(runlist),
    "--summary-csv", str(summary),
    "--uncertainty-threshold", "0.422000",
    "--harm-threshold", "0.291537",
    "--random-verify-prob", "0.500000",
    "--skip-done",
], check=True)

print("AGENTTRACE_BATCH_DONE")
print("runlist:", runlist)
print("summary:", summary)
