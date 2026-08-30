"""
scripts/pipeline/06_statistics.py — Statistical Validation (Methodology §8)
=============================================================================
Full statistical test suite:
 - Friedman + Nemenyi (multi-model ranking with explicit pairwise CD check)
 - Rank Instability Index (RII)
 - Protocol Sensitivity Score (PSS)
"""

import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def main():
  from config import RESULTS_DIR
  from src.evaluation.evaluation_database import EvaluationDatabase
  from src.evaluation.statistical_tests import (
    friedman_test, nemenyi_critical_distance,
    rank_instability_index, protocol_sensitivity_score,
  )
  from src.evaluation.ranking import compute_metric_ranks

  print("=" * 60)
  print(" STATISTICAL VALIDATION (Forced Honesty & Insights)")
  print("=" * 60)

  db = EvaluationDatabase()
  db.load()
  experiments = db.get_experiments(status='completed')
  if not experiments:
    print(" No completed experiments.")
    return

  all_stats = {'friedman': [], 'nemenyi': [], 'rii': {}, 'pss': {}}
  
  # Organize data: target -> protocol -> horizon -> model -> MAE
  groups = {}
  for exp in experiments:
    t, p, h, m = exp['target'], exp.get('protocol', 'walkforward'), exp['horizon'], exp['model']
    mae = exp.get('metrics', {}).get('MAE', float('inf'))
    if t not in groups: groups[t] = {}
    if p not in groups[t]: groups[t][p] = {}
    if h not in groups[t][p]: groups[t][p][h] = {}
    groups[t][p][h][m] = mae

  # 1. FRIEDMAN & NEMENYI (FORCED HONESTY)
  for target, proto_dict in groups.items():
    for protocol, horizons_data in proto_dict.items():
      models = set()
      for h_data in horizons_data.values(): models.update(h_data.keys())
      models = sorted(models)
      
      if len(models) < 3 or len(horizons_data) < 2: continue
      
      matrix = np.array([[horizons_data[h].get(m, float('inf')) for m in models] for h in sorted(horizons_data.keys())])
      result = friedman_test(matrix)
      cd = nemenyi_critical_distance(len(models), len(horizons_data))
      
      print(f"\n[{target} | {protocol.upper()}] Friedman p={result['p_value']:.4f}, CD={cd:.3f}")
      
      # Explicit Pairwise Check (Forced Honesty)
      mean_ranks = result['mean_ranks']
      model_ranks = dict(zip(models, mean_ranks))
      if 'GUMNet' in model_ranks:
        gumnet_rank = model_ranks['GUMNet']
        for m, r in model_ranks.items():
          if m != 'GUMNet':
            diff = gumnet_rank - r # lower rank is better
            if diff > cd:
              print(f"  FORCED HONESTY: [{m} > GUMNet] (Significant, diff={diff:.2f} > CD={cd:.2f})")
      
      all_stats['friedman'].append({'target': target, 'protocol': protocol, 'p_value': result['p_value'], 'cd': cd, 'ranks': model_ranks})

  # 2. RII (Rank Instability Index)
  for target, proto_dict in groups.items():
    for protocol, horizons_data in proto_dict.items():
      rankings_by_horizon = {}
      for h, h_data in horizons_data.items():
        if len(h_data) >= 2:
          rankings_by_horizon[h] = compute_metric_ranks(h_data, lower_is_better=True)
      if len(rankings_by_horizon) >= 2:
        rii = rank_instability_index(rankings_by_horizon)
        all_stats['rii'][f'{target}_{protocol}'] = rii
        print(f" RII [{target}/{protocol}]: {rii}")

  # 3. PSS (Protocol Sensitivity Score)
  for target, proto_dict in groups.items():
    models = set()
    for p_data in proto_dict.values():
      for h_data in p_data.values(): models.update(h_data.keys())
    models = sorted(models)
    
    # Build rankings per protocol (averaged across horizons)
    protocol_rankings = {}
    for protocol, horizons_data in proto_dict.items():
      avg_ranks = {m: [] for m in models}
      for h, h_data in horizons_data.items():
        if len(h_data) >= 2:
          r = compute_metric_ranks(h_data, lower_is_better=True)
          for m, rank in r.items(): avg_ranks[m].append(rank)
      protocol_rankings[protocol] = {m: np.mean(v) for m, v if v}
    
    if len(protocol_rankings) >= 2:
      print(f"\n  INSIGHT GENERATOR (PSS) for {target}:")
      pss_dict = protocol_sensitivity_score(protocol_rankings)
      all_stats['pss'][target] = pss_dict
      for m, pss in sorted(pss_dict.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {m:<18}: PSS = {pss:.3f} " + ("(Highly sensitive to protocol!)" if pss > 0.5 else "(Robust)"))

  # Save
  out_dir = os.path.join(RESULTS_DIR, 'evaluation_database')
  os.makedirs(out_dir, exist_ok=True)
  out_path = os.path.join(out_dir, 'statistical_results.json')
  with open(out_path, 'w', encoding='utf-8') as f: json.dump(all_stats, f, indent=2, ensure_ascii=False, default=str)
  print(f"\n Statistical results saved → {out_path}")

if __name__ == '__main__':
  main()
