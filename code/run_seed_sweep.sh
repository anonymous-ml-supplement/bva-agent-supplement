#!/usr/bin/env bash
set -euo pipefail

CODE_DIR="./ANONYMIZED_PATH"
DATA_DIR="./ANONYMIZED_PATH"

SUMMARY_CSV="${DATA_DIR}/summaries/phaseA_seed_sweep_summary.csv"
RUNLIST_CSV="${DATA_DIR}/runlists/phaseA_seed_sweep_runlist.csv"

mkdir -p "${DATA_DIR}/summaries" "${DATA_DIR}/runlists" "${DATA_DIR}/results" "${DATA_DIR}/logs"

# cases for Phase A
CASES=(
  "dependency_sensitive"
  "corruption_prone"
)

# start with two policies only
POLICIES=(
  "no_verify"
  "always_verify"
)

SEEDS=(1 2 3 4 5 6 7 8 9 10)

# build runlist if not exists
if [[ ! -f "${RUNLIST_CSV}" ]]; then
  echo "episode_id,case,policy,seed,status" > "${RUNLIST_CSV}"
  for case_name in "${CASES[@]}"; do
    short_case="${case_name}"
    for policy in "${POLICIES[@]}"; do
      for seed in "${SEEDS[@]}"; do
        ep="ep_${short_case}_${policy}_s${seed}"
        echo "${ep},${case_name},${policy},${seed},pending" >> "${RUNLIST_CSV}"
      done
    done
  done
fi

# run pending items
tail -n +2 "${RUNLIST_CSV}" | while IFS=, read -r episode_id case_name policy seed status; do
  if [[ "${status}" != "pending" ]]; then
    continue
  fi

  echo "============================================================"
  echo "Running: ${episode_id} | case=${case_name} | policy=${policy} | seed=${seed}"
  echo "============================================================"

  python3 "${CODE_DIR}/run_policy_episode.py" \
    --episode "${episode_id}" \
    --case "${case_name}" \
    --policy "${policy}" \
    --seed "${seed}" \
    --summary-csv "${SUMMARY_CSV}" \
    --runlist-csv "${RUNLIST_CSV}"

done

echo
echo "Done. Summary:"
echo "  ${SUMMARY_CSV}"
echo "Runlist:"
echo "  ${RUNLIST_CSV}"
