#!/usr/bin/env python3
"""
finalize_results.py
====================
Chạy sau khi training hoàn tất (50/50 runs).
Steps:
  1. Recompile results từ GUMNet v2 runs + giữ nguyên baselines từ compiled_results.csv
  2. Run MCS test
  3. Compute Average Rank + PICP
  4. Generate comparison report
  5. Print final summary cho paper

Usage:
    python3 scripts/finalize_results.py
    python3 scripts/finalize_results.py --check-only  (just show status)
"""
import os, sys, json, argparse
import pandas as pd
import numpy as np
from pathlib import Path

# Reconfigure stdout to support UTF-8 character printing on Windows
sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

RESDIR = os.path.join(BASE, 'results_v4', 'walkforward')
OUT_CSV = os.path.join(BASE, 'results_v4', 'compiled_results.csv')
SEEDS = [42, 123, 777, 2025, 9999]
TARGETS = ['XANG', 'DAU']
HORIZONS = [1, 3, 5, 10, 20, 60]
MODELS = ['GUMNet', 'LSTM', 'GRU', 'BiLSTM_Attention', 'XGBoost', 'PatchTST', 'DLinear']


def check_completion():
    """Check how many runs are complete."""
    print("=== Training Completion Status ===")
    total = 0; done = 0
    missing = []
    for model in MODELS:
        for target in TARGETS:
            for h in HORIZONS:
                for seed in SEEDS:
                    total += 1
                    dirpath = Path(RESDIR) / model / f'{target}_H{h}_seed{seed}'
                    if (dirpath / 'results.json').exists():
                        done += 1
                    else:
                        missing.append(f'{model}/{target}/H{h}/seed{seed}')
    
    gum_done = sum(1 for m in missing if not m.startswith('GUMNet'))
    gum_total = len(TARGETS) * len(HORIZONS) * len(SEEDS)
    
    print(f"Total: {done}/{total} runs complete")
    print(f"GUMNet: {gum_total - sum(1 for m in missing if m.startswith('GUMNet'))}/{gum_total}")
    
    print("\nMissing GUMNet runs:")
    for m in [x for x in missing if x.startswith('GUMNet')][:15]:
        print(f"  {m}")
    
    gum_remaining = sum(1 for m in missing if m.startswith('GUMNet'))
    return gum_remaining == 0


def recompile_gumnet_v2():
    """Recompile GUMNet v2 results and merge with v1 baselines."""
    print("\n=== Recompiling GUMNet v2 Results ===")
    
    # Load existing compiled results (has all baselines)
    df_old = pd.read_csv(OUT_CSV)
    df_baselines = df_old[df_old.Model != 'GUMNet'].copy()
    
    # Collect new GUMNet v2 results
    gum_rows = []
    gum_dir = Path(RESDIR) / 'GUMNet'
    
    for target in TARGETS:
        for h in HORIZONS:
            seed_metrics = {'MAE': [], 'RMSE': [], 'MAPE': [], 'R2': [], 'DA': []}
            found_seeds = []
            
            for seed in SEEDS:
                dirpath = gum_dir / f'{target}_H{h}_seed{seed}'
                result_file = dirpath / 'results.json'
                pred_file = dirpath / 'predictions.csv'
                
                if result_file.exists():
                    d = json.load(open(result_file))
                    m = d.get('metrics', d)
                    for metric in ['MAE', 'RMSE', 'MAPE', 'R2', 'DA']:
                        if metric in m:
                            seed_metrics[metric].append(m[metric])
                    found_seeds.append(seed)
            
            n = len(found_seeds)
            if n > 0:
                row = {
                    'Model': 'GUMNet', 'Target': target, 'Horizon': h,
                }
                for metric in ['MAE', 'RMSE', 'MAPE', 'R2', 'DA']:
                    vals = seed_metrics[metric]
                    if vals:
                        row[f'{metric}_mean'] = np.mean(vals)
                        row[f'{metric}_std'] = np.std(vals, ddof=1) if len(vals) > 1 else 0.0
                        row[f'{metric}_n'] = len(vals)
                    else:
                        row[f'{metric}_mean'] = np.nan
                        row[f'{metric}_std'] = np.nan
                        row[f'{metric}_n'] = 0
                
                gum_rows.append(row)
                print(f"  {target} H{h}: {n} seeds | MAE={row['MAE_mean']:.3f}±{row['MAE_std']:.3f} | R2={row['R2_mean']:.4f}")
            else:
                print(f"  {target} H{h}: NO DATA")
    
    # Add MASE column (set to nan for now)
    for col in ['MASE_mean', 'MASE_std', 'MASE_n']:
        if col not in df_baselines.columns:
            df_baselines[col] = np.nan
    
    df_gum_new = pd.DataFrame(gum_rows)
    for col in df_baselines.columns:
        if col not in df_gum_new.columns:
            df_gum_new[col] = np.nan
    
    df_final = pd.concat([df_gum_new, df_baselines], ignore_index=True)
    df_final.to_csv(OUT_CSV, index=False)
    print(f"\nSaved to: {OUT_CSV}")
    return df_final


def run_pipeline():
    """Run full post-processing pipeline."""
    import subprocess
    
    steps = [
        ('compile_results.py', 'Compiling results...'),
        ('compute_advanced_metrics.py', 'Computing Average Rank + PICP...'),
        ('model_confidence_set.py', 'Running MCS test...'),
        ('generate_comparison_report.py', 'Generating comparison report...'),
    ]
    
    for script, desc in steps:
        print(f"\n{desc}")
        result = subprocess.run(
            [sys.executable, f'scripts/{script}'],
            cwd=BASE, capture_output=True, text=True, encoding='utf-8', timeout=120
        )
        if result.returncode == 0:
            print(f"  ✅ {script} completed")
            # Print last 5 lines of output
            lines = result.stdout.strip().split('\n')
            for l in lines[-5:]:
                if l.strip():
                    print(f"  {l}")
        else:
            print(f"  ❌ {script} FAILED:")
            print(result.stderr[-500:])


def print_final_summary(df):
    """Print final paper-ready summary."""
    print("\n" + "="*80)
    print("FINAL RESULTS SUMMARY (for paper)")
    print("="*80)
    
    gum = df[df.Model == 'GUMNet']
    
    for target in TARGETS:
        print(f"\n### {target} ###")
        for h in HORIZONS:
            row = gum[(gum.Target==target)&(gum.Horizon==h)]
            if not row.empty:
                r = row.iloc[0]
                n = int(r['MAE_n']) if not np.isnan(r['MAE_n']) else 0
                if n < 5:
                    note = f" ⚠️ PARTIAL ({n}/5 seeds)"
                else:
                    note = ""
                print(f"  H{h:2d}: MAE={r['MAE_mean']:.3f}±{r['MAE_std']:.3f} | "
                      f"MAPE={r['MAPE_mean']:.2f}% | R²={r['R2_mean']:.4f}{note}")
    
    # Compare to key baselines
    print("\n### GUMNet vs Best Baseline (MAE) ###")
    for target in TARGETS:
        print(f"\n{target}:")
        for h in HORIZONS:
            gum_row = df[(df.Model=='GUMNet')&(df.Target==target)&(df.Horizon==h)]
            best_others = df[(df.Model!='GUMNet')&(df.Target==target)&(df.Horizon==h)].sort_values('MAE_mean')
            if not gum_row.empty and not best_others.empty:
                gum_mae = gum_row.iloc[0]['MAE_mean']
                best = best_others.iloc[0]
                delta = (gum_mae - best['MAE_mean'])/best['MAE_mean']*100
                flag = '✅' if delta < -0.5 else ('❌' if delta > 0.5 else '~')
                print(f"  H{h:2d}: GUMNet={gum_mae:.3f} | Best={best.Model}={best['MAE_mean']:.3f} | Δ={delta:+.1f}% {flag}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true', help='Only check completion status')
    parser.add_argument('--force', action='store_true', help='Run even if not all seeds complete')
    args = parser.parse_args()
    
    all_done = check_completion()
    
    if args.check_only:
        sys.exit(0)
    
    if not all_done and not args.force:
        print("\n⚠️  Training not complete. Run with --force to compile partial results.")
        print("    Or wait for training to finish and run again.")
        sys.exit(1)
    
    # Recompile GUMNet v2 results
    df = recompile_gumnet_v2()
    
    # Print final summary
    print_final_summary(df)
    
    # Optionally run full pipeline
    print("\n=== Running Analysis Pipeline ===")
    run_pipeline()
    
    print("\n" + "="*60)
    print("✅ finalize_results.py COMPLETE")
    print(f"  Results saved to: {OUT_CSV}")
    print(f"  Next: Review baseline_comparison.md and update manuscript")
