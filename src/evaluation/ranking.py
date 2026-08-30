"""
src/evaluation/ranking.py — Ranking System (Methodology §8)
==============================================================
Rankings are computed independently for MAE, RMSE, MAPE, and R²,
then aggregated using Average Rank (primary analysis),
while Borda Rank is used as a sensitivity analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from scipy import stats


def compute_metric_ranks(metric_values: Dict[str, float],
             lower_is_better: bool = True) -> Dict[str, int]:
  """
  Rank models for a single metric.

  Args:
    metric_values: {model_name: metric_value}
    lower_is_better: True for MAE/RMSE/MAPE, False for R²

  Returns:
    {model_name: rank} (1 = best)
  """
  models = list(metric_values.keys())
  values = [metric_values[m] for m in models]

  if not lower_is_better:
    values = [-v for v in values] # Negate so lower = better

  ranked = stats.rankdata(values, method='average')
  return {m: int(r) for m, r in zip(models, ranked)}


def compute_average_rank(all_metric_ranks: Dict[str, Dict[str, int]]) -> Dict[str, float]:
  """
  Primary ranking: Average Rank across all metrics.

  Args:
    all_metric_ranks: {metric_name: {model_name: rank}}

  Returns:
    {model_name: average_rank}
  """
  models = set()
  for ranks in all_metric_ranks.values():
    models.update(ranks.keys())

  avg_ranks = {}
  for model in models:
    ranks_for_model = [ranks[model] for ranks in all_metric_ranks.values()
              if model in ranks]
    avg_ranks[model] = float(np.mean(ranks_for_model))

  return dict(sorted(avg_ranks.items(), key=lambda x: x[1]))


def compute_borda_rank(all_metric_ranks: Dict[str, Dict[str, int]],
            n_models: int) -> Dict[str, float]:
  """
  Sensitivity analysis: Borda Count ranking.
  Borda score = (n_models - rank) for each metric, then sum.

  Args:
    all_metric_ranks: {metric_name: {model_name: rank}}
    n_models: Total number of models

  Returns:
    {model_name: borda_score} (higher = better)
  """
  models = set()
  for ranks in all_metric_ranks.values():
    models.update(ranks.keys())

  borda_scores = {}
  for model in models:
    score = 0.0
    for ranks in all_metric_ranks.values():
      if model in ranks:
        score += (n_models - ranks[model])
    borda_scores[model] = score

  return dict(sorted(borda_scores.items(), key=lambda x: x[1], reverse=True))


def build_ranking_table(results: List[Dict], metrics: List[str] = None) -> pd.DataFrame:
  """
  Build a comprehensive ranking table from experiment results.

  Args:
    results: List of dicts with keys: model, target, horizon, metrics
    metrics: Which metrics to rank on. Default: MAE, RMSE, MAPE, R2

  Returns:
    DataFrame with columns: Target, Horizon, Model, metric values, ranks, avg_rank, borda_score
  """
  if metrics is None:
    metrics = ['MAE', 'RMSE', 'MAPE', 'R2']

  lower_is_better = {'MAE': True, 'RMSE': True, 'MAPE': True, 'R2': False}

  rows = []
  for r in results:
    row = {
      'Model': r['model'],
      'Target': r.get('target_type', r.get('target', '')),
      'Horizon': r['horizon'],
      'Protocol': r.get('protocol', 'walkforward'),
      'Seed': r.get('seed', 42),
    }
    for m in metrics:
      if m in r.get('metrics', {}):
        row[m] = r['metrics'][m]
    rows.append(row)

  df = pd.DataFrame(rows)

  # Compute ranks per (Target, Horizon, Protocol) group
  rank_cols = []
  for m in metrics:
    rank_col = f'{m}_Rank'
    rank_cols.append(rank_col)
    df[rank_col] = np.nan

  avg_rank_col = 'Average_Rank'
  borda_col = 'Borda_Score'
  df[avg_rank_col] = np.nan
  df[borda_col] = np.nan

  for (target, horizon, protocol), group in df.groupby(['Target', 'Horizon', 'Protocol']):
    n_models = len(group)
    all_metric_ranks = {}

    for m in metrics:
      if m not in group.columns or group[m].isna().all():
        continue
      lib = lower_is_better.get(m, True)
      values = group[m].to_dict() # {idx: value}
      model_values = {group.loc[idx, 'Model']: val for idx, val in values.items()}
      ranks = compute_metric_ranks(model_values, lower_is_better=lib)

      # Map back to df indices
      for idx in group.index:
        model = group.loc[idx, 'Model']
        if model in ranks:
          df.loc[idx, f'{m}_Rank'] = ranks[model]

      all_metric_ranks[m] = ranks

    if all_metric_ranks:
      avg_ranks = compute_average_rank(all_metric_ranks)
      borda_ranks = compute_borda_rank(all_metric_ranks, n_models)
      for idx in group.index:
        model = group.loc[idx, 'Model']
        if model in avg_ranks:
          df.loc[idx, avg_rank_col] = avg_ranks[model]
        if model in borda_ranks:
          df.loc[idx, borda_col] = borda_ranks[model]

  return df.sort_values(['Target', 'Horizon', 'Protocol', avg_rank_col])
