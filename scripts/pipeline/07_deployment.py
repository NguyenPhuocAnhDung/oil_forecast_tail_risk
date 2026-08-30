"""
scripts/pipeline/07_deployment.py — Deployment Validation (Methodology §9)
============================================================================
Hypothesis H3: Walk-Forward protocol is expected to exhibit stronger rank 
correlation with future deployment performance than conventional protocols.

Walk-Forward Ranking 
            → Rank Correlation (Spearman / Kendall) → Deployment Consistency → H3
Observed Future Ranking 
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def main():
  from config import RESULTS_DIR, PROTOCOLS
  from src.evaluation.evaluation_database import EvaluationDatabase
  from src.evaluation.statistical_tests import spearman_rank_correlation, kendall_tau

  print("=" * 60)
  print(" DEPLOYMENT VALIDATION — Hypothesis H3 (Methodology §9)")
  print("=" * 60)

  db = EvaluationDatabase()
  db.load()

  experiments = db.get_experiments(status='completed')

  # Get unique (target, horizon) pairs
  pairs = set()
  for exp in experiments:
    pairs.add((exp['target'], exp['horizon']))

  deployment_results = []

  for target, horizon in sorted(pairs):
    # Get Walk-Forward rankings
    wf_exps = [e for e in experiments
          if e['target'] == target
          and e['horizon'] == horizon
          and e.get('protocol') == 'walkforward']

    # Get Future Holdout rankings
    fh_exps = [e for e in experiments
          if e['target'] == target
          and e['horizon'] == horizon
          and e.get('protocol') == 'future_holdout']

    if not wf_exps or not fh_exps:
      continue

    # Extract model rankings
    wf_ranks = {}
    for exp in wf_exps:
      avg_rank = exp.get('ranking', {}).get('average_rank')
      if avg_rank is not None:
        wf_ranks[exp['model']] = avg_rank

    fh_ranks = {}
    for exp in fh_exps:
      avg_rank = exp.get('ranking', {}).get('average_rank')
      if avg_rank is not None:
        fh_ranks[exp['model']] = avg_rank

    # Find common models
    common_models = sorted(set(wf_ranks.keys()) & set(fh_ranks.keys()))
    if len(common_models) < 3:
      continue

    wf_list = [wf_ranks[m] for m in common_models]
    fh_list = [fh_ranks[m] for m in common_models]

    # Spearman
    spearman = spearman_rank_correlation(wf_list, fh_list)
    # Kendall
    kendall = kendall_tau(wf_list, fh_list)

    result = {
      'target': target,
      'horizon': horizon,
      'models': common_models,
      'walkforward_ranks': wf_ranks,
      'future_holdout_ranks': fh_ranks,
      'spearman': spearman,
      'kendall': kendall,
      'deployment_consistent': spearman['rho'] > 0.6,
    }

    deployment_results.append(result)

    print(f"\n {target} H{horizon}:")
    print(f"  Walk-Forward ranks: {wf_ranks}")
    print(f"  Future Holdout ranks: {fh_ranks}")
    print(f"  Spearman ρ={spearman['rho']:.3f} (p={spearman['p_value']:.4f})")
    print(f"  Kendall τ={kendall['tau']:.3f} (p={kendall['p_value']:.4f})")
    print(f"  Deployment consistent: {'' if result['deployment_consistent'] else ''}")

  # Also compare other protocols vs Future Holdout
  for protocol in ['random', 'chronological']:
    print(f"\n --- Comparison: {protocol} vs Future Holdout ---")
    for target, horizon in sorted(pairs):
      proto_exps = [e for e in experiments
             if e['target'] == target
             and e['horizon'] == horizon
             and e.get('protocol') == protocol]
      fh_exps = [e for e in experiments
            if e['target'] == target
            and e['horizon'] == horizon
            and e.get('protocol') == 'future_holdout']

      if not proto_exps or not fh_exps:
        continue

      proto_ranks = {e['model']: e.get('ranking', {}).get('average_rank')
              for e in proto_exps if e.get('ranking', {}).get('average_rank') is not None}
      fh_ranks = {e['model']: e.get('ranking', {}).get('average_rank')
             for e in fh_exps if e.get('ranking', {}).get('average_rank') is not None}

      common = sorted(set(proto_ranks.keys()) & set(fh_ranks.keys()))
      if len(common) < 3:
        continue

      sp = spearman_rank_correlation(
        [proto_ranks[m] for m in common],
        [fh_ranks[m] for m in common]
      )
      print(f"  {target} H{horizon}: ρ={sp['rho']:.3f} (p={sp['p_value']:.4f})")

  # Save
  output_dir = os.path.join(RESULTS_DIR, 'evaluation_database')
  os.makedirs(output_dir, exist_ok=True)
  output_path = os.path.join(output_dir, 'deployment_validation.json')

  with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(deployment_results, f, indent=2, ensure_ascii=False, default=str)

  print(f"\n Deployment validation → {output_path}")


if __name__ == '__main__':
  main()
