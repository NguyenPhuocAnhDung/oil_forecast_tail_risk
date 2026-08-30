#!/usr/bin/env python3
"""
compare_v1_v2.py
So sánh GUMNet v1 (compiled_results.csv) vs GUMNet v2 (results mới trong results_v4)
Chạy bất kỳ lúc nào để xem tiến độ so sánh.
"""
import json, os, glob
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1_CSV = os.path.join(BASE, 'results_v4', 'compiled_results.csv')
GUM_DIR = os.path.join(BASE, 'results_v4', 'walkforward', 'GUMNet')

TARGETS  = ['XANG', 'DAU']
HORIZONS = [1, 3, 5, 10, 20, 60]
SEEDS    = [42, 123, 777, 2025, 9999]
MODELS_BASELINE = ['LSTM', 'GRU', 'BiLSTM_Attention', 'XGBoost', 'PatchTST', 'DLinear']

df_v1 = pd.read_csv(V1_CSV)
df_gum_v1 = df_v1[df_v1['Model'] == 'GUMNet'].copy()

print('='*80)
print('GUMNet v1 vs v2 Comparison (live update)')
print('='*80)

rows = []
for target in TARGETS:
    print(f'\n{"─"*70}')
    print(f'  {target}')
    print(f'{"─"*70}')
    hdr = f'  {"H":<5} {"v1 MAE":>10} {"v2 MAE":>10} {"ΔMAE":>8} {"v1 R²":>9} {"v2 R²":>9}  {"Seeds":>6}  {"Status"}'
    print(hdr)
    print('  ' + '-'*70)

    for h in HORIZONS:
        # v1
        r1 = df_gum_v1[(df_gum_v1['Target']==target) & (df_gum_v1['Horizon']==h)]
        if r1.empty:
            continue
        v1 = r1.iloc[0]

        # v2: collect available seeds
        v2_maes, v2_r2s, v2_mapes = [], [], []
        for seed in SEEDS:
            f = os.path.join(GUM_DIR, f'{target}_H{h}_seed{seed}', 'results.json')
            if os.path.exists(f):
                with open(f) as fp:
                    r = json.load(fp)
                m = r['metrics']
                v2_maes.append(m['MAE'])
                v2_r2s.append(m['R2'])
                v2_mapes.append(m['MAPE'])

        n = len(v2_maes)
        if n == 0:
            status = '⏳ pending'
            line = f"  H{h:<4} {v1.MAE_mean:>10.3f} {'—':>10} {'—':>8} {v1.R2_mean:>9.4f} {'—':>9}  {n:>2}/{len(SEEDS)}  {status}"
        else:
            v2_mae  = np.mean(v2_maes)
            v2_r2   = np.mean(v2_r2s)
            delta   = v2_mae - v1.MAE_mean
            pct     = delta / v1.MAE_mean * 100

            if delta < -0.02:
                arrow = '✅↓'
            elif delta > 0.05:
                arrow = '🔴↑'
            else:
                arrow = '⚠️ ~'

            partial = '' if n == len(SEEDS) else f'(partial)'
            status  = f'{arrow} {pct:+.1f}% {partial}'
            line = f"  H{h:<4} {v1.MAE_mean:>10.3f} {v2_mae:>10.3f} {delta:>+8.3f} {v1.R2_mean:>9.4f} {v2_r2:>9.4f}  {n:>2}/{len(SEEDS)}  {status}"

            rows.append({'Target': target, 'Horizon': h, 'v1_MAE': v1.MAE_mean,
                         'v2_MAE': v2_mae, 'delta_MAE': delta, 'pct': pct,
                         'v1_R2': v1.R2_mean, 'v2_R2': v2_r2, 'n_seeds': n})
        print(line)

# Baseline comparison for context
print('\n\n' + '='*80)
print('  GUMNet v2 vs Baselines (best competitor per cell)')
print('='*80)
print(f'  {"H":<5} {"Target":<7} {"GUMv2 MAE":>10} {"Best Base":>12} {"Best MAE":>10} {"Gap":>8}')
print('  ' + '-'*60)
for target in TARGETS:
    for h in HORIZONS:
        # GUMNet v2
        v2_maes = []
        for seed in SEEDS:
            f = os.path.join(GUM_DIR, f'{target}_H{h}_seed{seed}', 'results.json')
            if os.path.exists(f):
                with open(f) as fp:
                    r = json.load(fp)
                v2_maes.append(r['metrics']['MAE'])
        if not v2_maes:
            continue
        gum_v2_mae = np.mean(v2_maes)
        n = len(v2_maes)

        # Best baseline
        subs = df_v1[(df_v1['Target']==target) & (df_v1['Horizon']==h) &
                     (df_v1['Model'].isin(MODELS_BASELINE))]
        if subs.empty:
            continue
        best_idx = subs['MAE_mean'].idxmin()
        best_model = subs.loc[best_idx, 'Model']
        best_mae   = subs.loc[best_idx, 'MAE_mean']
        gap = gum_v2_mae - best_mae
        flag = '🏆' if gap < 0 else ('❌' if gap > 0.1 else '~')
        print(f'  H{h:<4} {target:<7} {gum_v2_mae:>10.3f} {best_model:>12} {best_mae:>10.3f} {gap:>+8.3f} {flag} ({n}s)')

print()
total_gum = len(glob.glob(os.path.join(GUM_DIR, '*/results.json')))
print(f'Progress: {total_gum}/50 GUMNet v2 runs completed')
