"""
scripts/pipeline/04_ranking.py — Ranking Computation (Methodology §8)
======================================================================
Prediction → Metrics → Ranking(MAE) → Ranking(RMSE) → Ranking(MAPE) → Ranking(R²)
→ Average Rank (primary) → Borda Check (sensitivity)
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def main():
  from config import RESULTS_DIR
  from src.evaluation.evaluation_database import EvaluationDatabase
  from src.evaluation.ranking import (
    compute_metric_ranks, compute_average_rank, compute_borda_rank
  )

  print("=" * 60)
  print(" RANKING COMPUTATION (Methodology §8)")
  print("=" * 60)

  # Load database
  db = EvaluationDatabase()
  db.load()

  experiments = db.get_experiments(status='completed')
  if not experiments:
    print(" No completed experiments found.")
    return

  metrics = ['MAE', 'RMSE', 'MAPE', 'R2']
  lower_is_better = {'MAE': True, 'RMSE': True, 'MAPE': True, 'R2': False}

  # Group by (target, horizon, protocol) for ranking
  groups = {}
  for exp in experiments:
    key = (exp['target'], exp['horizon'], exp.get('protocol', 'walkforward'))
    if key not in groups:
      groups[key] = []
    groups[key].append(exp)

  ranking_updates = {}

  for (target, horizon, protocol), group_exps in sorted(groups.items()):
    n_models = len(group_exps)
    if n_models < 2:
      continue

    print(f"\n {target} H{horizon} [{protocol}] — {n_models} models")

    # Compute per-metric rankings
    all_metric_ranks = {}
    for m in metrics:
      model_values = {}
      for exp in group_exps:
        if m in exp.get('metrics', {}):
          model_values[exp['model']] = exp['metrics'][m]

      if len(model_values) >= 2:
        ranks = compute_metric_ranks(model_values, lower_is_better=lower_is_better[m])
        all_metric_ranks[m] = ranks
        print(f"  {m} ranking: {ranks}")

    if not all_metric_ranks:
      continue

    # Average Rank (primary)
    avg_ranks = compute_average_rank(all_metric_ranks)
    print(f"  Average Rank: {avg_ranks}")

    # Borda Rank (sensitivity)
    borda = compute_borda_rank(all_metric_ranks, n_models)
    print(f"  Borda Score: {borda}")

    # Update ranking in database
    for exp in group_exps:
      eid = exp['experiment_id']
      model = exp['model']
      ranking_updates[eid] = {
        'MAE': all_metric_ranks.get('MAE', {}).get(model),
        'RMSE': all_metric_ranks.get('RMSE', {}).get(model),
        'MAPE': all_metric_ranks.get('MAPE', {}).get(model),
        'R2': all_metric_ranks.get('R2', {}).get(model),
        'average_rank': avg_ranks.get(model),
        'borda_score': borda.get(model),
      }

  # Apply updates and save
  db.update_rankings(ranking_updates)
  db.save()
  print(f"\n Rankings computed and saved for {len(ranking_updates)} experiments")


if __name__ == '__main__':
  main()
