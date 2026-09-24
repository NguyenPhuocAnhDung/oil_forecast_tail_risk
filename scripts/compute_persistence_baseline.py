"""
Compute Naïve Persistence (No-Change) Baseline for all horizons.
Persistence: P̂_{t+h} = P_t (last known price at forecast origin)

Run: python3 scripts/compute_persistence_baseline.py
"""
import pandas as pd
import numpy as np
import glob
import json
import os

HORIZONS = [1, 3, 5, 7, 10, 20, 60]
SEED = 42

# ---------------------------------------------------------------------------
# 1. Build full actual price series from all available predictions
# ---------------------------------------------------------------------------
def build_price_lookup(target, product_filter=None):
    dfs = []
    for f in glob.glob(f'results_v4/walkforward/GUMNetHet/{target}_H*_seed*/'
                        'predictions.csv'):
        df = pd.read_csv(f, parse_dates=['date'])
        if product_filter:
            df = df[df['product'] == product_filter]
        dfs.append(df[['date', 'true']])

    price_df = (pd.concat(dfs)
                  .drop_duplicates('date')
                  .sort_values('date')
                  .reset_index(drop=True))
    return price_df.set_index('date')['true']


# ---------------------------------------------------------------------------
# 2. For each horizon, look up origin price h trading days back
# ---------------------------------------------------------------------------
def compute_persistence_metrics(target, horizon, price_series, seed=42,
                                 product_filter=None):
    pred_file = (f'results_v4/walkforward/GUMNetHet/'
                 f'{target}_H{horizon}_seed{seed}/predictions.csv')
    df = pd.read_csv(pred_file, parse_dates=['date'])

    if product_filter:
        df = df[df['product'] == product_filter]

    df = (df.drop_duplicates('date')
            .sort_values('date')
            .reset_index(drop=True))

    sorted_dates = price_series.index.sort_values()
    date_arr = sorted_dates.to_numpy()          # numpy datetime64
    price_arr = price_series.loc[sorted_dates].values

    origins = []
    for d in df['date']:
        pos = np.searchsorted(date_arr, np.datetime64(d))  # position of d
        origin_pos = pos - horizon                          # h steps back
        if origin_pos >= 0:
            origins.append(float(price_arr[origin_pos]))
        else:
            origins.append(np.nan)

    df['persistence'] = origins
    valid = df.dropna(subset=['persistence'])

    actual = valid['true'].values
    pers   = valid['persistence'].values

    mae  = float(np.mean(np.abs(actual - pers)))
    rmse = float(np.sqrt(np.mean((actual - pers) ** 2)))
    mape = float(np.mean(np.abs((actual - pers) / actual)) * 100)
    ss_res = float(np.sum((actual - pers) ** 2))
    ss_tot = float(np.sum((actual - np.mean(actual)) ** 2))
    r2   = float(1 - ss_res / ss_tot) if ss_tot > 0 else np.nan

    # DA: sign of change from origin price
    # Persistence predicts ZERO change => DA = % times market also stayed flat
    # i.e. sgn(0) vs sgn(true - origin); persistence always guesses 0
    # Convention: sgn(0) == sgn(0) counts as correct only if actual also flat
    actual_delta = actual - pers  # actual change over h days
    # Persistence says delta = 0 => always wrong when market moves
    # Use 0-threshold: correct if (pred_delta >= 0) == (actual_delta >= 0)
    pred_delta = np.zeros_like(actual_delta)   # persistence = no change
    da = float(np.mean(np.sign(pred_delta) == np.sign(actual_delta)) * 100)

    return {
        'MAE': round(mae, 4),
        'RMSE': round(rmse, 4),
        'MAPE': round(mape, 4),
        'R2': round(r2, 4),
        'DA': round(da, 2),
        'N': int(len(valid)),
    }


# ---------------------------------------------------------------------------
# 3. Main
# ---------------------------------------------------------------------------
results = {}

for target, product_filter, label in [
    ('XANG', 'MG95', 'MG95 (XANG)'),
    ('DAU',  None,   'DO (DAU)'),
]:
    print(f'\n=== Persistence Baseline: {label} ===')
    price_series = build_price_lookup(target, product_filter)
    print(f'  Price series: {price_series.index.min()} to {price_series.index.max()}'
          f'  N={len(price_series)}')

    results[target] = {}
    for h in HORIZONS:
        try:
            m = compute_persistence_metrics(
                target, h, price_series, seed=SEED,
                product_filter=product_filter)
            results[target][h] = m
            print(f'  H{h:2d}: MAE={m["MAE"]:.4f}  RMSE={m["RMSE"]:.4f}'
                  f'  MAPE={m["MAPE"]:.2f}%  R²={m["R2"]:.4f}'
                  f'  DA={m["DA"]:.2f}%  (N={m["N"]})')
        except Exception as e:
            print(f'  H{h}: ERROR — {e}')

# ---------------------------------------------------------------------------
# 4. Save results
# ---------------------------------------------------------------------------
out_path = 'results_v4/persistence_baseline_metrics.json'
with open(out_path, 'w') as fp:
    json.dump(results, fp, indent=2)
print(f'\nSaved to {out_path}')

# ---------------------------------------------------------------------------
# 5. Also compare with GUMNetHet at H60 (most critical)
# ---------------------------------------------------------------------------
print('\n=== CRITICAL: GUMNetHet vs Persistence at H60 ===')
df_m = pd.read_csv('seed42_metrics.csv')
for target, label in [('XANG', 'MG95'), ('DAU', 'DO')]:
    gum = df_m[(df_m['model'] == 'GUMNetHet') & (df_m['target'] == target)
               & (df_m['horizon'] == 60)].iloc[0]
    pers = results[target][60]
    print(f'\n{label} H60:')
    print(f'  Persistence  MAE={pers["MAE"]:.4f}  RMSE={pers["RMSE"]:.4f}  R²={pers["R2"]:.4f}')
    print(f'  GUMNetHet    MAE={gum["MAE"]:.4f}  RMSE={gum["RMSE"]:.4f}  R²={gum["R2"]:.4f}')
    print(f'  GUMNetHet beats persistence?'
          f'  MAE: {gum["MAE"] < pers["MAE"]}  RMSE: {gum["RMSE"] < pers["RMSE"]}')
