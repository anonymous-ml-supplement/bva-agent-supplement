#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
RUNS_DIR = BASE_DIR / 'runs'
CSV_PATH = BASE_DIR / 'runs_summary.csv'


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def pick(d: Dict[str, Any], keys: List[str], default: Any = '') -> Any:
    for key in keys:
        if key in d:
            return d[key]
    return default


def fmt_bool(x: Any) -> str:
    if isinstance(x, bool):
        return 'true' if x else 'false'
    if x in {0, 1}:
        return str(x)
    return str(x)


def fmt_float(x: Any) -> str:
    if x == '' or x is None:
        return ''
    return f'{float(x):.4f}'


def collect_run_dirs(run_ids: List[str]) -> List[Path]:
    if not RUNS_DIR.exists():
        return []
    if run_ids:
        return [RUNS_DIR / run_id for run_id in run_ids if (RUNS_DIR / run_id).exists()]
    return sorted([p for p in RUNS_DIR.iterdir() if p.is_dir()])


def build_row(run_dir: Path) -> Optional[Dict[str, Any]]:
    manifest_path = run_dir / 'manifest.json'
    summary_path = run_dir / 'summary.json'
    if not manifest_path.exists() or not summary_path.exists():
        return None

    manifest = load_json(manifest_path)
    summary = load_json(summary_path)

    return {
        'run_id': pick(manifest, ['run_id'], run_dir.name),
        'created_at_utc': pick(manifest, ['created_at_utc'], ''),
        'episode_id': pick(summary, ['episode_id'], ''),
        'case_type': pick(summary, ['case_type'], pick(manifest, ['case_type'], '')),
        'seed': pick(manifest, ['seed'], ''),
        'model': pick(manifest, ['model'], ''),
        'mode_plan': pick(manifest, ['mode_plan'], ''),
        'harm_threshold': pick(summary, ['harm_threshold'], pick(manifest, ['impact_threshold'], '')),
        'reversibility': pick(summary, ['reversibility'], ''),
        'coupling_strength': pick(summary, ['coupling_strength'], ''),
        'public_risk_label': pick(summary, ['public_risk_label'], ''),
        'public_risk_hint': pick(summary, ['public_risk_hint'], ''),
        'mode': pick(summary, ['mode'], ''),
        'requested_action': pick(summary, ['requested_action'], ''),
        'final_action': pick(summary, ['final_action'], ''),
        'corrected': pick(summary, ['corrected'], ''),
        'verification_cost': pick(summary, ['verification_cost'], ''),
        'branch_harm_exact': pick(summary, ['branch_harm_exact'], ''),
        'reward_wrong_continuation': pick(summary, ['reward_wrong_continuation'], ''),
        'reward_corrected_continuation': pick(summary, ['reward_corrected_continuation'], ''),
        'success': pick(summary, ['success'], ''),
        'done': pick(summary, ['done'], ''),
        'irreversible_failure': pick(summary, ['irreversible_failure'], ''),
        'metadata_corrupted': pick(summary, ['metadata_corrupted'], ''),
        'total_reward': pick(summary, ['total_reward'], ''),
    }


def print_table(rows: List[Dict[str, Any]]) -> None:
    display_columns = [
        'run_id', 'episode_id', 'case_type', 'public_risk_label', 'mode',
        'final_action', 'corrected', 'branch_harm_exact', 'total_reward'
    ]
    display_rows: List[Dict[str, str]] = []
    for row in rows:
        display_rows.append({
            'run_id': str(row['run_id']),
            'episode_id': str(row['episode_id']),
            'case_type': str(row['case_type']),
            'public_risk_label': str(row['public_risk_label']),
            'mode': str(row['mode']),
            'final_action': str(row['final_action']),
            'corrected': fmt_bool(row['corrected']),
            'branch_harm_exact': fmt_float(row['branch_harm_exact']),
            'total_reward': fmt_float(row['total_reward']),
        })

    if not display_rows:
        return

    widths = {col: max(len(col), max(len(r[col]) for r in display_rows)) for col in display_columns}
    header = ' | '.join(col.ljust(widths[col]) for col in display_columns)
    sep = '-+-'.join('-' * widths[col] for col in display_columns)
    print(header)
    print(sep)
    for row in display_rows:
        print(' | '.join(row[col].ljust(widths[col]) for col in display_columns))


def write_csv(rows: List[Dict[str, Any]]) -> None:
    fieldnames = [
        'run_id', 'created_at_utc', 'episode_id', 'case_type', 'seed', 'model',
        'mode_plan', 'harm_threshold', 'reversibility', 'coupling_strength',
        'public_risk_label', 'public_risk_hint', 'mode', 'requested_action',
        'final_action', 'corrected', 'verification_cost', 'branch_harm_exact',
        'reward_wrong_continuation', 'reward_corrected_continuation',
        'success', 'done', 'irreversible_failure', 'metadata_corrupted', 'total_reward'
    ]
    with CSV_PATH.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', action='append', default=[])
    args = parser.parse_args()

    rows: List[Dict[str, Any]] = []
    for run_dir in collect_run_dirs(args.run_id):
        row = build_row(run_dir)
        if row is not None:
            rows.append(row)

    if not rows:
        print(json.dumps({'status': 'empty', 'message': 'No runs found.'}, indent=2))
        return

    rows = sorted(rows, key=lambda x: x['run_id'])
    print_table(rows)
    write_csv(rows)
    print()
    print(json.dumps({'status': 'ok', 'num_runs': len(rows), 'csv_path': str(CSV_PATH)}, indent=2))


if __name__ == '__main__':
    main()
