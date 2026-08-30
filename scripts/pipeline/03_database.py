"""
scripts/pipeline/03_database.py — Build Evaluation Database (Methodology §8)
===============================================================================
Import existing results and build the single source of truth.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def main():
  from src.evaluation.evaluation_database import EvaluationDatabase

  print("=" * 60)
  print(" BUILD EVALUATION DATABASE (Methodology §8)")
  print("=" * 60)

  db = EvaluationDatabase()

  # Import existing Walk-Forward results
  n_imported = db.import_existing_results()

  # Print summary
  summary = db.summary()
  print(f"\n Schema version: {summary['schema_version']}")
  print(f" Total experiments: {summary['total_experiments']}")
  print(f" Completed: {summary['completed']}")
  print(f" Models: {summary['models']}")
  print(f" Protocols: {summary['protocols']}")
  print(f" Targets: {summary['targets']}")
  print(f" Horizons: {summary['horizons']}")

  # Save
  db_path = db.save()
  print(f"\n Evaluation Database saved → {db_path}")

  return db


if __name__ == '__main__':
  main()
