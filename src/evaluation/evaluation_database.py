"""
src/evaluation/evaluation_database.py — Evaluation Database (Methodology §8)
===============================================================================
The Evaluation Database serves as the single source of truth for all subsequent
ranking, statistical validation, visualization, and deployment analyses.

Schema v2.0 — stores: predictions, metrics, rankings, statistical results,
configurations, random seeds, protocol metadata, trained model metadata,
runtime logs, dataset_version, and experiment status.
"""

import os
import json
import glob
import hashlib
import platform
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import torch


def _get_git_hash() -> str:
  """Get current git commit hash."""
  try:
    result = subprocess.run(
      ['git', 'rev-parse', '--short', 'HEAD'],
      capture_output=True, text=True, timeout=5
    )
    return result.stdout.strip() if result.returncode == 0 else 'unknown'
  except Exception:
    return 'unknown'


def _get_data_hash(data_path: str) -> str:
  """Compute SHA256 hash of dataset file for versioning."""
  if not os.path.exists(data_path):
    return 'file_not_found'
  h = hashlib.sha256()
  with open(data_path, 'rb') as f:
    for chunk in iter(lambda: f.read(8192), b''):
      h.update(chunk)
  return h.hexdigest()[:16]


def _get_environment_info() -> dict:
  """Collect environment metadata for reproducibility."""
  env = {
    'hostname': platform.node(),
    'os': f"{platform.system()} {platform.release()}",
    'python': platform.python_version(),
    'pytorch': torch.__version__,
    'cuda_available': torch.cuda.is_available(),
  }
  if torch.cuda.is_available():
    env['gpu'] = torch.cuda.get_device_name(0)
    env['cuda_version'] = torch.version.cuda or 'unknown'
  else:
    env['gpu'] = 'N/A'
    env['cuda_version'] = 'N/A'
  return env


class EvaluationDatabase:
  """
  Centralized Evaluation Database.

  Manages all experimental results across models, protocols, horizons, and seeds.
  Serves as the single source of truth for the Evaluation Science Framework.
  """

  def __init__(self, results_dir: str = None, data_path: str = None):
    from config import RESULTS_DIR, DATA_PATH, EVAL_DB_SCHEMA_VERSION
    self.results_dir = results_dir or RESULTS_DIR
    self.data_path = data_path or DATA_PATH
    self.schema_version = EVAL_DB_SCHEMA_VERSION
    self.db = {
      'schema_version': self.schema_version,
      'created_at': datetime.utcnow().isoformat() + 'Z',
      'updated_at': None,
      'git_hash': _get_git_hash(),
      'dataset_version': _get_data_hash(self.data_path),
      'environment': _get_environment_info(),
      'experiments': [],
    }

  def import_existing_results(self):
    """
    Import results from results_v4/ into the database.
    Supports both directory structures:
     NEW: results_v4/{protocol}/{model}/{target}_H{horizon}/results.json
     OLD: results_v4/{model}/{target}_H{horizon}/results.json
    """
    # Scan for results.json at any depth
    result_files = sorted(glob.glob(os.path.join(self.results_dir, '**', 'results.json'), recursive=True))

    imported = 0
    seen_ids = set()

    for fpath in result_files:
      try:
        with open(fpath, 'r') as f:
          data = json.load(f)

        # Read protocol from results.json directly (preferred)
        protocol = data.get('protocol', 'walkforward')

        experiment = self._build_experiment_record(
          model=data.get('model', 'unknown'),
          target=data.get('target_type', ''),
          horizon=data.get('horizon', 0),
          protocol=protocol,
          seed=data.get('seed', 42),
          metrics=data.get('metrics', {}),
          n_features=data.get('n_features', 0),
          result_dir=os.path.dirname(fpath),
          status=data.get('status', 'completed'),
          runtime_seconds=data.get('runtime_seconds', 0),
        )
        self.db['experiments'].append(experiment)
        imported += 1
      except Exception as e:
        print(f"Warning: Could not import {fpath}: {e}")

    print(f"Imported {imported} existing experiments into Evaluation Database.")
    return imported

  def add_experiment(self, model: str, target: str, horizon: int,
            protocol: str, seed: int, metrics: dict,
            result_dir: str = '', status: str = 'completed',
            runtime_seconds: float = 0.0, **kwargs):
    """Add a new experiment record to the database."""
    experiment = self._build_experiment_record(
      model=model, target=target, horizon=horizon,
      protocol=protocol, seed=seed, metrics=metrics,
      result_dir=result_dir, status=status,
      runtime_seconds=runtime_seconds, **kwargs
    )
    self.db['experiments'].append(experiment)

  def _build_experiment_record(self, model: str, target: str, horizon: int,
                 protocol: str, seed: int, metrics: dict,
                 result_dir: str = '', status: str = 'completed',
                 runtime_seconds: float = 0.0, **kwargs) -> dict:
    """Build a single experiment record with full metadata."""
    experiment_id = f"{model}_{target}_H{horizon}_{protocol}_seed{seed}"

    record = {
      'experiment_id': experiment_id,
      'model': model,
      'target': target,
      'horizon': horizon,
      'protocol': protocol,
      'seed': seed,
      'status': status, # completed | running | failed
      'metrics': metrics,
      'datetime': datetime.utcnow().isoformat() + 'Z',
      'git_hash': _get_git_hash(),
      'dataset_version': self.db.get('dataset_version', 'unknown'),
      'runtime_seconds': runtime_seconds,
    }

    # Paths to prediction/error files
    if result_dir:
      pred_path = os.path.join(result_dir, 'predictions.csv')
      err_path = os.path.join(result_dir, 'errors.npy')
      if os.path.exists(pred_path):
        record['predictions_path'] = pred_path
      if os.path.exists(err_path):
        record['errors_path'] = err_path

    # Per-metric rankings will be added by the ranking pipeline step
    record['ranking'] = {
      'MAE': None, 'RMSE': None, 'MAPE': None, 'R2': None,
      'average_rank': None, 'borda_score': None,
    }

    # Additional kwargs
    for k, v in kwargs.items():
      if k not in record:
        record[k] = v

    return record

  def update_rankings(self, ranking_data: dict):
    """
    Update ranking fields in experiments after ranking computation.

    Args:
      ranking_data: {experiment_id: {metric: rank, average_rank: ..., borda_score: ...}}
    """
    for exp in self.db['experiments']:
      eid = exp['experiment_id']
      if eid in ranking_data:
        exp['ranking'] = ranking_data[eid]

  def get_experiments(self, protocol: str = None, model: str = None,
            target: str = None, horizon: int = None,
            status: str = 'completed') -> List[dict]:
    """Filter experiments by criteria."""
    results = self.db['experiments']
    if protocol:
      results = [e for e in results if e.get('protocol') == protocol]
    if model:
      results = [e for e in results if e.get('model') == model]
    if target:
      results = [e for e in results if e.get('target') == target]
    if horizon is not None:
      results = [e for e in results if e.get('horizon') == horizon]
    if status:
      results = [e for e in results if e.get('status') == status]
    return results

  def save(self, output_path: str = None):
    """Save database to JSON file."""
    if output_path is None:
      os.makedirs(os.path.join(self.results_dir, 'evaluation_database'), exist_ok=True)
      output_path = os.path.join(self.results_dir, 'evaluation_database', 'evaluation_db.json')

    self.db['updated_at'] = datetime.utcnow().isoformat() + 'Z'

    with open(output_path, 'w', encoding='utf-8') as f:
      json.dump(self.db, f, indent=2, ensure_ascii=False, default=str)

    print(f"Evaluation Database saved: {output_path}")
    print(f" Schema version: {self.db['schema_version']}")
    print(f" Total experiments: {len(self.db['experiments'])}")
    return output_path

  def load(self, input_path: str = None):
    """Load database from JSON file."""
    if input_path is None:
      input_path = os.path.join(self.results_dir, 'evaluation_database', 'evaluation_db.json')

    with open(input_path, 'r', encoding='utf-8') as f:
      self.db = json.load(f)

    print(f"Loaded Evaluation Database: {len(self.db['experiments'])} experiments")

  def summary(self) -> dict:
    """Return a summary of the database contents."""
    exps = self.db['experiments']
    return {
      'schema_version': self.db['schema_version'],
      'total_experiments': len(exps),
      'completed': len([e for e in exps if e.get('status') == 'completed']),
      'failed': len([e for e in exps if e.get('status') == 'failed']),
      'models': sorted(set(e['model'] for e in exps)),
      'protocols': sorted(set(e.get('protocol', 'unknown') for e in exps)),
      'targets': sorted(set(e['target'] for e in exps)),
      'horizons': sorted(set(e['horizon'] for e in exps)),
      'seeds': sorted(set(e.get('seed', 42) for e in exps)),
    }
