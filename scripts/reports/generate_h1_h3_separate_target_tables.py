import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from collections import defaultdict
import numpy as np
import pandas as pd
from config import SOTA_TAXONOMY_REGISTRY, GUM_NET_VARIANTS, ALL_SOTA_BASELINES

SEEDS = [42, 123, 777, 2025, 9999]
HORIZONS = ['H1', 'H3']

# Map models to paradigms
model_paradigm = {}
for p, models in SOTA_TAXONOMY_REGISTRY.items():
    for m in models:
        model_paradigm[m] = p
for m in GUM_NET_VARIANTS:
    model_paradigm[m] = 'P8_GUMNet_Ours'

def extract_metrics_for_target(target):
    # data[horizon][model][metric] = list of values across seeds
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for h in HORIZONS:
        for s in SEEDS:
            for m in ALL_SOTA_BASELINES + GUM_NET_VARIANTS:
                paths = [
                    f'results_v4/walkforward/{m}/{target}_{h}_seed{s}/results.json',
                    f'results_v4/walkforward/{m}/{target}_{h}/results.json' if s == 42 else None
                ]
                for p in paths:
                    if p and os.path.exists(p):
                        with open(p) as fp:
                            d = json.load(fp)
                        mets = d.get('metrics', {})
                        for k, v in mets.items():
                            norm_k = k.upper()
                            if norm_k in ['CRPS']:
                                data[h][m]['CRPS'].append(float(v))
                            elif norm_k in ['DIRECTIONAL_ACCURACY', 'DA']:
                                data[h][m]['DA'].append(float(v))
                            else:
                                try:
                                    data[h][m][norm_k].append(float(v))
                                except (ValueError, TypeError):
                                    pass
                        break
    return data

def build_target_table(target, target_name):
    data = extract_metrics_for_target(target)
    
    rows = []
    for m in ALL_SOTA_BASELINES + GUM_NET_VARIANTS:
        p = model_paradigm.get(m, 'Other').replace('_', ' ')
        row = {'Model': m, 'Paradigm': p}
        
        for h in HORIZONS:
            h_data = data[h][m]
            n_seeds = len(h_data.get('MAE', []))
            row[f'{h}_Seeds'] = n_seeds
            
            for k in ['MAE', 'RMSE', 'MAPE', 'CRPS', 'DA', 'R2', 'MASE', 'SMAPE']:
                vals = h_data.get(k, [])
                row[f'{h}_{k}_mean'] = np.mean(vals) if vals else np.nan
                row[f'{h}_{k}_std'] = np.std(vals) if len(vals) > 1 else 0.0
                
        rows.append(row)
        
    df = pd.DataFrame(rows).sort_values('H1_MAE_mean')
    
    # Save CSV
    os.makedirs('results_v4/reports', exist_ok=True)
    csv_path = f'results_v4/reports/table_{target.lower()}_h1_h3_5seeds.csv'
    df.to_csv(csv_path, index=False)
    
    # Format Markdown Table
    out_lines = []
    out_lines.append(f'# 🛢️ BẢNG THỐNG KÊ TOÀN DIỆN: {target_name.upper()} (H1 & H3 — 5 SEEDS)')
    out_lines.append('')
    out_lines.append(f'> **Mục tiêu**: `{target}` | **Tập mẫu**: 200 ngày Walk-Forward | **Chốt dữ liệu**: $\le$ 2026-04-30')
    out_lines.append('')
    out_lines.append('| STT | Mô Hình (Model) | Phân Nhóm | H1: MAE (Mean ± Std) | H1: RMSE | H1: MAPE (%) | H1: CRPS | H1: DA (%) | H3: MAE (Mean ± Std) | H3: RMSE | H3: MAPE (%) | H3: CRPS | H3: DA (%) |')
    out_lines.append('| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |')
    
    for i, r in enumerate(df.to_dict('records'), 1):
        m_name = r['Model']
        p_name = r['Paradigm']
        
        # H1 formatting
        h1_mae = f"{r['H1_MAE_mean']:.4f} ± {r['H1_MAE_std']:.4f}" if r['H1_Seeds'] > 1 else f"{r['H1_MAE_mean']:.4f}" if not np.isnan(r['H1_MAE_mean']) else "N/A"
        h1_rmse = f"{r['H1_RMSE_mean']:.4f} ± {r['H1_RMSE_std']:.4f}" if r['H1_Seeds'] > 1 else f"{r['H1_RMSE_mean']:.4f}" if not np.isnan(r['H1_RMSE_mean']) else "N/A"
        h1_mape = f"{r['H1_MAPE_mean']:.3f}% ± {r['H1_MAPE_std']:.3f}%" if r['H1_Seeds'] > 1 else f"{r['H1_MAPE_mean']:.3f}%" if not np.isnan(r['H1_MAPE_mean']) else "N/A"
        h1_crps = f"{r['H1_CRPS_mean']:.4f}" if not np.isnan(r['H1_CRPS_mean']) else "N/A"
        h1_da = f"{r['H1_DA_mean']:.1f}%" if not np.isnan(r['H1_DA_mean']) else "N/A"
        
        # H3 formatting
        h3_mae = f"{r['H3_MAE_mean']:.4f} ± {r['H3_MAE_std']:.4f}" if r['H3_Seeds'] > 1 else f"{r['H3_MAE_mean']:.4f}" if not np.isnan(r['H3_MAE_mean']) else "N/A"
        h3_rmse = f"{r['H3_RMSE_mean']:.4f} ± {r['H3_RMSE_std']:.4f}" if r['H3_Seeds'] > 1 else f"{r['H3_RMSE_mean']:.4f}" if not np.isnan(r['H3_RMSE_mean']) else "N/A"
        h3_mape = f"{r['H3_MAPE_mean']:.3f}% ± {r['H3_MAPE_std']:.3f}%" if r['H3_Seeds'] > 1 else f"{r['H3_MAPE_mean']:.3f}%" if not np.isnan(r['H3_MAPE_mean']) else "N/A"
        h3_crps = f"{r['H3_CRPS_mean']:.4f}" if not np.isnan(r['H3_CRPS_mean']) else "N/A"
        h3_da = f"{r['H3_DA_mean']:.1f}%" if not np.isnan(r['H3_DA_mean']) else "N/A"
        
        out_lines.append(f'| {i:2d} | **{m_name}** | `{p_name}` | **{h1_mae}** | {h1_rmse} | {h1_mape} | {h1_crps} | {h1_da} | **{h3_mae}** | {h3_rmse} | {h3_mape} | {h3_crps} | {h3_da} |')
        
    md_content = '\n'.join(out_lines)
    md_path = f'results_v4/reports/table_{target.lower()}_h1_h3_5seeds.md'
    with open(md_path, 'w') as fp:
        fp.write(md_content)
        
    print(f'Done generating table for {target_name}! Output saved to {md_path} and {csv_path}')
    return md_content

def generate_both_tables():
    xang_md = build_target_table('XANG', 'Xăng (Mogas 95)')
    dau_md = build_target_table('DAU', 'Dầu (Diesel DO)')
    return xang_md, dau_md

if __name__ == '__main__':
    generate_both_tables()
