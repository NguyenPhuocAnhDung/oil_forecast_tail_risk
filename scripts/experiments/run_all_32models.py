#!/usr/bin/env python
"""
run_all_32models.py
===================
Orchestrator script that manages the sequential execution of model walkforward validation
for all SOTA baselines and GUM-Net variants, followed by statistical validation
and visualization scripts.

Features:
- --force-rerun flag defaulting to True
- --dry-run flag for pipeline verification
- Backup results_v4/ to results_v4_backup_{timestamp}/
- Clean results_v4/walkforward/{model}/ folders before execution (if force-rerun is True)
- Spawns subprocesses for train_unified.py
- Calls downstream compilation, DM test, effect size, and output generation scripts
"""

import os
import sys
import shutil
import argparse
import subprocess
from datetime import datetime, timezone

# Add project root to path for config import
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config import ALL_SOTA_BASELINES, GUM_NET_VARIANTS, ALL_HORIZONS, SEEDS, TARGETS

def main():
    parser = argparse.ArgumentParser(description="Orchestrator for all 32+ models pipeline")
    parser.add_argument('--force-rerun', type=lambda x: (str(x).lower() in ['true', '1', 'yes']), default=True,
                        help="Force rerun of all experiments by cleaning output directories first")
    parser.add_argument('--dry-run', action='store_true',
                        help="Dry run: prints command lines, cleans active dirs, and runs downstream reporting with mock data")
    # Granular control for partial runs
    parser.add_argument('--paradigm', type=str, default=None,
                        help="Run only models from a specific paradigm (e.g. P1_Linear, P5_SSM, GUMNet)")
    parser.add_argument('--horizon', type=int, default=None,
                        help="Run only a specific horizon (e.g. 1, 5, 10). Default: all horizons.")
    parser.add_argument('--seeds', type=str, default=None,
                        help="Comma-separated seeds to run (e.g. '42,123'). Default: all SEEDS from config.")
    parser.add_argument('--target', type=str, default='both', choices=['XANG', 'DAU', 'both'],
                        help="Target type to run. Default: both.")
    args = parser.parse_args()

    results_dir = 'results_v4'
    start_time = datetime.now()
    start_timestamp_str = start_time.strftime("%Y%m%d_%H%M%S")
    start_timestamp_iso = start_time.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')

    print(f"Pipeline started at: {start_time}")
    print(f"Force Rerun: {args.force_rerun}")
    print(f"Dry Run: {args.dry_run}")

    # Determine filters
    from config import SOTA_TAXONOMY_REGISTRY
    if args.paradigm == 'GUMNet':
        all_models = GUM_NET_VARIANTS
    elif args.paradigm and args.paradigm in SOTA_TAXONOMY_REGISTRY:
        all_models = SOTA_TAXONOMY_REGISTRY[args.paradigm]
    else:
        all_models = ALL_SOTA_BASELINES + GUM_NET_VARIANTS

    horizons = [args.horizon] if args.horizon else ALL_HORIZONS
    seeds = [int(s) for s in args.seeds.split(',')] if args.seeds else SEEDS
    targets = ['XANG', 'DAU'] if args.target == 'both' else [args.target]

    total_planned = len(all_models) * len(horizons) * len(seeds) * len(targets)
    print(f"  Models: {len(all_models)} | Horizons: {horizons} | Seeds: {seeds} | Targets: {targets}")
    print(f"  Total experiments planned: {total_planned}")

    # 1. Step 1: Backup results_v4/
    if os.path.exists(results_dir) and not args.dry_run:
        pid = os.getpid()
        backup_dir = f"{results_dir}_backup_{start_timestamp_str}_{pid}"
        print(f"\n[Step 1] Backing up active results to {backup_dir}...")
        try:
            shutil.copytree(results_dir, backup_dir)
            print("Backup completed successfully.")
        except Exception as e:
            print(f"Warning: Backup failed ({e}), continuing...")
    else:
        print("\n[Step 1] Skipping backup (dry-run or results_v4 does not exist).")

    # 2. Step 2: Clean only selected experiments if force-rerun is True
    if args.force_rerun:
        print("\n[Step 2] Force-rerun enabled. Cleaning matching experiment directories...")
        cleaned_count = 0
        for seed in seeds:
            for target in targets:
                for horizon in horizons:
                    for model in all_models:
                        exp_dir = os.path.join(results_dir, 'walkforward', model, f'{target}_H{horizon}_seed{seed}')
                        if os.path.exists(exp_dir):
                            try:
                                shutil.rmtree(exp_dir)
                                cleaned_count += 1
                            except Exception as e:
                                print(f"Warning: Failed to delete {exp_dir}: {e}")
        print(f" Cleaned {cleaned_count} existing run directories.")
    else:
        print("\n[Step 2] Force-rerun disabled. Keeping existing checkpoints.")

    # 3. Step 3: Run Models
    print("\n[Step 3] Executing experiments loop...")
    cmd_count = 0

    train_script = os.path.join(project_root, 'scripts', 'training', 'train_unified.py')
    for seed in seeds:
        for target in targets:
            for horizon in horizons:
                for model in all_models:
                    cmd_count += 1
                    
                    cmd = [
                        sys.executable,
                        train_script,
                        '--type', target,
                        '--model', model,
                        '--horizon', str(horizon),
                        '--seed', str(seed),
                        '--protocol', 'walkforward'
                    ]
                    
                    if args.dry_run:
                        if cmd_count <= 5 or cmd_count % 500 == 0:
                            print(f" [Planned {cmd_count}] {' '.join(cmd)}")
                    else:
                        print(f" Running [{cmd_count}/{total_planned}]: {' '.join(cmd)}")
                        try:
                            # Inherit environment (GUMNET_TEST_MODE is set from shell)
                            subprocess.run(cmd, check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"Error: Command failed with exit code {e.returncode}")
                            sys.exit(1)
                            
    print(f"Total experiments processed: {cmd_count}")

    # 4. Step 4-7: Invoke downstream compilation and validation scripts
    print("\n[Step 4-7] Invoking downstream validation and reporting pipeline...")
    
    gen_outputs_script = os.path.join(project_root, 'scripts', 'reports', 'generate_all_outputs.py')
    compile_script = os.path.join(project_root, 'scripts', 'reports', 'compile_completed_h_5seeds.py')
    dm_script = os.path.join(project_root, 'scripts', 'evaluation', 'dm_test_32models.py')
    effect_script = os.path.join(project_root, 'scripts', 'evaluation', 'effect_size_32models.py')

    if args.dry_run:
        print("Executing generate_all_outputs.py (which triggers mock data generation in dry-run mode)...")
        if os.path.exists(gen_outputs_script):
            subprocess.run([sys.executable, gen_outputs_script, '--results-dir', results_dir], check=False)
    else:
        if os.path.exists(compile_script):
            print("Running compile_completed_h_5seeds.py...")
            subprocess.run([sys.executable, compile_script], check=False)
        
        if os.path.exists(dm_script):
            print("Running dm_test_32models.py...")
            subprocess.run([sys.executable, dm_script, '--results-dir', results_dir], check=False)
        
        if os.path.exists(effect_script):
            print("Running effect_size_32models.py...")
            subprocess.run([sys.executable, effect_script, '--results-dir', results_dir], check=False)
        
        if os.path.exists(gen_outputs_script):
            print("Running generate_all_outputs.py...")
            subprocess.run([sys.executable, gen_outputs_script, '--results-dir', results_dir], check=False)

    elapsed_time = datetime.now() - start_time
    print(f"\nPipeline execution finished in {elapsed_time}")

if __name__ == '__main__':
    main()
