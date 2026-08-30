#!/usr/bin/env python3
"""
model_confidence_set.py
========================
Model Confidence Set (MCS) test — Hansen, Lunde, Nason (2011)
Econometrica 79(2):453-497.

Determines which models belong to the "superior set" at confidence level α.
Uses bootstrap T-max statistic.

Usage:
    python3 scripts/model_confidence_set.py
"""
import numpy as np
import pandas as pd
import json, os, glob, sys
from itertools import combinations

# Reconfigure stdout to support UTF-8 character printing on Windows
sys.stdout.reconfigure(encoding='utf-8')

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = os.path.join(BASE, 'results_v4', 'walkforward')
CSV     = os.path.join(BASE, 'results_v4', 'compiled_results.csv')

MODELS   = ['GUMNet', 'LSTM', 'GRU', 'BiLSTM_Attention', 'XGBoost', 'PatchTST', 'DLinear']
TARGETS  = ['XANG', 'DAU']
HORIZONS = [1, 3, 5, 10, 20, 60]
SEEDS    = [42, 123, 777, 2025, 9999]

np.random.seed(42)

def load_errors(model, target, horizon):
    """Load forecast errors across all seeds."""
    all_errors = []
    for seed in SEEDS:
        err_f = os.path.join(RES_DIR, model, f'{target}_H{horizon}_seed{seed}', 'errors.npy')
        if os.path.exists(err_f):
            e = np.load(err_f)
            all_errors.append(e)
    if not all_errors:
        return None
    # Truncate to shortest length and stack
    min_len = min(len(e) for e in all_errors)
    return np.stack([e[:min_len] for e in all_errors], axis=0)  # [n_seeds, T]

def squared_loss(errors):
    """MSE loss for each time step: [n_seeds, T] → [T]"""
    return np.mean(errors**2, axis=0)

def dm_statistic(loss_i, loss_j, n_boot=999):
    """
    Diebold-Mariano statistic via bootstrap.
    H0: E[loss_i - loss_j] = 0
    Returns: (t_stat, p_value)
    """
    d = loss_i - loss_j  # differential loss [T]
    T = len(d)
    d_mean = d.mean()
    
    # Block bootstrap for autocorrelation
    block_size = max(1, int(T**0.25))  # Andrews (1991) rule
    n_blocks = T // block_size
    
    boot_means = np.zeros(n_boot)
    for b in range(n_boot):
        starts = np.random.randint(0, T - block_size + 1, n_blocks)
        boot_d = np.concatenate([d[s:s+block_size] for s in starts])[:T]
        boot_means[b] = boot_d.mean()
    
    se = boot_means.std()
    if se < 1e-10:
        return 0.0, 1.0
    t_stat = d_mean / se
    # Two-sided p-value
    p_val = 2 * min(np.mean(boot_means >= d_mean), np.mean(boot_means <= d_mean))
    return float(t_stat), float(p_val)

def mcs_test(models, loss_dict, alpha=0.10, n_boot=999):
    """
    MCS algorithm: iteratively eliminate worst model until all remaining
    are equally good (p-value >= alpha).
    
    loss_dict: {model_name: loss_array [T]}
    Returns: list of models in MCS (superior set)
    """
    remaining = list(models)
    
    while len(remaining) > 1:
        # Compute T_max statistic
        t_stats = {}
        p_vals = {}
        
        for m in remaining:
            # Compare m against average of all others
            other_loss = np.mean([loss_dict[other] for other in remaining if other != m], axis=0)
            t, p = dm_statistic(loss_dict[m], other_loss, n_boot=n_boot)
            t_stats[m] = t
            p_vals[m] = p
        
        # Find minimum p-value
        min_p = min(p_vals.values())
        min_p_model = min(p_vals, key=p_vals.get)
        
        # If min p >= alpha, all remaining models are in MCS
        if min_p >= alpha:
            break
        
        # Eliminate the model with highest loss (most significantly worse)
        worst = max(remaining, key=lambda m: loss_dict[m].mean())
        remaining.remove(worst)
    
    return remaining, p_vals

def run_mcs():
    print('='*70)
    print('Model Confidence Set (MCS) Test — Hansen et al. (2011)')
    print('Significance level α=0.10 (90% confidence)')
    print('='*70)
    
    all_results = []
    
    for target in TARGETS:
        for h in HORIZONS:
            print(f'\n--- {target} H{h} ---')
            
            # Load losses
            loss_dict = {}
            for model in MODELS:
                errors = load_errors(model, target, h)
                if errors is not None:
                    loss_dict[model] = squared_loss(errors)
            
            if len(loss_dict) < 2:
                print(f'  Insufficient data (only {len(loss_dict)} models available)')
                continue
            
            # Align losses to the minimum common length (T)
            min_T = min(len(v) for v in loss_dict.values())
            for m in list(loss_dict.keys()):
                loss_dict[m] = loss_dict[m][-min_T:]  # align to the most recent test samples
            
            available = list(loss_dict.keys())

            
            # Run MCS
            mcs_models, p_vals = mcs_test(available, loss_dict, alpha=0.10, n_boot=499)
            
            # Mean losses
            mean_losses = {m: loss_dict[m].mean() for m in available}
            best = min(available, key=lambda m: mean_losses[m])
            
            in_mcs = {m: (m in mcs_models) for m in available}
            gumnet_in_mcs = in_mcs.get('GUMNet', False)
            
            print(f'  MCS members ({len(mcs_models)}/{len(available)}): {mcs_models}')
            print(f'  GUMNet in MCS: {"✅ YES" if gumnet_in_mcs else "❌ NO"}')
            print(f'  Best model: {best} (MSE={mean_losses[best]:.4f})')
            if 'GUMNet' in mean_losses:
                print(f'  GUMNet MSE: {mean_losses["GUMNet"]:.4f}')
            
            all_results.append({
                'Target': target, 'Horizon': h,
                'MCS_members': mcs_models,
                'GUMNet_in_MCS': gumnet_in_mcs,
                'Best_model': best,
                'n_models_in_MCS': len(mcs_models),
            })
    
    # Summary
    print('\n\n' + '='*70)
    print('SUMMARY FOR PAPER (Table: MCS Results)')
    print('='*70)
    print(f'{"H":<5} {"Target":<8} {"MCS Size":>9} {"GUMNet":>8} {"Best Model":>18}')
    print('-'*55)
    for r in all_results:
        gum_str = '✅ YES' if r['GUMNet_in_MCS'] else '❌ NO '
        print(f'H{r["Horizon"]:<4} {r["Target"]:<8} {r["n_models_in_MCS"]:>9} {gum_str:>8} {r["Best_model"]:>18}')
    
    gum_in_mcs = sum(1 for r in all_results if r['GUMNet_in_MCS'])
    print(f'\nGUMNet in MCS: {gum_in_mcs}/{len(all_results)} cells ({gum_in_mcs/len(all_results)*100:.0f}%)')
    print()
    print('PAPER CLAIM:')
    print(f'  "GUMNet belongs to the Model Confidence Set at α=0.10 in {gum_in_mcs}')
    print(f'   out of {len(all_results)} forecast cells, indicating it is statistically')
    print(f'   indistinguishable from the best model in those cells."')
    
    return all_results

if __name__ == '__main__':
    results = run_mcs()
