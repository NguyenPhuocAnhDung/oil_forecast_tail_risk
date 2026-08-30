import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from collections import defaultdict
import numpy as np
import pandas as pd
from config import SOTA_TAXONOMY_REGISTRY, GUM_NET_VARIANTS, ALL_SOTA_BASELINES

seeds = [42, 123, 777, 2025, 9999]

# Map models to paradigms
model_paradigm = {}
for p, models in SOTA_TAXONOMY_REGISTRY.items():
    for m in models:
        model_paradigm[m] = p
for m in GUM_NET_VARIANTS:
    model_paradigm[m] = 'P8_GUMNet_Ours'

def extract_target_data(target):
    data = defaultdict(lambda: defaultdict(list))
    for s in seeds:
        for m in ALL_SOTA_BASELINES + GUM_NET_VARIANTS:
            paths = [
                f'results_v4/walkforward/{m}/{target}_H1_seed{s}/results.json',
                f'results_v4/walkforward/{m}/{target}_H1/results.json' if s == 42 else None
            ]
            for p in paths:
                if p and os.path.exists(p):
                    with open(p) as fp:
                        d = json.load(fp)
                    mets = d.get('metrics', {})
                    for k in ['MAE', 'RMSE', 'MAPE', 'CRPS', 'Directional_Accuracy', 'DA']:
                        v = mets.get(k)
                        if v is not None:
                            norm_k = 'DA' if k in ['Directional_Accuracy', 'DA'] else k
                            data[m][norm_k].append(float(v))
                    break
    return data

xang = extract_target_data('XANG')
dau = extract_target_data('DAU')

rows = []
for m in ALL_SOTA_BASELINES + GUM_NET_VARIANTS:
    p = model_paradigm.get(m, 'Other')
    x_mae = xang[m]['MAE']
    x_rmse = xang[m]['RMSE']
    x_mape = xang[m]['MAPE']
    
    d_mae = dau[m]['MAE']
    d_rmse = dau[m]['RMSE']
    d_mape = dau[m]['MAPE']
    
    x_mae_str = f'{np.mean(x_mae):.4f} ± {np.std(x_mae):.4f}' if len(x_mae) > 1 else f'{np.mean(x_mae):.4f}'
    x_rmse_str = f'{np.mean(x_rmse):.4f} ± {np.std(x_rmse):.4f}' if len(x_rmse) > 1 else f'{np.mean(x_rmse):.4f}'
    x_mape_str = f'{np.mean(x_mape):.4f}% ± {np.std(x_mape):.4f}%' if len(x_mape) > 1 else f'{np.mean(x_mape):.4f}%'
    
    d_mae_str = f'{np.mean(d_mae):.4f} ± {np.std(d_mae):.4f}' if len(d_mae) > 1 else f'{np.mean(d_mae):.4f}'
    d_rmse_str = f'{np.mean(d_rmse):.4f} ± {np.std(d_rmse):.4f}' if len(d_rmse) > 1 else f'{np.mean(d_rmse):.4f}'
    d_mape_str = f'{np.mean(d_mape):.4f}% ± {np.std(d_mape):.4f}%' if len(d_mape) > 1 else f'{np.mean(d_mape):.4f}%'
    
    rows.append({
        'Paradigm': p.replace('_', ' '),
        'Model': m,
        'XANG_MAE_mean': np.mean(x_mae) if x_mae else 999.0,
        'XANG_MAE': x_mae_str,
        'XANG_RMSE': x_rmse_str,
        'XANG_MAPE': x_mape_str,
        'XANG_Seeds': len(x_mae),
        'DAU_MAE': d_mae_str,
        'DAU_RMSE': d_rmse_str,
        'DAU_MAPE': d_mape_str,
        'DAU_Seeds': len(d_mae),
    })

df = pd.DataFrame(rows).sort_values('XANG_MAE_mean')

out_lines = []
out_lines.append('| STT | Mô Hình (Model) | Phân Nhóm (Paradigm) | XĂNG: MAE (Mean ± Std) | XĂNG: RMSE (Mean ± Std) | XĂNG: MAPE (%) | DẦU: MAE (Seed 42) | DẦU: RMSE (Seed 42) | DẦU: MAPE (%) |')
out_lines.append('| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |')
for i, r in enumerate(df.to_dict('records'), 1):
    m_name = r['Model']
    p_name = r['Paradigm']
    x_mae_val = r['XANG_MAE']
    x_rmse_val = r['XANG_RMSE']
    x_mape_val = r['XANG_MAPE']
    d_mae_val = r['DAU_MAE']
    d_rmse_val = r['DAU_RMSE']
    d_mape_val = r['DAU_MAPE']
    out_lines.append(f'| {i:2d} | **{m_name}** | `{p_name}` | **{x_mae_val}** | {x_rmse_val} | {x_mape_val} | **{d_mae_val}** | {d_rmse_val} | {d_mape_val} |')

output_text = '\n'.join(out_lines)
print(output_text)

with open('results_v4/summary_h1_5seeds_xang_dau.md', 'w') as fp:
    fp.write(output_text)
