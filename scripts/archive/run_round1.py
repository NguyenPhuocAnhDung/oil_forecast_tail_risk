"""
scripts/run_round1.py — Round 1 Experiment Orchestrator
==========================================================
Runs ALL Round 1 experiments (seed=42):
 7 models × 5 horizons × 4 protocols × 2 targets = 280 experiments

Strategy:
 1. Walk-Forward first (most important protocol)
 2. Then Chronological, Random, Future Holdout
 3. Within each protocol: short horizons first (fail-fast)

Usage:
  python scripts/run_round1.py             # Run all
  python scripts/run_round1.py --protocol walkforward  # One protocol
  python scripts/run_round1.py --resume         # Skip completed
  python scripts/run_round1.py --dry-run        # Show plan
"""

import argparse
import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
  ALL_HORIZONS, PROTOCOLS, BASELINES, RESULTS_DIR, DEFAULT_SEED
)

ALL_MODELS = ['GUMNet'] + BASELINES # 7 models total
ALL_TARGETS = ['XANG', 'DAU']

# Protocol execution order (most important first)
PROTOCOL_ORDER = ['walkforward', 'chronological', 'random', 'future_holdout']

# Horizon order (short first for fail-fast)
HORIZON_ORDER = sorted(ALL_HORIZONS)


def is_completed(protocol, model, target, horizon, seed=DEFAULT_SEED):
  """Check if experiment already completed."""
  result_file = os.path.join(
    RESULTS_DIR, protocol, model, f'{target}_H{horizon}', 'results.json'
  )
  if os.path.exists(result_file):
    try:
      with open(result_file, 'r') as f:
        data = json.load(f)
      return data.get('status') == 'completed'
    except Exception:
      return False
  return False


def build_experiment_queue(protocol_filter=None, resume=False, target_filter=None):
  """Build ordered queue of experiments to run."""
  queue = []
  protocols = [protocol_filter] if protocol_filter else PROTOCOL_ORDER
  targets = [target_filter] if target_filter else ALL_TARGETS

  for protocol in protocols:
    for horizon in HORIZON_ORDER:
      for target in targets:
        for model in ALL_MODELS:
          if resume and is_completed(protocol, model, target, horizon):
            continue
          queue.append({
            'protocol': protocol,
            'model': model,
            'target': target,
            'horizon': horizon,
          })

  return queue


def estimate_time(queue):
  """Rough time estimate based on horizon and model."""
  # Average seconds per Walk-Forward iteration (from observed data)
  # GUMNet: ~30s/iter, Baselines: ~10s/iter, XGBoost: ~2s/iter
  model_speed = {
    'GUMNet': 30, 'LSTM': 10, 'GRU': 10,
    'BiLSTM_Attention': 12, 'PatchTST': 15,
    'DLinear': 8, 'XGBoost': 2,
  }
  # Iterations = test_days / horizon
  test_days_map = {1: 100, 3: 100, 5: 100, 10: 150, 60: 600}

  total_seconds = 0
  for exp in queue:
    test_days = test_days_map.get(exp['horizon'], 100)
    iterations = test_days // exp['horizon']
    speed = model_speed.get(exp['model'], 15)
    total_seconds += iterations * speed

  return total_seconds


def run_single_experiment(exp, idx, total, seed=DEFAULT_SEED):
  """Run one experiment via subprocess."""
  print(f"\n{'='*80}")
  print(f" [{idx}/{total}] {exp['model']} | {exp['target']} | H{exp['horizon']} | {exp['protocol']}")
  print(f" Started: {datetime.now().strftime('%H:%M:%S')}")
  print(f"{'='*80}")

  cmd = [
    sys.executable, os.path.join('scripts', 'train_unified.py'),
    '--type', exp['target'],
    '--model', exp['model'],
    '--horizon', str(exp['horizon']),
    '--protocol', exp['protocol'],
    '--seed', str(seed),
  ]

  start = time.time()
  result = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  elapsed = time.time() - start

  status = 'completed' if result.returncode == 0 else 'FAILED'
  print(f" [{idx}/{total}] {status} in {elapsed:.0f}s")

  return result.returncode == 0


def main():
  parser = argparse.ArgumentParser(description='Round 1 Experiment Orchestrator')
  parser.add_argument('--protocol', type=str, default=None,
            help='Run only this protocol')
  parser.add_argument('--resume', action='store_true',
            help='Skip already completed experiments')
  parser.add_argument('--dry-run', action='store_true',
            help='Show experiment plan without running')
  parser.add_argument('--seed', type=int, default=DEFAULT_SEED)
  parser.add_argument('--target', type=str, default=None,
                      help='Run only this target (XANG or DAU)')
  args = parser.parse_args()

  queue = build_experiment_queue(
    protocol_filter=args.protocol,
    resume=args.resume,
    target_filter=args.target
  )

  total = len(queue)
  est_seconds = estimate_time(queue)
  est_hours = est_seconds / 3600

  print("\n" + "=" * 80)
  print("  ROUND 1 EXPERIMENT ORCHESTRATOR")
  print(f"   Seed: {args.seed}")
  print(f"   Total experiments: {total}")
  print(f"   Estimated time: {est_hours:.1f} hours ({est_seconds:,.0f} seconds)")
  print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print("=" * 80)

  if args.resume:
    # Count completed
    all_queue = build_experiment_queue(protocol_filter=args.protocol, resume=False, target_filter=args.target)
    completed = len(all_queue) - total
    print(f"   Completed: {completed} | Remaining: {total}")

  # Summary by protocol
  from collections import Counter
  proto_counts = Counter(e['protocol'] for e in queue)
  for p, c in proto_counts.items():
    print(f"   {p}: {c} experiments")

  if args.dry_run:
    print(f"\n [DRY RUN] Experiment queue:")
    for i, exp in enumerate(queue, 1):
      print(f"  {i:3d}. {exp['model']:20s} | {exp['target']} | H{exp['horizon']:2d} | {exp['protocol']}")
    return

  # Run
  total_start = time.time()
  completed = 0
  failed = 0

  for i, exp in enumerate(queue, 1):
    success = run_single_experiment(exp, i, total, args.seed)
    if success:
      completed += 1
    else:
      failed += 1

    # Progress update every 10 experiments
    if i % 10 == 0:
      elapsed = time.time() - total_start
      avg = elapsed / i
      remaining = avg * (total - i)
      print(f"\n  Progress: {i}/{total} | {completed} | {failed} | "
         f"ETA: {timedelta(seconds=int(remaining))}")

  total_elapsed = time.time() - total_start
  print(f"\n{'='*80}")
  print(f"  ROUND 1 COMPLETE")
  print(f"   Total: {total} | Completed: {completed} | Failed: {failed}")
  print(f"   Time: {timedelta(seconds=int(total_elapsed))}")
  print(f"{'='*80}\n")


if __name__ == '__main__':
  main()
