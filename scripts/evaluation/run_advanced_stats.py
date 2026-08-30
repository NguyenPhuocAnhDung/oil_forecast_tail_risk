import os
import sys
import json
import glob
import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.tsa.stattools import adfuller, kpss

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config import DATA_PATH, RESULTS_DIR, BASELINES

def dm_test(e1, e2, h=1):
    """
    Diebold-Mariano Test with HAC variance and HLN (1997) small-sample correction.
    e1: Errors of Model 1 (e.g. GUMNet)
    e2: Errors of Model 2 (e.g. Baseline)
    h: Forecast horizon
    Returns: (DM statistic with HLN correction, p-value)
    """
    d = e1**2 - e2**2
    n = len(d)
    if n < 3:
        return np.nan, np.nan

    mean_d = np.mean(d)

    # HAC Variance (Newey-West type)
    # Autocovariance up to lag h-1 with bandwidth restriction to avoid noise in small samples
    gamma_0 = np.var(d, ddof=1)
    var_d = gamma_0
    
    # Econometric bandwidth limit: Floor(1.2 * N^(1/3))
    max_lag = min(h - 1, int(np.floor(1.2 * n**(1/3))))
    max_lag = max(1, max_lag)
    
    for lag in range(1, max_lag + 1):
        # Global mean covariance formulation (Q1 econometric standard)
        gamma_k = np.mean((d[lag:] - mean_d) * (d[:-lag] - mean_d))
        var_d += 2 * gamma_k

    # Prevent negative variance due to numerical issues
    var_d = max(var_d, 1e-8)

    # Standard DM stat
    stat = mean_d / np.sqrt(var_d / n)

    # Harvey, Leybourne, and Newbold (1997) small-sample correction
    # Factor = sqrt((n + 1 - 2*h + (h/n)*(h-1)) / n)
    hln_factor = (n + 1 - 2 * h + (h / n) * (h - 1)) / n
    hln_factor = max(hln_factor, 1e-8)  # safety
    correction = np.sqrt(hln_factor)
    stat_hln = stat * correction

    # p-value (two-sided) based on standard normal
    pval = 2 * (1 - norm.cdf(abs(stat_hln)))

    return stat_hln, pval


def check_stationarity():
    print("\n" + "=" * 60)
    print(" STATIONARITY TESTS (ADF & KPSS with regression='c')")
    print("=" * 60)
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()

    targets = ['MG95', 'MG92', 'DO 0.05%', 'DO 0.001%']
    for t in targets:
        if t not in df.columns:
            print(f"\n--- {t}: COLUMN NOT FOUND, SKIPPING ---")
            continue
        series = df[t].dropna()
        # Log return
        log_ret = np.log(series / series.shift(1)).dropna()

        print(f"\n--- {t} (Log Returns, n={len(log_ret)}) ---")

        # ADF with constant only (econometrically appropriate for returns)
        adf_result = adfuller(log_ret, regression='c')
        print(f"ADF Statistic: {adf_result[0]:.4f}")
        print(f"p-value:       {adf_result[1]:.6f}")
        print(f"Lags used:     {adf_result[2]}")

        # KPSS with constant only (econometrically appropriate for returns)
        kpss_result = kpss(log_ret, regression='c', nlags='auto')
        print(f"KPSS Statistic: {kpss_result[0]:.4f}")
        print(f"p-value:        {kpss_result[1]:.4f}")

        # Conclusion
        adf_reject = adf_result[1] < 0.05
        kpss_reject = kpss_result[1] < 0.05
        if adf_reject and not kpss_reject:
            print("Conclusion: STATIONARY (ADF rejects unit root, KPSS does not reject stationarity)")
        elif not adf_reject and kpss_reject:
            print("Conclusion: NON-STATIONARY")
        elif adf_reject and kpss_reject:
            print("Conclusion: TREND-STATIONARY (conflicting — likely trend component)")
        else:
            print("Conclusion: INCONCLUSIVE")


def find_best_baseline_errors(results_dir, target, h, seed=42):
    """Find the baseline with lowest MAE for a given (target, h) cell."""
    best_mae = float('inf')
    best_model = None
    best_errors = None

    for model_name in BASELINES:
        # Try seed-specific path first
        err_path = os.path.join(results_dir, model_name,
                                f'{target}_H{h}_seed{seed}', 'errors.npy')
        res_path = os.path.join(results_dir, model_name,
                                f'{target}_H{h}_seed{seed}', 'results.json')
        if not os.path.exists(err_path):
            err_path = os.path.join(results_dir, model_name,
                                    f'{target}_H{h}', 'errors.npy')
            res_path = os.path.join(results_dir, model_name,
                                    f'{target}_H{h}', 'results.json')

        if os.path.exists(res_path) and os.path.exists(err_path):
            with open(res_path, 'r') as f:
                res = json.load(f)
            mae = res.get('metrics', {}).get('MAE', float('inf'))
            if mae < best_mae:
                best_mae = mae
                best_model = model_name
                best_errors = np.load(err_path)

    return best_model, best_errors


def run_dm_tests():
    print("\n" + "=" * 60)
    print(" DIEBOLD-MARIANO TEST (HAC & HLN 1997 Correction)")
    print(" With Holm-Bonferroni Multiple Testing Correction")
    print("=" * 60)
    print(" Comparison: GUMNet vs Best Baseline per (Target, Horizon) cell")
    print("-" * 60)

    from config import ALL_HORIZONS
    results_dir = os.path.join(RESULTS_DIR, 'walkforward')
    targets = ['XANG', 'DAU']
    horizons = ALL_HORIZONS

    # Collect all results first for Holm-Bonferroni correction
    all_results = []

    for target in targets:
        for h in horizons:
            # GUMNet errors
            gum_path = os.path.join(results_dir, 'GUMNet',
                                    f'{target}_H{h}_seed42', 'errors.npy')
            if not os.path.exists(gum_path):
                gum_path = os.path.join(results_dir, 'GUMNet',
                                        f'{target}_H{h}', 'errors.npy')

            if not os.path.exists(gum_path):
                continue

            err_gum = np.load(gum_path)

            # Find best baseline
            best_model, err_base = find_best_baseline_errors(results_dir, target, h)

            if err_base is None:
                continue

            # Reshape back to [N, output_dim] (output_dim = 2) to avoid cross-product autocorrelation
            output_dim = 2
            n_rows_gum = len(err_gum) // output_dim
            n_rows_base = len(err_base) // output_dim
            min_rows = min(n_rows_gum, n_rows_base)

            if min_rows > 0:
                err_gum_2d = err_gum[:min_rows * output_dim].reshape(min_rows, output_dim)
                err_base_2d = err_base[:min_rows * output_dim].reshape(min_rows, output_dim)

                # Compute mean squared error per timestep across products
                mse_gum = np.mean(err_gum_2d ** 2, axis=1)
                mse_base = np.mean(err_base_2d ** 2, axis=1)

                # Pass sqrt(mse) so that e1**2 - e2**2 in dm_test yields the correct loss differential
                e1_aligned = np.sqrt(mse_gum)
                e2_aligned = np.sqrt(mse_base)

                stat, pval = dm_test(e1_aligned, e2_aligned, h)
                all_results.append({
                    'target': target, 'horizon': h, 'best_model': best_model,
                    'dm_stat': stat, 'p_value': pval, 'n_obs': min_rows
                })

    # ── Holm-Bonferroni Multiple Testing Correction ──────────────────────
    # Holm (1979) step-down procedure: controls FWER without being as
    # conservative as standard Bonferroni.
    # Sort by ascending p-value, then adjust: p_adj[i] = p[i] * (m - i)
    # where m = total number of tests, i = rank (0-indexed)
    if all_results:
        m = len(all_results)
        sorted_idx = sorted(range(m), key=lambda i: all_results[i]['p_value'])
        p_adj = [0.0] * m

        running_max = 0.0
        for rank, idx in enumerate(sorted_idx):
            raw_p = all_results[idx]['p_value']
            adjusted = min(1.0, raw_p * (m - rank))
            running_max = max(running_max, adjusted)
            p_adj[idx] = running_max  # Enforce monotonicity

        for r in all_results:
            r['p_holm'] = p_adj[all_results.index(r)]

    # Print results
    for target in targets:
        print(f"\n>>> Target: {target}")
        target_results = [r for r in all_results if r['target'] == target]
        for r in target_results:
            h = r['horizon']
            stat = r['dm_stat']
            pval = r['p_value']
            p_holm = r['p_holm']
            best_model = r['best_model']
            sig_raw  = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else "ns"
            sig_holm = "***" if p_holm < 0.01 else "**" if p_holm < 0.05 else "*" if p_holm < 0.1 else "ns"
            print(f"  H{h:02d} (GUMNet vs {best_model:18s}): "
                  f"DM={stat:+.4f}, p={pval:.4f} {sig_raw:3s} | p_holm={p_holm:.4f} {sig_holm}")

        if not target_results:
            print(f"  No results found for {target}")

    print("\n  Note: p = raw DM p-value | p_holm = Holm-Bonferroni adjusted")
    print(f"  Total tests: {m if all_results else 0}, alpha=0.05 (unadjusted) / alpha=0.0025 (Bonferroni)")


if __name__ == '__main__':
    check_stationarity()
    run_dm_tests()

