#!/usr/bin/env bash
set -euo pipefail

CODE_DIR="./ANONYMIZED_PATH"
DATA_DIR="./ANONYMIZED_PATH"

SUMMARY_CSV="${DATA_DIR}/summaries/phaseB_selected_summary.csv"
RUNLIST_CSV="${DATA_DIR}/runlists/phaseB_selected_runlist.csv"

mkdir -p "${DATA_DIR}/summaries" "${DATA_DIR}/runlists" "${DATA_DIR}/results"

declare -A CASE_TO_SEEDS
CASE_TO_SEEDS[dependency_sensitive]="2 6 7 8"
CASE_TO_SEEDS[corruption_prone]="1 2 3 4"

POLICIES=(
  "uncertainty_only"
  "harm_aware_selective"
  "random_matched_cost"
)

if [[ ! -f "${RUNLIST_CSV}" ]]; then
  echo "episode_id,case,policy,seed,status" > "${RUNLIST_CSV}"

  for case_name in "${!CASE_TO_SEEDS[@]}"; do
    for policy in "${POLICIES[@]}"; do
      for seed in ${CASE_TO_SEEDS[$case_name]}; do
        ep="ep_${case_name}_${policy}_s${seed}"
        echo "${ep},${case_name},${policy},${seed},pending" >> "${RUNLIST_CSV}"
      done
    done
  done
fi

tail -n +2 "${RUNLIST_CSV}" | while IFS=, read -r episode_id case_name policy seed status; do
  if [[ "${status}" != "pending" ]]; then
    continue
  fi

  echo "============================================================"
  echo "Running: ${episode_id} | case=${case_name} | policy=${policy} | seed=${seed}"
  echo "============================================================"

  if [[ "${policy}" == "random_matched_cost" ]]; then
    python3 "${CODE_DIR}/run_policy_episode.py" \
      --episode "${episode_id}" \
      --case "${case_name}" \
      --policy "${policy}" \
      --seed "${seed}" \
      --random-verify-prob 0.50 \
      --summary-csv "${SUMMARY_CSV}" \
      --runlist-csv "${RUNLIST_CSV}"
  else
    python3 "${CODE_DIR}/run_policy_episode.py" \
      --episode "${episode_id}" \
      --case "${case_name}" \
      --policy "${policy}" \
      --seed "${seed}" \
      --summary-csv "${SUMMARY_CSV}" \
      --runlist-csv "${RUNLIST_CSV}"
  fi
done

echo
echo "Done. Summary:"
echo "  ${SUMMARY_CSV}"
echo "Runlist:"
echo "  ${RUNLIST_CSV}"
