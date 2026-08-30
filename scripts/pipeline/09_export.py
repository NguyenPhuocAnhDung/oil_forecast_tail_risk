"""
scripts/pipeline/09_export.py — Reproducibility Package Export (Methodology §11)
=================================================================================
Export complete reproducibility package:
 - evaluation_db.json
 - ablation_protocols.json
 - protocol_audit_report.md
 - config.yaml
 - random_seeds.json
 - environment.json
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def export_config_yaml(output_dir: str):
  """Export config.py as config.yaml for reproducibility."""
  from config import (
    TARGETS, ALL_HORIZONS, BASELINES, SEEDS, DEFAULT_SEED,
    BATCH_SIZE, MAX_EPOCHS, D_FEAT, NUM_QUANTILES, QUANTILES,
    PROTOCOLS, FUTURE_HOLDOUT_RATIO, DATASET_FREEZE_DATE,
    EVAL_DB_SCHEMA_VERSION,
  )

  config = {
    'dataset_freeze_date': DATASET_FREEZE_DATE,
    'schema_version': EVAL_DB_SCHEMA_VERSION,
    'targets': TARGETS,
    'horizons': ALL_HORIZONS,
    'baselines': BASELINES,
    'seeds': SEEDS,
    'default_seed': DEFAULT_SEED,
    'batch_size': BATCH_SIZE,
    'max_epochs': MAX_EPOCHS,
    'd_feat': D_FEAT,
    'num_quantiles': NUM_QUANTILES,
    'quantiles': QUANTILES,
    'protocols': PROTOCOLS,
    'future_holdout_ratio': FUTURE_HOLDOUT_RATIO,
  }

  path = os.path.join(output_dir, 'config.yaml')
  with open(path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
  print(f"  config.yaml → {path}")


def export_random_seeds(output_dir: str):
  """Export random seeds configuration."""
  from config import SEEDS, DEFAULT_SEED

  seeds_config = {
    'seeds': SEEDS,
    'default_seed': DEFAULT_SEED,
    'note': 'Multi-seed strategy: Round 1 (seed=42) complete run, '
        'Round 2 (remaining seeds) incremental for CI/STD/Mean.',
  }

  path = os.path.join(output_dir, 'random_seeds.json')
  with open(path, 'w', encoding='utf-8') as f:
    json.dump(seeds_config, f, indent=2, ensure_ascii=False)
  print(f"  random_seeds.json → {path}")


def export_ablation_protocols(output_dir: str):
  """Export protocol descriptions for reproducibility."""
  protocols = {
    'protocols': [
      {
        'name': 'random',
        'scientific_purpose': 'Control',
        'description': 'Random shuffle split (70/15/15) — exposes temporal leakage danger.',
      },
      {
        'name': 'chronological',
        'scientific_purpose': 'Conventional',
        'description': 'Fixed chronological split (70/15/15) — standard in prior research.',
      },
      {
        'name': 'walkforward',
        'scientific_purpose': 'Deployment',
        'description': 'Expanding-window Walk-Forward — simulates real-world deployment.',
      },
      {
        'name': 'future_holdout',
        'scientific_purpose': 'External validation',
        'description': 'Final 15% temporal segment held out — IMMUTABLE, never used for '
                'model selection, hyperparameter tuning, early stopping, or threshold tuning.',
      },
    ],
  }

  path = os.path.join(output_dir, 'ablation_protocols.json')
  with open(path, 'w', encoding='utf-8') as f:
    json.dump(protocols, f, indent=2, ensure_ascii=False)
  print(f"  ablation_protocols.json → {path}")


def main():
  from config import RESULTS_DIR

  print("=" * 60)
  print(" REPRODUCIBILITY PACKAGE EXPORT (Methodology §11)")
  print("=" * 60)

  output_dir = os.path.join(RESULTS_DIR, 'evaluation_database')
  os.makedirs(output_dir, exist_ok=True)

  export_config_yaml(output_dir)
  export_random_seeds(output_dir)
  export_ablation_protocols(output_dir)

  # Check existing files
  expected_files = [
    'evaluation_db.json',
    'protocol_audit_report.md',
    'environment.json',
    'config.yaml',
    'random_seeds.json',
    'ablation_protocols.json',
  ]

  print(f"\n Reproducibility package checklist:")
  for fname in expected_files:
    fpath = os.path.join(output_dir, fname)
    exists = os.path.exists(fpath)
    icon = '' if exists else ''
    print(f"  {icon} {fname}")

  print(f"\n Reproducibility package → {output_dir}/")


if __name__ == '__main__':
  main()
