#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Sequence

from branch_replay import cleanup_branch_clones, run_branch_replay
from public_risk_hint import attach_public_risk_hint
from rollout_policy import run_default_rollout
from sandbox_env import VERIFY_COST, apply_action, init_episode, load_state

POLICY_CHOICES = [
    'no_verify',
    'always_verify',
    'uncertainty_only',
    'harm_aware_selective',
    'random_matched_cost',
]


def build_case_list(case_mode: str) -> List[str]:
    if case_mode == 'mixed':
        return ['easy', 'dependency_sensitive', 'corruption_prone']
    if case_mode in {'easy', 'dependency_sensitive', 'corruption_prone'}:
        return [case_mode]
    raise ValueError(f'Unsupported case_mode: {case_mode}')


def make_episode_specs(cases: Sequence[str], episodes_per_case: int, seed_start: int, run_name: str) -> List[Dict[str, Any]]:
    specs: List[Dict[str, Any]] = []
    for case_type in cases:
        for i in range(episodes_per_case):
            seed = seed_start + i
            specs.append({
                'case_type': case_type,
                'seed': seed,
                'episode_stub': f'{run_name}__{case_type}__{i:03d}',
            })
    return specs


def prepare_episode(episode_id: str, case_type: str, seed: int) -> Dict[str, Any]:
    init_episode(episode_id=episode_id, case_type=case_type, seed=seed, overwrite=True)
    hint = attach_public_risk_hint(episode_id)
    apply_action(episode_id, 'inspect_files')
    state = load_state(episode_id)
    return {
        'hint': hint,
        'state': state,
    }


def branch_metrics(episode_id: str) -> Dict[str, Any]:
    replay = run_branch_replay(
        source_episode=episode_id,
        candidate_action='risky_patch',
        corrected_action='safe_edit',
        cleanup=True,
    )
    impact = replay['impact_summary']
    return {
        'replay': replay,
        'branch_harm_exact': float(impact['branch_harm_exact']),
        'reward_wrong_continuation': float(impact['reward_wrong_continuation']),
        'reward_corrected_continuation': float(impact['reward_corrected_continuation']),
    }


def harm_decision(branch_harm_exact: float, threshold: float) -> bool:
    return branch_harm_exact > threshold


def uncertainty_decision(public_risk_hint: float, threshold: float) -> bool:
    return public_risk_hint >= threshold


def random_decision(target_verify_rate: float, key: str) -> bool:
    rng = random.Random(f'random_matched_cost::{key}')
    return rng.random() < target_verify_rate


def run_single_episode(
    policy_name: str,
    case_type: str,
    seed: int,
    episode_id: str,
    harm_threshold: float,
    uncertainty_threshold: float,
    matched_verify_rate: float,
) -> Dict[str, Any]:
    prep = prepare_episode(episode_id=episode_id, case_type=case_type, seed=seed)
    hint = prep['hint']
    state = prep['state']

    public_risk_hint = float(hint['public_risk_hint'])
    public_risk_label = hint['public_risk_label']

    verified = 0
    corrected = 0
    verification_cost = 0.0
    chosen_action = 'risky_patch'
    branch_harm_exact = None
    reward_wrong_continuation = None
    reward_corrected_continuation = None

    need_branch_eval = policy_name in {'always_verify', 'harm_aware_selective'}
    metrics = None
    if need_branch_eval:
        metrics = branch_metrics(episode_id)
        branch_harm_exact = metrics['branch_harm_exact']
        reward_wrong_continuation = metrics['reward_wrong_continuation']
        reward_corrected_continuation = metrics['reward_corrected_continuation']

    if policy_name == 'no_verify':
        verified = 0
        chosen_action = 'risky_patch'

    elif policy_name == 'always_verify':
        verified = 1
        verification_cost = VERIFY_COST
        chosen_action = 'safe_edit'
        corrected = 1

    elif policy_name == 'uncertainty_only':
        verified = 1 if uncertainty_decision(public_risk_hint, uncertainty_threshold) else 0
        if verified:
            verification_cost = VERIFY_COST
            chosen_action = 'safe_edit'
            corrected = 1

    elif policy_name == 'harm_aware_selective':
        verify_now = harm_decision(float(branch_harm_exact), harm_threshold)
        verified = 1 if verify_now else 0
        if verified:
            verification_cost = VERIFY_COST
            chosen_action = 'safe_edit'
            corrected = 1

    elif policy_name == 'random_matched_cost':
        verify_now = random_decision(matched_verify_rate, episode_id)
        verified = 1 if verify_now else 0
        if verified:
            verification_cost = VERIFY_COST
            chosen_action = 'safe_edit'
            corrected = 1

    else:
        raise ValueError(f'Unknown policy: {policy_name}')

    apply_action(episode_id, chosen_action)
    rollout = run_default_rollout(episode_id)
    final_state = load_state(episode_id)
    cleanup_branch_clones(episode_id)

    realized_reward = float(final_state['total_reward'])
    net_reward = realized_reward - verification_cost

    return {
        'policy': policy_name,
        'episode_id': episode_id,
        'case_type': case_type,
        'seed': seed,
        'public_risk_hint': public_risk_hint,
        'public_risk_label': public_risk_label,
        'reversibility': state.get('reversibility'),
        'coupling_strength': state.get('coupling_strength'),
        'chosen_action': chosen_action,
        'verified': verified,
        'verification_cost': verification_cost,
        'corrected': corrected,
        'branch_harm_exact': branch_harm_exact,
        'reward_wrong_continuation': reward_wrong_continuation,
        'reward_corrected_continuation': reward_corrected_continuation,
        'realized_reward': realized_reward,
        'net_reward': net_reward,
        'success': int(final_state['success']),
        'done': int(final_state['done']),
        'metadata_corrupted': int(final_state['metadata_corrupted']),
        'irreversible_failure': int(final_state['irreversible_failure']),
        'final_state': final_state,
        'rollout': rollout,
    }


def summarize_policy(records: Sequence[Dict[str, Any]], policy_name: str) -> Dict[str, Any]:
    return {
        'policy': policy_name,
        'episodes': len(records),
        'avg_net_reward': mean(float(r['net_reward']) for r in records),
        'avg_realized_reward': mean(float(r['realized_reward']) for r in records),
        'success_rate': mean(int(r['success']) for r in records),
        'failure_rate': mean(1 - int(r['success']) for r in records),
        'verify_rate': mean(int(r['verified']) for r in records),
        'avg_verification_cost': mean(float(r['verification_cost']) for r in records),
        'correction_rate': mean(int(r['corrected']) for r in records),
        'irreversible_failure_rate': mean(int(r['irreversible_failure']) for r in records),
        'avg_branch_harm_exact_when_measured': mean(
            float(r['branch_harm_exact']) for r in records if r['branch_harm_exact'] is not None
        ) if any(r['branch_harm_exact'] is not None for r in records) else None,
    }


def format_summary_table(rows: Sequence[Dict[str, Any]]) -> str:
    headers = [
        'policy', 'episodes', 'avg_net_reward', 'avg_realized_reward', 'success_rate',
        'failure_rate', 'verify_rate', 'avg_verification_cost', 'correction_rate', 'irreversible_failure_rate'
    ]
    widths = {h: len(h) for h in headers}
    formatted_rows: List[Dict[str, str]] = []
    for row in rows:
        frow = {
            'policy': str(row['policy']),
            'episodes': str(row['episodes']),
            'avg_net_reward': f"{float(row['avg_net_reward']):.4f}",
            'avg_realized_reward': f"{float(row['avg_realized_reward']):.4f}",
            'success_rate': f"{float(row['success_rate']):.4f}",
            'failure_rate': f"{float(row['failure_rate']):.4f}",
            'verify_rate': f"{float(row['verify_rate']):.4f}",
            'avg_verification_cost': f"{float(row['avg_verification_cost']):.4f}",
            'correction_rate': f"{float(row['correction_rate']):.4f}",
            'irreversible_failure_rate': f"{float(row['irreversible_failure_rate']):.4f}",
        }
        formatted_rows.append(frow)
        for h in headers:
            widths[h] = max(widths[h], len(frow[h]))

    def fmt_row(row: Dict[str, str]) -> str:
        return ' | '.join(row[h].ljust(widths[h]) for h in headers)

    lines = [fmt_row({h: h for h in headers}), '-+-'.join('-' * widths[h] for h in headers)]
    lines.extend(fmt_row(row) for row in formatted_rows)
    return '\n'.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--episodes-per-case', type=int, default=10)
    parser.add_argument('--case-mode', default='mixed', choices=['mixed', 'easy', 'dependency_sensitive', 'corruption_prone'])
    parser.add_argument('--policies', nargs='+', default=POLICY_CHOICES, choices=POLICY_CHOICES)
    parser.add_argument('--harm-threshold', type=float, default=3.0)
    parser.add_argument('--uncertainty-threshold', type=float, default=0.55)
    parser.add_argument('--seed-start', type=int, default=0)
    args = parser.parse_args()

    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_name = f'branch_baselines_rerun_{timestamp}'
    run_dir = logs_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    cases = build_case_list(args.case_mode)
    episode_specs = make_episode_specs(cases, args.episodes_per_case, args.seed_start, run_name)

    harm_verify_decisions = []
    for spec in episode_specs:
        episode_id = f"{spec['episode_stub']}__planning"
        prepare_episode(episode_id=episode_id, case_type=spec['case_type'], seed=spec['seed'])
        metrics = branch_metrics(episode_id)
        harm_verify_decisions.append(int(harm_decision(metrics['branch_harm_exact'], args.harm_threshold)))
        cleanup_branch_clones(episode_id)
    matched_verify_rate = mean(harm_verify_decisions) if harm_verify_decisions else 0.0

    all_records: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []

    for policy_name in args.policies:
        policy_records: List[Dict[str, Any]] = []
        for spec in episode_specs:
            episode_id = f"{spec['episode_stub']}__{policy_name}"
            record = run_single_episode(
                policy_name=policy_name,
                case_type=spec['case_type'],
                seed=spec['seed'],
                episode_id=episode_id,
                harm_threshold=args.harm_threshold,
                uncertainty_threshold=args.uncertainty_threshold,
                matched_verify_rate=matched_verify_rate,
            )
            policy_records.append(record)
            all_records.append(record)
        summary_rows.append(summarize_policy(policy_records, policy_name))

    metadata = {
        'run_name': run_name,
        'episodes_per_case': args.episodes_per_case,
        'case_mode': args.case_mode,
        'cases': cases,
        'harm_threshold': args.harm_threshold,
        'uncertainty_threshold': args.uncertainty_threshold,
        'matched_verify_rate': matched_verify_rate,
        'policies': args.policies,
    }

    summary_table = format_summary_table(summary_rows)
    print(summary_table)
    print()
    print(json.dumps({'metadata': metadata, 'summary_rows': summary_rows}, indent=2))

    (run_dir / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    (run_dir / 'summary.json').write_text(json.dumps(summary_rows, indent=2), encoding='utf-8')
    (run_dir / 'records.json').write_text(json.dumps(all_records, indent=2), encoding='utf-8')
    (run_dir / 'summary.txt').write_text(summary_table + '\n\n' + json.dumps({'metadata': metadata, 'summary_rows': summary_rows}, indent=2), encoding='utf-8')

    print()
    print(f'Saved outputs to: {run_dir}')


if __name__ == '__main__':
    main()
