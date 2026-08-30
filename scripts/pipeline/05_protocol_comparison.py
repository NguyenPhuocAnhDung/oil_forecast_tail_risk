"""
scripts/pipeline/05_protocol_comparison.py — Protocol Comparison (Contribution H1)
====================================================================================
Compares model rankings across 4 evaluation protocols to answer the core research question:
"Do different evaluation protocols lead to different scientific conclusions?"

This is the PRIMARY CONTRIBUTION of the paper.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def main():
  from config import RESULTS_DIR, PROTOCOLS
  from src.evaluation.evaluation_database import EvaluationDatabase
  from src.evaluation.statistical_tests import (
    protocol_sensitivity_score, rank_instability_index
  )

  print("=" * 60)
  print(" PROTOCOL COMPARISON — Core Contribution (H1)")
  print("=" * 60)

  db = EvaluationDatabase()
  db.load()

  experiments = db.get_experiments(status='completed')

  # Group rankings by protocol for each (target, horizon)
  all_targets_horizons = set()
  for exp in experiments:
    all_targets_horizons.add((exp['target'], exp['horizon']))

  comparison_results = []

  for target, horizon in sorted(all_targets_horizons):
    print(f"\n {target} H{horizon}:")

    # Get rankings per protocol
    rankings_by_protocol = {}
    for protocol in PROTOCOLS:
      protocol_exps = [e for e in experiments
               if e['target'] == target
               and e['horizon'] == horizon
               and e.get('protocol') == protocol]
      if protocol_exps:
        # Extract average rank
        ranks = {}
        for exp in protocol_exps:
          avg_rank = exp.get('ranking', {}).get('average_rank')
          if avg_rank is not None:
            ranks[exp['model']] = avg_rank
        if ranks:
          rankings_by_protocol[protocol] = ranks
          print(f"  {protocol}: {ranks}")

    if len(rankings_by_protocol) >= 2:
      # Compute PSS
      pss = protocol_sensitivity_score(rankings_by_protocol)
      print(f"  PSS: {pss}")

      comparison_results.append({
        'target': target,
        'horizon': horizon,
        'rankings_by_protocol': rankings_by_protocol,
        'pss': pss,
        'n_protocols': len(rankings_by_protocol),
      })

  # Save protocol comparison results
  output_dir = os.path.join(RESULTS_DIR, 'evaluation_database')
  os.makedirs(output_dir, exist_ok=True)

  output_path = os.path.join(output_dir, 'protocol_comparison.json')
  with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(comparison_results, f, indent=2, ensure_ascii=False, default=str)

  print(f"\n Protocol comparison → {output_path}")
  print(f"  Compared {len(comparison_results)} (target, horizon) groups")


if __name__ == '__main__':
  main()
