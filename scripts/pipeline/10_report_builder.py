"""
scripts/pipeline/10_report_builder.py — Experimental Report Builder
=====================================================================
Auto-generate publication-ready tables and figure references.
Output: results_v4/report/ directory with:
 - table_1_model_comparison.md
 - table_2_protocol_rankings.md
 - table_3_statistical_tests.md
 - table_4_deployment_consistency.md
 - appendix_full_results.md
"""

import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def build_table_1_model_comparison(experiments, output_dir):
  """
  Table 1: Model Performance Comparison (Walk-Forward, seed=42).
  Rows: Models, Columns: MAE/RMSE/MAPE/R² per target×horizon.
  """
  lines = ['# Table 1: Model Performance Comparison (Walk-Forward Protocol)', '']

  for target in ['XANG', 'DAU']:
    lines.append(f'## {target}')
    lines.append('')
    lines.append('| Model | Horizon | MAE | RMSE | MAPE (%) | R² |')
    lines.append('|-------|---------|-----|------|----------|----|')

    target_exps = sorted(
      [e for e in experiments
       if e['target'] == target and e.get('protocol') == 'walkforward'],
      key=lambda x: (x['horizon'], x['model'])
    )

    for exp in target_exps:
      m = exp.get('metrics', {})
      lines.append(
        f"| {exp['model']} | H{exp['horizon']} | "
        f"{m.get('MAE', 0):.3f} | {m.get('RMSE', 0):.3f} | "
        f"{m.get('MAPE', 0):.2f} | {m.get('R2', 0):.4f} |"
      )
    lines.append('')

  path = os.path.join(output_dir, 'table_1_model_comparison.md')
  with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
  print(f"  Table 1 → {path}")


def build_table_2_protocol_rankings(experiments, output_dir):
  """
  Table 2: Rankings by Protocol — Average Rank + Borda.
  The core table for H1.
  """
  lines = ['# Table 2: Model Rankings by Evaluation Protocol', '']

  protocols = sorted(set(e.get('protocol', 'walkforward') for e in experiments))

  for target in ['XANG', 'DAU']:
    lines.append(f'## {target}')
    lines.append('')
    lines.append('| Protocol | Model | Avg Rank | Borda | MAE_R | RMSE_R | MAPE_R | R²_R |')
    lines.append('|----------|-------|----------|-------|-------|--------|--------|------|')

    for protocol in protocols:
      proto_exps = [e for e in experiments
             if e['target'] == target and e.get('protocol') == protocol]

      # Average across horizons
      models = sorted(set(e['model'] for e in proto_exps))
      for model in models:
        m_exps = [e for e in proto_exps if e['model'] == model]
        if not m_exps:
          continue

        rankings = [e.get('ranking', {}) for e in m_exps]
        avg_rank = np.mean([r.get('average_rank', 0) for r in rankings if r.get('average_rank')])
        borda = np.mean([r.get('borda_score', 0) for r in rankings if r.get('borda_score')])
        mae_r = np.mean([r.get('MAE', 0) for r in rankings if r.get('MAE')])
        rmse_r = np.mean([r.get('RMSE', 0) for r in rankings if r.get('RMSE')])
        mape_r = np.mean([r.get('MAPE', 0) for r in rankings if r.get('MAPE')])
        r2_r = np.mean([r.get('R2', 0) for r in rankings if r.get('R2')])

        lines.append(
          f"| {protocol} | {model} | {avg_rank:.2f} | {borda:.1f} | "
          f"{mae_r:.1f} | {rmse_r:.1f} | {mape_r:.1f} | {r2_r:.1f} |"
        )
    lines.append('')

  path = os.path.join(output_dir, 'table_2_protocol_rankings.md')
  with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
  print(f"  Table 2 → {path}")


def build_table_3_statistical_tests(output_dir):
  """
  Table 3: Statistical Test Results.
  """
  from config import RESULTS_DIR
  stats_path = os.path.join(RESULTS_DIR, 'evaluation_database', 'statistical_results.json')

  if not os.path.exists(stats_path):
    print("  No statistical results found — skipping Table 3")
    return

  with open(stats_path, 'r') as f:
    stats = json.load(f)

  lines = ['# Table 3: Statistical Validation Results', '']

  # Friedman
  if stats.get('friedman'):
    lines.append('## Friedman Test (Multi-model ranking)')
    lines.append('')
    lines.append('| Target | Protocol | χ² | p-value | Significant | Nemenyi CD |')
    lines.append('|--------|----------|----|---------|-------------|-----------|')
    for fr in stats['friedman']:
      sig = '' if fr.get('significant_5pct') else ''
      lines.append(
        f"| {fr['target']} | {fr['protocol']} | "
        f"{fr['statistic']:.2f} | {fr['p_value']:.4f} | {sig} | "
        f"{fr.get('nemenyi_cd', 0):.3f} |"
      )
    lines.append('')

  # RII
  if stats.get('rii'):
    lines.append('## Rank Instability Index (RII)')
    lines.append('')
    lines.append('| Target/Protocol | Model | RII |')
    lines.append('|-----------------|-------|-----|')
    for key, rii_data in stats['rii'].items():
      for model, rii_val in sorted(rii_data.items()):
        lines.append(f"| {key} | {model} | {rii_val:.4f} |")
    lines.append('')

  path = os.path.join(output_dir, 'table_3_statistical_tests.md')
  with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
  print(f"  Table 3 → {path}")


def build_table_4_deployment(output_dir):
  """
  Table 4: Deployment Consistency (H3).
  """
  from config import RESULTS_DIR
  deploy_path = os.path.join(RESULTS_DIR, 'evaluation_database', 'deployment_validation.json')

  if not os.path.exists(deploy_path):
    print("  No deployment results found — skipping Table 4")
    return

  with open(deploy_path, 'r') as f:
    deploy_results = json.load(f)

  lines = ['# Table 4: Deployment Consistency (Hypothesis H3)', '']
  lines.append('| Target | Horizon | Spearman ρ | p-value | Kendall τ | p-value | Consistent |')
  lines.append('|--------|---------|-----------|---------|----------|---------|-----------|')

  for r in deploy_results:
    sp = r.get('spearman', {})
    kt = r.get('kendall', {})
    consistent = '' if r.get('deployment_consistent') else ''
    lines.append(
      f"| {r['target']} | H{r['horizon']} | "
      f"{sp.get('rho', 0):.3f} | {sp.get('p_value', 1):.4f} | "
      f"{kt.get('tau', 0):.3f} | {kt.get('p_value', 1):.4f} | {consistent} |"
    )

  path = os.path.join(output_dir, 'table_4_deployment_consistency.md')
  with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
  print(f"  Table 4 → {path}")


def build_appendix(experiments, output_dir):
  """
  Appendix: Full results for all models × targets × horizons.
  """
  lines = ['# Appendix: Complete Experimental Results', '']
  lines.append(f'Total experiments: {len(experiments)}')
  lines.append('')
  lines.append('| Model | Target | H | Protocol | Seed | MAE | RMSE | MAPE | R² | Avg Rank |')
  lines.append('|-------|--------|---|----------|------|-----|------|------|----|----------|')

  for exp in sorted(experiments, key=lambda x: (x['target'], x['horizon'], x.get('protocol', ''), x['model'])):
    m = exp.get('metrics', {})
    r = exp.get('ranking', {})
    lines.append(
      f"| {exp['model']} | {exp['target']} | {exp['horizon']} | "
      f"{exp.get('protocol', 'wf')} | {exp.get('seed', 42)} | "
      f"{m.get('MAE', 0):.3f} | {m.get('RMSE', 0):.3f} | "
      f"{m.get('MAPE', 0):.2f} | {m.get('R2', 0):.4f} | "
      f"{r.get('average_rank', '-')} |"
    )

  path = os.path.join(output_dir, 'appendix_full_results.md')
  with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
  print(f"  Appendix → {path}")


def main():
  from config import RESULTS_DIR
  from src.evaluation.evaluation_database import EvaluationDatabase

  print("=" * 60)
  print(" EXPERIMENTAL REPORT BUILDER")
  print("=" * 60)

  db = EvaluationDatabase()
  db.load()
  experiments = db.get_experiments(status='completed')

  output_dir = os.path.join(RESULTS_DIR, 'report')
  os.makedirs(output_dir, exist_ok=True)

  print(f"\n Generating report from {len(experiments)} experiments...\n")

  build_table_1_model_comparison(experiments, output_dir)
  build_table_2_protocol_rankings(experiments, output_dir)
  build_table_3_statistical_tests(output_dir)
  build_table_4_deployment(output_dir)
  build_appendix(experiments, output_dir)

  # Figure references
  figures_dir = os.path.join(RESULTS_DIR, 'figures')
  if os.path.exists(figures_dir):
    figs = [f for f in os.listdir(figures_dir) if f.endswith('.png')]
    print(f"\n  Figures available: {len(figs)}")
    for fig in sorted(figs):
      print(f"   {fig}")

  print(f"\n Report → {output_dir}/")


if __name__ == '__main__':
  main()
