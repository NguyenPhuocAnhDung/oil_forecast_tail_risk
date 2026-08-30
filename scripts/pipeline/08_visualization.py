"""
scripts/pipeline/08_visualization.py — Visualization (Methodology §8)
=======================================================================
Generate publication-quality figures for Q1 Journals:
 - CD Diagram (Critical Difference) - via Nemenyi
 - Protocol Comparison Heatmap (Rank Clustering)
 - Seed Stability Boxplot (Variance across 5 seeds)
 - Bump Chart / Ranking Transition Plot
 - Horizon Degradation
"""

import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def plot_ranking_transition(db_experiments, output_dir):
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt

  protocols_order = ['random', 'chronological', 'walkforward', 'future_holdout']
  targets = sorted(set(e['target'] for e in db_experiments))

  for target in targets:
    fig, axes = plt.subplots(1, 1, figsize=(10, 6))
    models = sorted(set(e['model'] for e in db_experiments if e['target'] == target))
    colors = plt.cm.Set2(np.linspace(0, 1, len(models)))
    
    model_ranks_by_protocol = {m: [] for m in models}
    for protocol in protocols_order:
      protocol_exps = [e for e in db_experiments if e['target'] == target and e.get('protocol') == protocol]
      model_avg = {}
      for m in models:
        m_exps = [e for e in protocol_exps if e['model'] == m]
        ranks = [e.get('ranking', {}).get('average_rank') for e in m_exps if e.get('ranking', {}).get('average_rank') is not None]
        model_avg[m] = np.mean(ranks) if ranks else None
      for m in models:
        model_ranks_by_protocol[m].append(model_avg.get(m))

    x_positions = range(len(protocols_order))
    for i, model in enumerate(models):
      ranks = model_ranks_by_protocol[model]
      valid_x = [x for x, r in zip(x_positions, ranks) if r is not None]
      valid_r = [r for r in ranks if r is not None]
      if valid_r:
        axes.plot(valid_x, valid_r, 'o-', color=colors[i], linewidth=3, markersize=10, label=model)

    axes.set_xlabel('Evaluation Protocol', fontsize=12, fontweight='bold')
    axes.set_ylabel('Average Rank (lower = better)', fontsize=12, fontweight='bold')
    axes.set_title(f'Ranking Transition (Instability) — {target}', fontsize=14, fontweight='bold')
    axes.set_xticks(x_positions)
    axes.set_xticklabels([p.replace('_', '\n').upper() for p in protocols_order], fontweight='bold')
    axes.invert_yaxis()
    axes.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    axes.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'ranking_transition_{target}.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_protocol_heatmap(db_experiments, output_dir):
  """Publication-quality heatmap showing rank clustering"""
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  try:
    import seaborn as sns
  except ImportError:
    print("  Seaborn not installed. Skipping heatmap.")
    return

  targets = sorted(set(e['target'] for e in db_experiments))
  protocols_order = ['random', 'chronological', 'walkforward', 'future_holdout']
  
  for target in targets:
    models = sorted(set(e['model'] for e in db_experiments if e['target'] == target))
    if not models: continue
    
    matrix = np.zeros((len(models), len(protocols_order)))
    for j, protocol in enumerate(protocols_order):
      protocol_exps = [e for e in db_experiments if e['target'] == target and e.get('protocol') == protocol]
      for i, m in enumerate(models):
        m_exps = [e for e in protocol_exps if e['model'] == m]
        ranks = [e.get('ranking', {}).get('average_rank') for e in m_exps if e.get('ranking', {}).get('average_rank') is not None]
        matrix[i, j] = np.mean(ranks) if ranks else np.nan
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt=".1f", cmap="YlGnBu_r", 
          xticklabels=[p.upper() for p in protocols_order], yticklabels=models,
          cbar_kws={'label': 'Average Rank'})
    plt.title(f'Protocol Rank Clustering — {target}', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'protocol_heatmap_{target}.png'), dpi=300, bbox_inches='tight')
    plt.close()

def plot_seed_boxplot(db_experiments, output_dir):
  """Boxplot for 5 seeds to show variance and robustness (Reviewer Q1 standard)"""
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  try:
    import seaborn as sns
  except ImportError:
    return

  # Filter only Walk-Forward (most important for stability)
  wf_exps = [e for e in db_experiments if e.get('protocol') == 'walkforward']
  if not wf_exps: return
  
  targets = sorted(set(e['target'] for e in wf_exps))
  
  for target in targets:
    t_exps = [e for e in wf_exps if e['target'] == target]
    models = sorted(set(e['model'] for e in t_exps))
    
    # Prepare data: list of MAPEs for each model across all seeds and horizons
    data = []
    labels = []
    for m in models:
      m_mapes = [e.get('metrics', {}).get('MAPE') for e in t_exps if e['model'] == m and e.get('metrics', {}).get('MAPE') is not None]
      if m_mapes:
        data.append(m_mapes)
        labels.append(m)
    
    if not data: continue

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=data, palette="Set2")
    plt.xticks(range(len(labels)), labels, rotation=45)
    plt.ylabel('MAPE (%)', fontweight='bold')
    plt.title(f'Model Robustness Across Seeds & Horizons (Walk-Forward) — {target}', fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y', linestyle='--')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'seed_boxplot_{target}.png'), dpi=300, bbox_inches='tight')
    plt.close()


def main():
  from config import RESULTS_DIR
  from src.evaluation.evaluation_database import EvaluationDatabase

  print("=" * 60)
  print(" VISUALIZATION (Publication Quality)")
  print("=" * 60)

  db = EvaluationDatabase()
  db.load()
  experiments = db.get_experiments(status='completed')

  output_dir = os.path.join(RESULTS_DIR, 'figures')
  os.makedirs(output_dir, exist_ok=True)

  if not experiments:
    print(" No experiments to visualize yet.")
    return

  print(f"\n Generating Q1-standard figures for {len(experiments)} experiments...")

  plot_ranking_transition(experiments, output_dir)
  plot_protocol_heatmap(experiments, output_dir)
  plot_seed_boxplot(experiments, output_dir)
  
  print(f"\n All publication figures saved → {output_dir}/")
  print(" Note: CD Diagram requires R/Orange for exact Nemenyi graph, or will be generated post-analysis.")

if __name__ == '__main__':
  main()
