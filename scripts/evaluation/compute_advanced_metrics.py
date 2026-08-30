#!/usr/bin/env python3
"""
compute_advanced_metrics.py
===========================
Tính Average Rank + PICP + PINAW cho bảng kết quả Q1 paper.

Average Rank: rank GUMNet trên (MAE, MAPE, R²) across horizons/targets
PICP: Prediction Interval Coverage Probability (target ≥ 90%)
PINAW: Prediction Interval Normalized Average Width
"""
import json, os, glob, sys
import numpy as np
import pandas as pd
from scipy import stats

# Reconfigure stdout to support UTF-8 character printing on Windows
sys.stdout.reconfigure(encoding='utf-8')

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(BASE, 'results_v4', 'walkforward')
CSV     = os.path.join(BASE, 'results_v4', 'compiled_results.csv')

MODELS   = ['GUMNet', 'LSTM', 'GRU', 'BiLSTM_Attention', 'XGBoost', 'PatchTST', 'DLinear']
TARGETS  = ['XANG', 'DAU']
HORIZONS = [1, 3, 5, 10, 20, 60]
SEEDS    = [42, 123, 777, 2025, 9999]

# ─────────────────────────────────────────────
# 1. Average Rank Table
# ─────────────────────────────────────────────
df = pd.read_csv(CSV)

print('='*70)
print('TABLE: Average Rank (lower = better, across all horizons+targets)')
print('='*70)

rank_records = []
for target in TARGETS:
    for h in HORIZONS:
        sub = df[(df['Target']==target) & (df['Horizon']==h)]
        if sub.empty: continue
        for metric in ['MAE', 'MAPE', 'R2']:
            ascending = (metric != 'R2')
            sub2 = sub.sort_values(f'{metric}_mean', ascending=ascending).reset_index(drop=True)
            for rank_idx, row in sub2.iterrows():
                rank_records.append({
                    'Model': row['Model'], 'Target': target, 'Horizon': h,
                    'Metric': metric, 'Rank': rank_idx + 1
                })

df_rank = pd.DataFrame(rank_records)
avg_rank = df_rank.groupby('Model')['Rank'].mean().sort_values()
print(avg_rank.to_string())

print('\n--- Per-metric Average Rank ---')
piv = df_rank.groupby(['Model','Metric'])['Rank'].mean().unstack()
print(piv.round(2).to_string())

print('\n--- Per-horizon Average Rank for GUMNet ---')
gum = df_rank[df_rank['Model']=='GUMNet']
print(gum.groupby('Horizon')['Rank'].mean().to_string())

# ─────────────────────────────────────────────
# 2. PICP + PINAW (from GUMNet predictions)
# ─────────────────────────────────────────────
print('\n\n' + '='*70)
print('TABLE: Uncertainty Calibration (GUMNet only)')
print('PICP = P(y ∈ [Q10, Q90])  target ≥ 90%')
print('PINAW = (Q90-Q10) / range(y_train)  lower = sharper')
print('='*70)
print(f'{"H":<5} {"Target":<7} {"PICP(%)":>10} {"PINAW":>10} {"Calibrated?":>12}')
print('-'*50)

for target in TARGETS:
    for h in HORIZONS:
        picps, pinaws = [], []
        for seed in SEEDS:
            pred_f = os.path.join(RES_DIR, 'GUMNet', f'{target}_H{h}_seed{seed}', 'predictions.csv')
            if not os.path.exists(pred_f):
                continue
            pred_df = pd.read_csv(pred_f)
            if 'q10' not in pred_df.columns or 'q90' not in pred_df.columns:
                # Try alternate column names
                cols = pred_df.columns.tolist()
                q_cols = [c for c in cols if c.startswith('q') or 'quantile' in c.lower()]
                if len(q_cols) < 3:
                    continue
                q10_col, q50_col, q90_col = q_cols[0], q_cols[1], q_cols[2]
            else:
                q10_col, q90_col = 'q10', 'q90'

            y_true = pred_df['true'].values
            q10    = pred_df[q10_col].values
            q90    = pred_df[q90_col].values

            covered = ((y_true >= q10) & (y_true <= q90)).mean() * 100
            width   = (q90 - q10).mean()
            y_range = y_true.std() * 4  # approx range
            pinaw   = width / (y_range + 1e-8)

            picps.append(covered)
            pinaws.append(pinaw)

        if picps:
            picp_mean = np.mean(picps)
            pinaw_mean = np.mean(pinaws)
            calibrated = '✅' if picp_mean >= 88 else '⚠️'
            print(f'H{h:<4} {target:<7} {picp_mean:>10.1f} {pinaw_mean:>10.3f} {calibrated:>12}')
        else:
            print(f'H{h:<4} {target:<7} {"N/A":>10} {"N/A":>10} {"⏳":>12}')

# ─────────────────────────────────────────────
# 3. Directional Accuracy Leaderboard
# ─────────────────────────────────────────────
print('\n\n' + '='*70)
print('TABLE: Directional Accuracy (DA%) — GUMNet advantage domain')
print('='*70)
print(f'{"H":<5} {"Target":<7}', end='')
for m in MODELS:
    print(f' {m[:8]:>9}', end='')
print()
print('-'*90)

for target in TARGETS:
    for h in HORIZONS:
        sub = df[(df['Target']==target) & (df['Horizon']==h)]
        if sub.empty: continue
        print(f'H{h:<4} {target:<7}', end='')
        for model in MODELS:
            row = sub[sub['Model']==model]
            if row.empty:
                print(f' {"—":>9}', end='')
            else:
                da = row.iloc[0]['DA_mean']
                marker = '*' if model == 'GUMNet' else ' '
                print(f' {da:>8.1f}{marker}', end='')
        print()

print('\n* = GUMNet')

# ─────────────────────────────────────────────
# 4. Summary for paper
# ─────────────────────────────────────────────
gum_avg_rank = avg_rank['GUMNet']
best_competitor_rank = avg_rank.drop('GUMNet').min()
best_competitor = avg_rank.drop('GUMNet').idxmin()

print(f'\n\n{"="*70}')
print('SUMMARY FOR PAPER')
print(f'{"="*70}')
print(f'GUMNet Average Rank: {gum_avg_rank:.2f}/7')
print(f'Best baseline ({best_competitor}): {best_competitor_rank:.2f}/7')
print(f'GUMNet better by: {best_competitor_rank - gum_avg_rank:.2f} rank positions')
print()

# Count cells where GUMNet is #1
n_first = 0
n_cells = 0
for target in TARGETS:
    for h in HORIZONS:
        sub = df[(df['Target']==target) & (df['Horizon']==h)]
        if sub.empty: continue
        n_cells += 1
        best = sub.sort_values('MAE_mean').iloc[0]['Model']
        if best == 'GUMNet':
            n_first += 1

print(f'Cells where GUMNet MAE #1: {n_first}/{n_cells}')
print(f'Cells where GUMNet in top-3: ', end='')
n_top3 = 0
for target in TARGETS:
    for h in HORIZONS:
        sub = df[(df['Target']==target) & (df['Horizon']==h)]
        if sub.empty: continue
        rank = sub.sort_values('MAE_mean').reset_index(drop=True)
        gum_rank = rank[rank['Model']=='GUMNet'].index[0] + 1
        if gum_rank <= 3:
            n_top3 += 1
print(f'{n_top3}/{n_cells}')
