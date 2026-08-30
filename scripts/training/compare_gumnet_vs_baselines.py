import glob, os, json, numpy as np

horizons = ['H1', 'H3', 'H5', 'H7', 'H10', 'H20']
seeds = [42, 123, 777, 9999, 2025]

sota_models = [
    'GUMNet', 'GUMNet_Wavelet', 'GUMNet_Fourier', 'GUMNet_iTrans', 'GUMNet_Mamba',
    'GUMNet_Patch', 'GUMNet_Diffusion', 'GUMNet_Graph', 'GUMNetHet', 'GUMNet_Adaptive',
    'GUMNet_Decomp', 'GUMNet_Fusion', 'GUMNet_RL', 'GUMNet_MoE_Sparse',
    'TimesFM', 'Chronos', 'Moirai', 'TTM',
    'PatchTST', 'RLinear', 'DLinear', 'LTSF_Linear',
    'iTransformer', 'TimesNet', 'TimeMixer', 'TFT', 'Autoformer'
]

gumnet_models = [m for m in sota_models if 'GUMNet' in m]
baseline_models = [m for m in sota_models if 'GUMNet' not in m]

# Data structures
horizon_data = {}
for h in horizons:
    horizon_data[h] = {}
    for m in sota_models:
        mae_list, rmse_list, mape_list, r2_list, crps_list, da_list = [], [], [], [], [], []
        for s in seeds:
            p = f'results_v4/walkforward/{m}/XANG_{h}_seed{s}/results.json'
            with open(p) as f:
                d = json.load(f)
            met = d.get('metrics', {})
            mae_list.append(met.get('MAE', 0))
            rmse_list.append(met.get('RMSE', 0))
            mape_list.append(met.get('MAPE', 0))
            r2_list.append(met.get('R2', 0))
            crps_val = met.get('crps', met.get('CRPS', met.get('MAE', 0)))
            crps_list.append(crps_val)
            da_list.append(met.get('DA', 0))
        horizon_data[h][m] = {
            'MAE': np.mean(mae_list), 'RMSE': np.mean(rmse_list),
            'MAPE': np.mean(mape_list), 'R2': np.mean(r2_list),
            'CRPS': np.mean(crps_list), 'DA': np.mean(da_list)
        }

# Evaluate GUMNet overall rank and averages
summary = []
for g in gumnet_models:
    ranks_mae = []
    ranks_crps = []
    avg_mae = np.mean([horizon_data[h][g]['MAE'] for h in horizons])
    avg_rmse = np.mean([horizon_data[h][g]['RMSE'] for h in horizons])
    avg_mape = np.mean([horizon_data[h][g]['MAPE'] for h in horizons])
    avg_r2 = np.mean([horizon_data[h][g]['R2'] for h in horizons])
    avg_crps = np.mean([horizon_data[h][g]['CRPS'] for h in horizons])
    avg_da = np.mean([horizon_data[h][g]['DA'] for h in horizons])
    
    for h in horizons:
        # Rank among all 27 SOTA models by MAE
        sorted_m = sorted(sota_models, key=lambda m: horizon_data[h][m]['MAE'])
        ranks_mae.append(sorted_m.index(g) + 1)
        sorted_crps = sorted(sota_models, key=lambda m: horizon_data[h][m]['CRPS'])
        ranks_crps.append(sorted_crps.index(g) + 1)
        
    summary.append({
        'model': g,
        'mean_rank_mae': np.mean(ranks_mae),
        'mean_rank_crps': np.mean(ranks_crps),
        'avg_mae': avg_mae,
        'avg_rmse': avg_rmse,
        'avg_mape': avg_mape,
        'avg_r2': avg_r2,
        'avg_crps': avg_crps,
        'avg_da': avg_da,
        'ranks_mae': ranks_mae
    })

# Also compute baseline averages
b_summary = []
for b in baseline_models:
    avg_mae = np.mean([horizon_data[h][b]['MAE'] for h in horizons])
    avg_rmse = np.mean([horizon_data[h][b]['RMSE'] for h in horizons])
    avg_mape = np.mean([horizon_data[h][b]['MAPE'] for h in horizons])
    avg_r2 = np.mean([horizon_data[h][b]['R2'] for h in horizons])
    avg_crps = np.mean([horizon_data[h][b]['CRPS'] for h in horizons])
    avg_da = np.mean([horizon_data[h][b]['DA'] for h in horizons])
    ranks_mae = [sorted(sota_models, key=lambda m: horizon_data[h][m]['MAE']).index(b) + 1 for h in horizons]
    b_summary.append({
        'model': b,
        'avg_mae': avg_mae, 'avg_rmse': avg_rmse, 'avg_mape': avg_mape,
        'avg_r2': avg_r2, 'avg_crps': avg_crps, 'avg_da': avg_da,
        'mean_rank_mae': np.mean(ranks_mae),
        'ranks_mae': ranks_mae
    })

summary.sort(key=lambda x: x['avg_mae'])
b_summary.sort(key=lambda x: x['avg_mae'])

print('=== 1. TOP GUMNET MODELS (AVG ACROSS ALL 6 HORIZONS H1..H20) ===')
for rank, r in enumerate(summary, 1):
    print(f"{rank:2d}. {r['model']:<22}: Avg MAE={r['avg_mae']:.3f} | Avg CRPS={r['avg_crps']:.3f} | Avg RMSE={r['avg_rmse']:.3f} | Avg R2={r['avg_r2']:.4f} | Ranks={r['ranks_mae']}")

print('\n=== 2. TOP BASELINE MODELS (AVG ACROSS ALL 6 HORIZONS H1..H20) ===')
for rank, r in enumerate(b_summary, 1):
    print(f"{rank:2d}. {r['model']:<22}: Avg MAE={r['avg_mae']:.3f} | Avg CRPS={r['avg_crps']:.3f} | Avg RMSE={r['avg_rmse']:.3f} | Avg R2={r['avg_r2']:.4f} | Ranks={r['ranks_mae']}")

# Top 1 & Top 2 GUMNet head-to-head comparison per horizon
top1_gumnet = summary[0]['model']
top2_gumnet = summary[1]['model']

print(f'\n=== 3. HEAD-TO-HEAD PER HORIZON: TOP 1 ({top1_gumnet}) & TOP 2 ({top2_gumnet}) VS BEST BASELINES ===')
print(f'Horizon | Best Baseline (MAE) | {top1_gumnet} (MAE) | {top2_gumnet} (MAE) | Winner MAE | Winner CRPS')
for h in horizons:
    best_b = min(baseline_models, key=lambda b: horizon_data[h][b]['MAE'])
    b_mae = horizon_data[h][best_b]['MAE']
    t1_mae = horizon_data[h][top1_gumnet]['MAE']
    t2_mae = horizon_data[h][top2_gumnet]['MAE']
    
    best_all = min(sota_models, key=lambda m: horizon_data[h][m]['MAE'])
    best_crps = min(sota_models, key=lambda m: horizon_data[h][m]['CRPS'])
    
    print(f'{h:<7} | {best_b:<12} ({b_mae:.3f}) | {t1_mae:.3f} | {t2_mae:.3f} | {best_all} | {best_crps}')
