"""
src/evaluation/statistical_tests.py — Kiểm định thống kê
==========================================================
Diebold-Mariano Test, Model Confidence Set, Friedman Test.
Chuẩn Q1 journal cho model comparison.
"""

import numpy as np
from scipy import stats


def diebold_mariano_test(errors_1: np.ndarray, errors_2: np.ndarray,
             horizon: int = 1, loss_type: str = 'mae') -> dict:
  """
  Diebold-Mariano (1995) test for equal predictive ability.
  
  H0: E[d_t] = 0 (two models have equal forecast accuracy)
  H1: E[d_t] ≠ 0 (forecasts differ significantly)
  
  Args:
    errors_1: Forecast errors from model 1 (y_true - y_pred_1)
    errors_2: Forecast errors from model 2 (y_true - y_pred_2)
    horizon: Forecast horizon (for Newey-West correction)
    loss_type: 'mae' for absolute errors, 'mse' for squared errors
  
  Returns:
    dict with 'dm_stat', 'p_value', 'significant_5pct', 'significant_1pct'
  """
  e1 = np.array(errors_1).flatten()
  e2 = np.array(errors_2).flatten()
  
  if loss_type == 'mae':
    d = np.abs(e1) - np.abs(e2)
  else:
    d = e1 ** 2 - e2 ** 2
  
  T = len(d)
  d_bar = np.mean(d)
  
  # Newey-West HAC variance estimator with Bartlett kernel and bandwidth limit
  gamma_0 = np.var(d, ddof=1)
  gamma_sum = 0.0
  
  # Econometric bandwidth limit: Floor(1.2 * T^(1/3))
  max_lag = min(horizon - 1, int(np.floor(1.2 * T**(1/3))))
  max_lag = max(0, max_lag)
  
  for k in range(1, max_lag + 1):
    w = 1 - k / (max_lag + 1)
    gamma_k = np.mean((d[k:] - d_bar) * (d[:-k] - d_bar))
    gamma_sum += 2 * w * gamma_k
  
  V = max(gamma_0 + gamma_sum, 1e-10) # Prevent division by zero
  
  # Standard DM stat
  dm_stat = d_bar / np.sqrt(V / T)
  
  # Harvey, Leybourne, and Newbold (1997) small-sample correction
  hln_factor = (T + 1 - 2 * horizon + (horizon / T) * (horizon - 1)) / T
  hln_factor = max(hln_factor, 1e-8)  # safety
  dm_stat = dm_stat * np.sqrt(hln_factor)
  
  p_value = 2 * (1 - stats.norm.cdf(abs(dm_stat)))
  
  return {
    'dm_stat': float(dm_stat),
    'p_value': float(p_value),
    'significant_5pct': p_value < 0.05,
    'significant_1pct': p_value < 0.01,
    'model_1_better': dm_stat < 0, # Negative = model_1 has smaller loss
  }


def friedman_test(metric_matrix: np.ndarray) -> dict:
  """
  Friedman test for comparing multiple models across multiple datasets/horizons.
  
  Args:
    metric_matrix: [n_datasets, n_models] matrix of metric values (lower = better)
  
  Returns:
    dict with 'statistic', 'p_value', 'ranks', 'mean_ranks'
  """
  n_datasets, n_models = metric_matrix.shape
  
  # Rank models within each dataset (1 = best)
  ranks = np.zeros_like(metric_matrix, dtype=float)
  for i in range(n_datasets):
    ranks[i] = stats.rankdata(metric_matrix[i])
  
  mean_ranks = ranks.mean(axis=0)
  
  # Friedman statistic
  stat, p_value = stats.friedmanchisquare(*[metric_matrix[:, j] for j in range(n_models)])
  
  return {
    'statistic': float(stat),
    'p_value': float(p_value),
    'ranks': ranks.tolist(),
    'mean_ranks': mean_ranks.tolist(),
    'significant_5pct': p_value < 0.05,
  }


def nemenyi_critical_distance(n_models: int, n_datasets: int, alpha: float = 0.05) -> float:
  """
  Nemenyi post-hoc test critical distance.
  
  CD = q_α × sqrt(n_models × (n_models + 1) / (6 × n_datasets))
  
  Uses approximation for q_α from Studentized Range distribution.
  """
  # q_alpha values for alpha=0.05 (from tables, approximated)
  q_alpha_table = {
    2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850,
    7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164,
  }
  q_alpha = q_alpha_table.get(n_models, 2.728) # Default for 5 models
  
  cd = q_alpha * np.sqrt(n_models * (n_models + 1) / (6 * n_datasets))
  return float(cd)


def compute_confidence_interval(values: list, confidence: float = 0.95) -> dict:
  """
  Tính confidence interval cho list of values (từ multi-seed runs).
  
  Args:
    values: List of metric values across seeds
    confidence: Confidence level (default 0.95)
  
  Returns:
    dict with 'mean', 'std', 'ci_lower', 'ci_upper', 'ci_width'
  """
  values = np.array(values)
  n = len(values)
  mean = np.mean(values)
  std = np.std(values, ddof=1)
  
  if n <= 1:
    return {'mean': float(mean), 'std': 0.0, 'ci_lower': float(mean),
        'ci_upper': float(mean), 'ci_width': 0.0}
  
  t_critical = stats.t.ppf((1 + confidence) / 2, df=n - 1)
  margin = t_critical * std / np.sqrt(n)
  
  return {
    'mean': float(mean),
    'std': float(std),
    'ci_lower': float(mean - margin),
    'ci_upper': float(mean + margin),
    'ci_width': float(2 * margin),
  }


# ============================================================
# RANKING AGREEMENT (Methodology §8)
# ============================================================

def spearman_rank_correlation(ranking_1: list, ranking_2: list) -> dict:
  """
  Spearman's ρ — Rank correlation between two orderings.
  Used for H3: Walk-Forward vs Future Holdout ranking correlation.

  Args:
    ranking_1: List of ranks for models under protocol 1
    ranking_2: List of ranks for models under protocol 2

  Returns:
    dict with 'rho', 'p_value', 'significant_5pct'
  """
  rho, p_value = stats.spearmanr(ranking_1, ranking_2)
  return {
    'rho': float(rho),
    'p_value': float(p_value),
    'significant_5pct': p_value < 0.05,
  }


def kendall_tau(ranking_1: list, ranking_2: list) -> dict:
  """
  Kendall's τ — Rank correlation (ordinal agreement).
  Used for Future Holdout deployment consistency.

  Args:
    ranking_1, ranking_2: Lists of ranks

  Returns:
    dict with 'tau', 'p_value', 'significant_5pct'
  """
  tau, p_value = stats.kendalltau(ranking_1, ranking_2)
  return {
    'tau': float(tau),
    'p_value': float(p_value),
    'significant_5pct': p_value < 0.05,
  }


def kendall_w(rank_matrix: np.ndarray) -> dict:
  """
  Kendall's W — Coefficient of concordance.
  Measures agreement among multiple rankers (e.g., multiple horizons).

  Args:
    rank_matrix: [n_raters, n_items] — each row is a ranking

  Returns:
    dict with 'W', 'chi2', 'p_value'
  """
  m, n = rank_matrix.shape # m raters, n items
  rank_sums = rank_matrix.sum(axis=0)
  mean_rank_sum = np.mean(rank_sums)
  SST = np.sum((rank_sums - mean_rank_sum) ** 2)

  W = (12 * SST) / (m ** 2 * (n ** 3 - n))
  chi2 = m * (n - 1) * W
  p_value = 1 - stats.chi2.cdf(chi2, df=n - 1)

  return {
    'W': float(W),
    'chi2': float(chi2),
    'p_value': float(p_value),
    'significant_5pct': p_value < 0.05,
  }


# ============================================================
# PRACTICAL SIGNIFICANCE (Methodology §8)
# ============================================================

def cliffs_delta(group1: np.ndarray, group2: np.ndarray) -> dict:
  """
  Cliff's Delta — Non-parametric effect size.
  Measures how often values in group1 are larger than group2.

  Interpretation:
    |δ| < 0.147: negligible
    |δ| < 0.33: small
    |δ| < 0.474: medium
    |δ| >= 0.474: large

  Args:
    group1, group2: Arrays of metric values

  Returns:
    dict with 'delta', 'magnitude'
  """
  n1, n2 = len(group1), len(group2)
  count = 0
  for x in group1:
    for y in group2:
      if x > y:
        count += 1
      elif x < y:
        count -= 1
  delta = count / (n1 * n2)

  abs_delta = abs(delta)
  if abs_delta < 0.147:
    magnitude = 'negligible'
  elif abs_delta < 0.33:
    magnitude = 'small'
  elif abs_delta < 0.474:
    magnitude = 'medium'
  else:
    magnitude = 'large'

  return {
    'delta': float(delta),
    'magnitude': magnitude,
  }


# ============================================================
# DESCRIPTIVE INDICATORS (Methodology §8)
# Note: These are descriptive indicators, NOT new statistical tests.
# ============================================================

def rank_instability_index(rankings_by_horizon: dict) -> dict:
  """
  RII — Rank Instability Index.
  Measures how much a model's rank changes across horizons.

  RII = std(ranks across horizons) / mean(ranks across horizons)

  Args:
    rankings_by_horizon: {horizon: {model: rank}}

  Returns:
    {model: RII_value}
  """
  models = set()
  for ranks in rankings_by_horizon.values():
    models.update(ranks.keys())

  rii = {}
  for model in models:
    model_ranks = [ranks[model] for ranks in rankings_by_horizon.values()
            if model in ranks]
    if len(model_ranks) > 1:
      rii[model] = float(np.std(model_ranks) / max(np.mean(model_ranks), 1e-8))
    else:
      rii[model] = 0.0

  return rii


def protocol_sensitivity_score(rankings_by_protocol: dict) -> dict:
  """
  PSS — Protocol Sensitivity Score.
  Measures how much a model's rank changes across evaluation protocols.

  PSS = max(rank) - min(rank) across protocols.
  High PSS = model performance is protocol-dependent.

  Args:
    rankings_by_protocol: {protocol: {model: rank}}

  Returns:
    {model: PSS_value}
  """
  models = set()
  for ranks in rankings_by_protocol.values():
    models.update(ranks.keys())

  pss = {}
  for model in models:
    model_ranks = [ranks[model] for ranks in rankings_by_protocol.values()
            if model in ranks]
    if len(model_ranks) > 1:
      pss[model] = float(max(model_ranks) - min(model_ranks))
    else:
      pss[model] = 0.0

  return pss
