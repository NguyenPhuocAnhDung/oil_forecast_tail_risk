#!/usr/bin/env python
"""
dm_test_32models.py
===================
Performs pairwise Diebold-Mariano (DM) tests and Hansen's Model Confidence Set (MCS)
across all models, targets, and horizons. Corrects the bootstrap centering bug and
optimizes execution speed using pre-generated circular block bootstrap indices and
original variance scaling.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.stats import t

# Add project root to path for config import
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config import ALL_SOTA_BASELINES, GUM_NET_VARIANTS

def compute_hac_variance(d, q):
    with np.errstate(invalid='ignore', divide='ignore'):
        T = len(d)
        d_mean = np.mean(d)
        d_centered = d - d_mean
        
        # autocovariances
        gamma = []
        gamma.append(np.mean(d_centered**2))
        for k in range(1, q + 1):
            if k < T:
                gamma.append(np.mean(d_centered[k:] * d_centered[:-k]))
            else:
                gamma.append(0.0)
                
        var_d = gamma[0]
        for k in range(1, q + 1):
            weight = 1.0 - (k / (q + 1))
            var_d += 2.0 * weight * gamma[k]
            
        return max(var_d / T, 1e-12)

def diebold_mariano_test(err1, err2, horizon, loss_type='mae'):
    """
    Computes pairwise DM test statistic and p-value.
    HLN small-sample correction is applied.
    """
    with np.errstate(invalid='ignore', divide='ignore'):
        if loss_type == 'mae':
            d = np.abs(err1) - np.abs(err2)
        elif loss_type == 'mse':
            d = err1**2 - err2**2
        else:
            raise ValueError(f"Unknown loss type: {loss_type}")
            
        T = len(d)
        if T < 5:
            return 0.0, 1.0
            
        d_mean = np.mean(d)
        
        # Bandwidth selection: max(0, min(h-1, floor(1.2 * T^(1/3))))
        q = int(max(0, min(horizon - 1, np.floor(1.2 * (T**(1/3))))))
        
        var_d_mean = compute_hac_variance(d, q)
        dm_stat = d_mean / np.sqrt(var_d_mean)
        
        # HLN small sample correction
        hln_factor = np.sqrt((T + 1 - 2 * horizon + (horizon * (horizon - 1)) / T) / T)
        dm_hln = dm_stat * hln_factor
        
        # Two-sided p-value
        p_value = 2.0 * (1.0 - t.cdf(np.abs(dm_hln), df=T - 1))
        if np.isnan(p_value):
            p_value = 1.0
            
        return dm_hln, p_value

def generate_block_bootstrap_indices(T, B, block_size):
    indices = np.zeros((B, T), dtype=int)
    num_blocks = int(np.ceil(T / block_size))
    for b in range(B):
        block_starts = np.random.randint(0, T, size=num_blocks)
        idx_list = []
        for start in block_starts:
            block_idx = (np.arange(start, start + block_size)) % T
            idx_list.append(block_idx)
        indices[b, :] = np.concatenate(idx_list)[:T]
    return indices

def run_mcs(L, alpha=0.10, B=1000, horizon=3):
    """
    Hansen's Model Confidence Set (MCS) procedure.
    L: numpy array [T, M] of model losses.
    alpha: significance level (default 0.10).
    B: number of bootstrap iterations.
    """
    with np.errstate(invalid='ignore', divide='ignore'):
        T, M = L.shape
        if T == 0 or M == 0:
            return list(range(M)), {i: 1.0 for i in range(M)}
        if M <= 1:
            return list(range(M)), {i: 1.0 for i in range(M)}

        # Pre-generate bootstrap indices: [B, T]
        block_size = int(max(1, np.floor(T**0.25)))
        boot_indices = generate_block_bootstrap_indices(T, B, block_size)
        
        # Initialize variables
        active_set = list(range(M))
        eliminated_pvals = {}
        
        # We will step-by-step eliminate models
        step = 0
        while len(active_set) > 1:
            L_active = L[:, active_set]
            curr_M = len(active_set)
            
            # 1. Compute original series statistics
            L_bar = np.mean(L_active, axis=0) # [M_curr]
            sum_L_bar = np.sum(L_bar)
            d_bar = (curr_M * L_bar - sum_L_bar) / (curr_M - 1) # [M_curr]
            
            # Compute relative loss series d_{i., t} for each model: [T, M_curr]
            sum_L = np.sum(L_active, axis=1, keepdims=True) # [T, 1]
            d_series = (curr_M * L_active - sum_L) / (curr_M - 1) # [T, M_curr]
            
            # Compute HAC standard error for each model's relative loss series
            q = int(max(0, min(horizon - 1, np.floor(1.2 * (T**(1/3))))))
            std_hac = np.zeros(curr_M)
            for i in range(curr_M):
                std_hac[i] = np.sqrt(compute_hac_variance(d_series[:, i], q))
                
            # Avoid division by zero
            std_hac = np.clip(std_hac, 1e-12, None)
            
            # Studentized sample statistics
            t_sample = d_bar / std_hac # [M_curr]
            T_max_sample = np.max(t_sample)
            
            # 2. Bootstrapping (optimized with pre-generated indices and original variance scaling)
            L_bar_boot = np.mean(L_active[boot_indices], axis=1) # [B, M_curr]
            sum_L_bar_boot = np.sum(L_bar_boot, axis=1, keepdims=True) # [B, 1]
            d_bar_boot = (curr_M * L_bar_boot - sum_L_bar_boot) / (curr_M - 1) # [B, M_curr]
            
            # Center the bootstrap distribution under null
            d_bar_boot_centered = d_bar_boot - d_bar # [B, M_curr]
            
            # Studentized bootstrap statistics
            t_boot = d_bar_boot_centered / std_hac # [B, M_curr]
            T_max_boot = np.max(t_boot, axis=1) # [B]
            
            # Compute bootstrap p-value
            p_val = np.mean(T_max_boot >= T_max_sample)
            
            # Find the model to eliminate (largest t_sample)
            worst_idx_in_active = np.argmax(t_sample)
            worst_model = active_set[worst_idx_in_active]
            
            eliminated_pvals[worst_model] = p_val
            
            if p_val >= alpha:
                # Cannot reject the null hypothesis of equal predictive ability, stop.
                break
            else:
                # Reject, eliminate worst model
                active_set.remove(worst_model)
                step += 1

        # Remaining models are in the superior set
        for m in active_set:
            eliminated_pvals[m] = 1.0
            
        # Ensure monotonicity of p-values
        # For Hansen's MCS, the final p-value for the eliminated model at step k is
        # max_{j<=k} p_val_j.
        # Let's reconstruct the elimination order
        elim_order = sorted(eliminated_pvals.keys(), key=lambda x: eliminated_pvals[x] if x not in active_set else 2.0)
        max_p = 0.0
        mcs_pvals = {}
        for m in elim_order:
            p = eliminated_pvals[m]
            if m not in active_set:
                max_p = max(max_p, p)
                mcs_pvals[m] = max_p
            else:
                mcs_pvals[m] = 1.0
                
        return active_set, mcs_pvals

def main():
    parser = argparse.ArgumentParser(description="econometric testing (DM & MCS)")
    parser.add_argument('--results-dir', type=str, default='results_v4')
    args = parser.parse_args()

    results_dir = args.results_dir
    walkforward_dir = os.path.join(results_dir, 'walkforward')
    if not os.path.exists(walkforward_dir):
        print(f"Error: Walkforward directory {walkforward_dir} does not exist.")
        sys.exit(1)

    # 1. Discover all models, targets, horizons with results
    all_models = sorted(os.listdir(walkforward_dir))
    
    # We want to filter for models in our registry
    candidate_models = [m for m in (ALL_SOTA_BASELINES + GUM_NET_VARIANTS) if m in all_models]
    if not candidate_models:
        candidate_models = all_models # Fallback to all models found if none in registry
        
    # Determine all target types and horizons present
    targets = set()
    horizons = set()
    for m in candidate_models:
        m_dir = os.path.join(walkforward_dir, m)
        if not os.path.isdir(m_dir):
            continue
        for run_name in os.listdir(m_dir):
            parts = run_name.split('_')
            if len(parts) >= 2:
                targets.add(parts[0])
                if parts[1].startswith('H'):
                    try:
                        horizons.add(int(parts[1][1:]))
                    except ValueError:
                        pass
                        
    targets = sorted(list(targets))
    horizons = sorted(list(horizons))

    print(f"Models found: {len(candidate_models)}")
    print(f"Targets found: {targets}")
    print(f"Horizons found: {horizons}")

    # To store MCS outputs
    mcs_records = []

    # 2. Loop over targets and horizons
    for target in targets:
        for horizon in horizons:
            print(f"\nProcessing {target} H{horizon}...")
            
            # Load and align errors across all models
            model_dfs = {}
            for m in candidate_models:
                m_dir = os.path.join(walkforward_dir, m)
                if not os.path.isdir(m_dir):
                    continue
                # Find all seeds
                seed_data = []
                for run_name in os.listdir(m_dir):
                    if run_name.startswith(f"{target}_H{horizon}_"):
                        pred_path = os.path.join(m_dir, run_name, 'predictions.csv')
                        if os.path.exists(pred_path):
                            try:
                                df = pd.read_csv(pred_path)
                                # Assign a 'seed' column based on the run folder name
                                seed_val = run_name.split('_')[-1]
                                df['seed'] = seed_val
                                # Set the DataFrame index to ['date', 'product', 'seed'] and deduplicate
                                df = df.set_index(['date', 'product', 'seed'])
                                df = df[~df.index.duplicated(keep='first')]
                                seed_data.append(df)
                            except Exception as e:
                                print(f"Error loading {pred_path}: {e}")
                
                if seed_data:
                    # Concat across seeds and deduplicate
                    df_concat = pd.concat(seed_data, axis=0)
                    df_concat = df_concat[~df_concat.index.duplicated(keep='first')]
                    model_dfs[m] = df_concat
                    
            if len(model_dfs) < 2:
                print(f"Not enough models with results for {target} H{horizon}. Skipping.")
                continue

            # Find the common index intersection across all models
            common_idx = None
            for m, df in model_dfs.items():
                if common_idx is None:
                    common_idx = df.index
                else:
                    common_idx = common_idx.intersection(df.index)

            # Slice each model's DataFrame to only keep rows in the common index intersection,
            # sort the index, and then extract the prediction and error values.
            model_errors = {}
            model_preds = {}
            for m in model_dfs.keys():
                df_sliced = model_dfs[m].loc[common_idx]
                df_sliced = df_sliced.sort_index()
                model_preds[m] = df_sliced['pred'].values
                model_errors[m] = df_sliced['true'].values - df_sliced['pred'].values

            available_models = sorted(list(model_errors.keys()))
            num_m = len(available_models)
            
            # Aligned loss series
            T_len = len(model_errors[available_models[0]])
            losses_mae = np.zeros((T_len, num_m))
            losses_mse = np.zeros((T_len, num_m))
            
            for idx, m in enumerate(available_models):
                losses_mae[:, idx] = np.abs(model_errors[m])
                losses_mse[:, idx] = model_errors[m]**2

            # A. Pairwise DM Tests
            for loss_type in ['mae', 'mse']:
                dm_matrix = np.zeros((num_m, num_m))
                p_matrix = np.zeros((num_m, num_m))
                
                for i in range(num_m):
                    for j in range(num_m):
                        if i == j:
                            dm_matrix[i, j] = 0.0
                            p_matrix[i, j] = 1.0
                        else:
                            stat, pval = diebold_mariano_test(
                                model_errors[available_models[i]],
                                model_errors[available_models[j]],
                                horizon,
                                loss_type=loss_type
                            )
                            dm_matrix[i, j] = stat
                            p_matrix[i, j] = pval
                            
                # Save matrices
                df_dm = pd.DataFrame(dm_matrix, index=available_models, columns=available_models)
                df_p = pd.DataFrame(p_matrix, index=available_models, columns=available_models)
                
                dm_csv_path = os.path.join(results_dir, f"dm_stat_matrix_{target}_H{horizon}_{loss_type}.csv")
                p_csv_path = os.path.join(results_dir, f"dm_pvalue_matrix_{target}_H{horizon}_{loss_type}.csv")
                
                df_dm.to_csv(dm_csv_path)
                df_p.to_csv(p_csv_path)
                
                # Also save standard name dm_pvalue_matrix_{horizon}.csv as a fallback or for MAE target
                if loss_type == 'mae' and target == 'XANG': # default fallback
                    df_p.to_csv(os.path.join(results_dir, f"dm_pvalue_matrix_{horizon}.csv"))

            # B. MCS test (runs on MAE by default, and also MSE)
            for loss_type in ['mae', 'mse']:
                L = losses_mae if loss_type == 'mae' else losses_mse
                active_set, mcs_pvals = run_mcs(L, alpha=0.10, B=1000, horizon=horizon)
                
                for idx, m in enumerate(available_models):
                    mcs_records.append({
                        'Target': target,
                        'Horizon': horizon,
                        'Model': m,
                        'Loss_Type': loss_type,
                        'MCS_pvalue': mcs_pvals[idx],
                        'In_MCS': int(mcs_pvals[idx] >= 0.10)
                    })

    if mcs_records:
        df_mcs = pd.DataFrame(mcs_records)
        mcs_csv_path = os.path.join(results_dir, 'mcs_superior_set.csv')
        df_mcs.to_csv(mcs_csv_path, index=False)
        print(f"\nSaved MCS results to {mcs_csv_path}")

if __name__ == '__main__':
    # Set random seed for bootstrap reproducibility
    np.random.seed(42)
    main()
