#!/usr/bin/env python3
"""
scripts/dm_test_da.py — Diebold-Mariano Test for Directional Accuracy
DA-First Framework: Test if GUMNet's DA advantage over DLinear is statistically significant.

Key comparison: GUMNet vs DLinear DA at H60 (primary claim in revised contribution)
"""
import numpy as np
import pandas as pd
import json
from pathlib import Path
from scipy import stats

BASE = Path(__file__).resolve().parent.parent
RESDIR = BASE / 'results_v4' / 'walkforward'
SEEDS = [42, 123, 777, 2025, 9999]
HORIZONS = [1, 3, 5, 10, 20, 60]

def load_predictions(model: str, target: str, horizon: int, seed: int):
    """Load predictions.csv for a given run."""
    d = RESDIR / model / f'{target}_H{horizon}_seed{seed}'
    f = d / 'predictions.csv'
    if not f.exists():
        return None
    return pd.read_csv(f)

def directional_correct(true_vals, pred_vals, output_dim=2):
    """Return 1/0 array: 1 if direction predicted correctly, handling 2D shapes."""
    n_samples = len(true_vals)
    n_rows = n_samples // output_dim
    if n_rows <= 1:
        return np.zeros(0)
    # Reshape back to [N, output_dim] to avoid cross-product contamination
    true_2d = true_vals[:n_rows * output_dim].reshape(n_rows, output_dim)
    pred_2d = pred_vals[:n_rows * output_dim].reshape(n_rows, output_dim)
    
    # Calculate direction along temporal axis (axis=0)
    true_dir = np.sign(np.diff(true_2d, axis=0))
    pred_dir = np.sign(np.diff(pred_2d, axis=0))
    return (true_dir == pred_dir).astype(float).flatten()

def dm_test_da(errors_1, errors_2, h=1, alternative='less'):
    """
    Diebold-Mariano test for DA loss differentials.
    errors_1 = DA errors of model 1 (1 = wrong, 0 = correct)
    errors_2 = DA errors of model 2
    alternative = 'less' means H1: errors_1 < errors_2 (model 1 better)
    """
    d = errors_1 - errors_2  # loss differential
    n = len(d)
    d_bar = np.mean(d)
    
    # HAC variance (Newey-West with h lags and bandwidth limit)
    gamma0 = np.var(d, ddof=1)
    gamma_h = 0.0
    
    # Econometric bandwidth limit: Floor(1.2 * N^(1/3))
    max_lag = min(h, int(np.floor(1.2 * n**(1/3))))
    max_lag = max(1, max_lag)
    
    for k in range(1, max_lag + 1):
        w = 1 - k / (max_lag + 1)
        gamma_h += 2 * w * np.mean((d[k:] - d_bar) * (d[:-k] - d_bar))
    
    var_d = (gamma0 + gamma_h) / n
    if var_d <= 0:
        return np.nan, np.nan
    
    dm_stat = d_bar / np.sqrt(var_d)
    p_value = stats.norm.cdf(dm_stat) if alternative == 'less' else 1 - stats.norm.cdf(dm_stat)
    return dm_stat, p_value

print("=" * 70)
print("DA DIEBOLD-MARIANO TEST: GUMNet vs DLinear")
print("H0: No difference in DA | H1: GUMNet DA > DLinear DA")
print("=" * 70)

for target in ['XANG', 'DAU']:
    print(f"\n{'='*50}")
    print(f"Target: {target}")
    print(f"{'='*50}")
    print(f"{'Horizon':<8} {'GUMNet DA':>12} {'DLinear DA':>12} {'DM stat':>10} {'p-value':>10} {'Sig':>6}")
    print("-" * 60)
    
    for h in HORIZONS:
        gumnet_da_vals = []
        dlinear_da_vals = []
        
        all_g_errors = []
        all_d_errors = []
        
        for seed in SEEDS:
            gum_pred = load_predictions('GUMNet', target, h, seed)
            dln_pred = load_predictions('DLinear', target, h, seed)
            
            if gum_pred is None or dln_pred is None:
                continue
            
            g_true = gum_pred['true'].values
            g_pred = gum_pred['pred'].values
            d_true = dln_pred['true'].values
            d_pred = dln_pred['pred'].values
            
            # DA values (correctly matched predictions)
            min_len = min(len(g_true), len(d_true))
            g_correct = directional_correct(g_true[:min_len], g_pred[:min_len])
            d_correct = directional_correct(d_true[:min_len], d_pred[:min_len])
            
            if len(g_correct) > 0 and len(d_correct) > 0:
                gumnet_da_vals.append(np.mean(g_correct) * 100)
                dlinear_da_vals.append(np.mean(d_correct) * 100)
                
                # Save temporal error arrays (1 = incorrect direction)
                all_g_errors.append(1 - g_correct)
                all_d_errors.append(1 - d_correct)
        
        if not gumnet_da_vals:
            print(f"H{h:<7} {'N/A':>12} {'N/A':>12} {'N/A':>10} {'N/A':>10} {'':>6}")
            continue
        
        g_mean = np.mean(gumnet_da_vals)
        d_mean = np.mean(dlinear_da_vals) if dlinear_da_vals else 0
        
        if all_g_errors:
            g_err_concat = np.concatenate(all_g_errors)
            d_err_concat = np.concatenate(all_d_errors)
            
            dm_stat, p_val = dm_test_da(g_err_concat, d_err_concat, h=min(h, 5))
            sig = '***' if p_val < 0.01 else ('**' if p_val < 0.05 else ('*' if p_val < 0.10 else ''))
            print(f"H{h:<7} {g_mean:>11.1f}% {d_mean:>11.1f}% {dm_stat:>10.3f} {p_val:>10.4f} {sig:>6}")
        else:
            print(f"H{h:<7} {g_mean:>11.1f}% {d_mean:>11.1f}% {'N/A':>10} {'N/A':>10} {'':>6}")

print()
print("Significance: *** p<0.01  ** p<0.05  * p<0.10")
print("DM stat < 0 means GUMNet has fewer DA errors (better DA)")
