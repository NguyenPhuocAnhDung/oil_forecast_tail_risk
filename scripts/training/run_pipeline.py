"""
scripts/run_pipeline.py — Pipeline Dispatcher
================================================
Modular pipeline controller (Airflow-style).
Calls each phase sequentially — does NOT contain logic itself.

Pipeline (matches Methodology_Upgraded.md):
 00. Environment Capture
 01. Dataset Freeze Verification
 02. Leakage Audit
 03. Training (delegated to existing scripts)
 04. Build Evaluation Database
 05. Ranking (Average Rank + Borda)
 06. Protocol Comparison (H1) + Statistical Validation
 07. Deployment Validation (H3)
 08. Visualization
 09. Reproducibility Export
 10. Report Builder
"""

import os
import sys
import subprocess
import time
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

PIPELINE_DIR = os.path.join(PROJECT_ROOT, 'scripts', 'pipeline')


def run_phase(phase_script: str, description: str, skip_on_fail: bool = False):
  """Run a pipeline phase and handle errors."""
  script_path = os.path.join(PIPELINE_DIR, phase_script)

  if not os.path.exists(script_path):
    print(f"  Script not found: {phase_script} — skipping")
    return False

  print(f"\n{'='*70}")
  print(f"  {description}")
  print(f"   Script: {phase_script}")
  print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
  print(f"{'='*70}")

  start = time.time()
  result = subprocess.run(
    [sys.executable, script_path],
    cwd=PROJECT_ROOT,
    stdout=sys.stdout,
    stderr=sys.stderr,
  )
  elapsed = time.time() - start

  if result.returncode == 0:
    print(f"  {description} — completed ({elapsed:.1f}s)")
    return True
  else:
    print(f"  {description} — FAILED (exit code {result.returncode})")
    if not skip_on_fail:
      print("  Pipeline halted. Fix the issue and re-run.")
      sys.exit(1)
    return False


def main():
  import argparse
  parser = argparse.ArgumentParser(description='Run Evaluation Pipeline')
  parser.add_argument('--skip-train', action='store_true',
            help='Skip training phase (use existing results)')
  parser.add_argument('--from-phase', type=int, default=0,
            help='Start from phase N (0-10)')
  parser.add_argument('--dry-run', action='store_true',
            help='Print pipeline steps without executing')
  args = parser.parse_args()

  phases = [
    ('00_environment.py',    'Phase 00: Environment Capture'),
    ('01_dataset_freeze.py',   'Phase 01: Dataset Freeze Verification'),
    ('01_audit.py',       'Phase 02: Leakage Audit & Verification'),
    (None,            'Phase 03: Training (use --skip-train or run separately)'),
    ('03_database.py',      'Phase 04: Build Evaluation Database'),
    ('04_ranking.py',      'Phase 05: Ranking (Average Rank + Borda)'),
    ('05_protocol_comparison.py','Phase 06a: Protocol Comparison (H1)'),
    ('06_statistics.py',     'Phase 06b: Statistical Validation'),
    ('07_deployment.py',     'Phase 07: Deployment Validation (H3)'),
    ('08_visualization.py',   'Phase 08: Visualization'),
    ('09_export.py',       'Phase 09: Reproducibility Export'),
    ('10_report_builder.py',   'Phase 10: Report Builder'),
  ]

  print("\n" + "=" * 70)
  print("  EVALUATION SCIENCE PIPELINE")
  print("   Methodology: Methodology_Upgraded.md (FROZEN)")
  print("   Config: config/experiment.yaml")
  print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print("=" * 70)

  if args.dry_run:
    print("\n [DRY RUN] Pipeline steps:")
    for i, (script, desc) in enumerate(phases):
      skip = ''
      if i < args.from_phase:
        skip = ' [SKIP - before --from-phase]'
      elif script is None and args.skip_train:
        skip = ' [SKIP - --skip-train]'
      elif script is None:
        skip = ' [MANUAL]'
      print(f"  {desc}{skip}")
    return

  total_start = time.time()

  for i, (script, desc) in enumerate(phases):
    if i < args.from_phase:
      print(f"\n ⏭ Skipping {desc} (--from-phase={args.from_phase})")
      continue

    if script is None: # Training phase
      if args.skip_train:
        print(f"\n ⏭ Skipping {desc} (--skip-train)")
      else:
        print(f"\n ℹ {desc}")
        print("   Run training separately with:")
        print("    python scripts/run_parallel_pipeline.py")
        print("   Or use --skip-train to use existing results.")
      continue

    run_phase(script, desc)

  total_elapsed = time.time() - total_start
  print(f"\n{'='*70}")
  print(f"  PIPELINE COMPLETE — Total time: {total_elapsed:.1f}s")
  print(f"{'='*70}\n")


if __name__ == '__main__':
  main()
