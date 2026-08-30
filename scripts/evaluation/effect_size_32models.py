#!/usr/bin/env python
"""
effect_size_32models.py
=======================
Computes practical significance (effect size) of performance differences between
the GUM-Net champion (e.g. GUMNet_Fusion) and SOTA baselines.
Uses the fast O(N log N) Mann-Whitney U rank statistic to compute Vargha-Delaney A12
and Cliff's Delta.
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

# Add project root to path for config import
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config import ALL_SOTA_BASELINES, GUM_NET_VARIANTS

def interpret_delta(delta):
    ad = abs(delta)
    if ad < 0.147:
        return 'negligible'
    elif ad < 0.330:
        return 'small'
    elif ad < 0.474:
        return 'medium'
    else:
        return 'large'

def compute_effect_size_fast(group1, group2):
    """
    Computes Cliff's Delta and Vargha-Delaney A12.
    Group 1: Baseline absolute errors.
    Group 2: GUMNet absolute errors.
    Returns: Cliff's Delta, Vargha-Delaney A12.
    A positive Delta and A12 > 0.5 indicate GUMNet has smaller errors (superior).
    """
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return 0.0, 0.5
        
    res = mannwhitneyu(group1, group2, alternative='two-sided')
    U1 = res.statistic
    a12 = U1 / (n1 * n2)
    delta = 2.0 * a12 - 1.0
    return delta, a12

def main():
    parser = argparse.ArgumentParser(description="Calculate non-parametric effect sizes")
    parser.add_argument('--results-dir', type=str, default='results_v4')
    parser.add_argument('--champion', type=str, default='GUMNet_Fusion',
                        help='GUMNet champion model name (default: GUMNet_Fusion)')
    args = parser.parse_args()

    results_dir = args.results_dir
    walkforward_dir = os.path.join(results_dir, 'walkforward')
    if not os.path.exists(walkforward_dir):
        print(f"Error: Walkforward directory {walkforward_dir} does not exist.")
        sys.exit(1)

    # Discover models in walkforward results
    all_models = sorted(os.listdir(walkforward_dir))
    
    # Identify champion GUMNet model
    champion = args.champion
    if champion not in all_models:
        # Fallback search for any GUMNet model
        gumnets = [m for m in GUM_NET_VARIANTS if m in all_models]
        if gumnets:
            champion = gumnets[0]
            print(f"Warning: Selected champion {args.champion} not found. Falling back to {champion}.")
        else:
            print("Error: No GUMNet variant results found in walkforward directory.")
            sys.exit(1)
            
    # Find SOTA baselines with results
    baselines = [m for m in ALL_SOTA_BASELINES if m in all_models]
    if not baselines:
        baselines = [m for m in all_models if not m.startswith('GUMNet')]
        print(f"Warning: No registered SOTA baselines found. Scanning all other folders: {baselines}")
        
    if not baselines:
        print("Error: No baseline model results found.")
        sys.exit(1)

    # Determine all target types and horizons present
    targets = set()
    horizons = set()
    for m in [champion] + baselines:
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

    print(f"Comparing champion: {champion}")
    print(f"Against baselines: {len(baselines)} models")
    print(f"Targets: {targets}")
    print(f"Horizons: {horizons}")

    records = []

    # Loop over target, horizon, and baseline models
    for target in targets:
        for horizon in horizons:
            # Load champion absolute errors across all seeds
            champ_errors = []
            champ_dir = os.path.join(walkforward_dir, champion)
            if not os.path.exists(champ_dir):
                continue
                
            for run_name in os.listdir(champ_dir):
                if run_name.startswith(f"{target}_H{horizon}_"):
                    pred_path = os.path.join(champ_dir, run_name, 'predictions.csv')
                    if os.path.exists(pred_path):
                        try:
                            df = pd.read_csv(pred_path)
                            df = df.sort_values(by=['date', 'product']).reset_index(drop=True)
                            champ_errors.append(df)
                        except Exception as e:
                            print(f"Error loading {pred_path}: {e}")
                            
            if not champ_errors:
                continue
                
            df_champ = pd.concat(champ_errors, axis=0).reset_index(drop=True)
            champ_abs_err = np.abs(df_champ['true'].values - df_champ['pred'].values)

            # Compare with each baseline
            for base in baselines:
                base_dir = os.path.join(walkforward_dir, base)
                base_errors = []
                for run_name in os.listdir(base_dir):
                    if run_name.startswith(f"{target}_H{horizon}_"):
                        pred_path = os.path.join(base_dir, run_name, 'predictions.csv')
                        if os.path.exists(pred_path):
                            try:
                                df = pd.read_csv(pred_path)
                                df = df.sort_values(by=['date', 'product']).reset_index(drop=True)
                                base_errors.append(df)
                            except Exception as e:
                                print(f"Error loading {pred_path}: {e}")
                                
                if not base_errors:
                    continue
                    
                df_base = pd.concat(base_errors, axis=0).reset_index(drop=True)
                base_abs_err = np.abs(df_base['true'].values - df_base['pred'].values)
                
                # Check length match
                min_len = min(len(champ_abs_err), len(base_abs_err))
                if min_len == 0:
                    continue
                
                # Group 1 = Baseline, Group 2 = GUMNet
                delta, a12 = compute_effect_size_fast(base_abs_err[:min_len], champ_abs_err[:min_len])
                magnitude = interpret_delta(delta)
                
                records.append({
                    'Baseline_Model': base,
                    'Champion_Model': champion,
                    'Target': target,
                    'Horizon': horizon,
                    'Cliff_Delta': delta,
                    'A12': a12,
                    'Magnitude': magnitude
                })

    if records:
        df_effect = pd.DataFrame(records)
        output_csv = os.path.join(results_dir, 'effect_size_matrix.csv')
        df_effect.to_csv(output_csv, index=False)
        print(f"Saved effect size matrix to {output_csv} ({len(df_effect)} comparisons)")
    else:
        print("No comparisons computed.")
        # Save empty placeholder to avoid breaking pipelines
        cols = ['Baseline_Model', 'Champion_Model', 'Target', 'Horizon', 'Cliff_Delta', 'A12', 'Magnitude']
        pd.DataFrame(columns=cols).to_csv(os.path.join(results_dir, 'effect_size_matrix.csv'), index=False)

if __name__ == '__main__':
    main()
