#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from branch_replay import cleanup_branch_clones, run_branch_replay
from rollout_policy import run_default_rollout
from sandbox_env import VERIFY_COST, apply_action, load_state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode', required=True)
    parser.add_argument('--mode', required=True, choices=['direct', 'verify_then_decide'])
    parser.add_argument('--action', required=True, choices=['risky_patch', 'safe_edit'])
    parser.add_argument('--harm-threshold', type=float, default=3.0)
    parser.add_argument(
        '--compute-branch-diagnostics',
        default='always',
        choices=['always', 'verify_only', 'never'],
        help='Whether to compute exact branch harm on cloned episodes for logging only.',
    )
    args = parser.parse_args()

    apply_action(args.episode, 'inspect_files')

    should_compute = (
        args.compute_branch_diagnostics == 'always'
        or (args.compute_branch_diagnostics == 'verify_only' and args.mode == 'verify_then_decide')
    )

    replay_result = None
    branch_harm_exact = None
    reward_wrong_continuation = None
    reward_corrected_continuation = None
    corrected = False
    final_action = args.action
    verification_cost = 0.0

    if should_compute:
        replay_result = run_branch_replay(
            source_episode=args.episode,
            candidate_action='risky_patch',
            corrected_action='safe_edit',
            cleanup=True,
        )
        impact_summary = replay_result['impact_summary']
        branch_harm_exact = float(impact_summary['branch_harm_exact'])
        reward_wrong_continuation = float(impact_summary['reward_wrong_continuation'])
        reward_corrected_continuation = float(impact_summary['reward_corrected_continuation'])

    if args.mode == 'verify_then_decide':
        verification_cost = VERIFY_COST
        if branch_harm_exact is None:
            replay_result = run_branch_replay(
                source_episode=args.episode,
                candidate_action='risky_patch',
                corrected_action='safe_edit',
                cleanup=True,
            )
            impact_summary = replay_result['impact_summary']
            branch_harm_exact = float(impact_summary['branch_harm_exact'])
            reward_wrong_continuation = float(impact_summary['reward_wrong_continuation'])
            reward_corrected_continuation = float(impact_summary['reward_corrected_continuation'])

        if args.action == 'risky_patch' and branch_harm_exact > args.harm_threshold:
            final_action = 'safe_edit'
            corrected = True

    apply_action(args.episode, final_action)
    rollout = run_default_rollout(args.episode)
    final_state = load_state(args.episode)
    cleanup_branch_clones(args.episode)

    result = {
        'status': 'ok',
        'episode_id': args.episode,
        'case_type': final_state.get('case_type'),
        'reversibility': final_state.get('reversibility'),
        'coupling_strength': final_state.get('coupling_strength'),
        'mode': args.mode,
        'requested_action': args.action,
        'final_action': final_action,
        'corrected': corrected,
        'verification_cost': verification_cost,
        'harm_threshold': args.harm_threshold,
        'branch_harm_exact': branch_harm_exact,
        'reward_wrong_continuation': reward_wrong_continuation,
        'reward_corrected_continuation': reward_corrected_continuation,
        'success': int(final_state['success']),
        'done': int(final_state['done']),
        'metadata_corrupted': int(final_state['metadata_corrupted']),
        'irreversible_failure': int(final_state['irreversible_failure']),
        'total_reward': float(final_state['total_reward']),
        'rollout': rollout,
        'replay_result': replay_result,
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
