import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from collections import defaultdict
import numpy as np
import pandas as pd
from config import SOTA_TAXONOMY_REGISTRY, GUM_NET_VARIANTS, ALL_SOTA_BASELINES

SEEDS = [42, 123, 777, 2025, 9999]
HORIZONS = ['H1', 'H3', 'H5', 'H7']
TARGET = 'XANG'
TARGET_NAME = 'Xăng (Mogas 95)'

# Map models to paradigms
model_paradigm = {}
for p, models in SOTA_TAXONOMY_REGISTRY.items():
    for m in models:
        model_paradigm[m] = p
for m in GUM_NET_VARIANTS:
    model_paradigm[m] = 'P8_GUMNet_Ours'

def extract_xang_metrics():
    # data[horizon][model][metric] = list of values across seeds
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for h in HORIZONS:
        for s in SEEDS:
            for m in ALL_SOTA_BASELINES + GUM_NET_VARIANTS:
                paths = [
                    f'results_v4/walkforward/{m}/{TARGET}_{h}_seed{s}/results.json',
                    f'results_v4/walkforward/{m}/{TARGET}_{h}/results.json' if s == 42 else None
                ]
                for p in paths:
                    if p and os.path.exists(p):
                        try:
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
                        except Exception as e:
                            pass
    return data

def build_xang_summary_tables():
    data = extract_xang_metrics()
    
    rows = []
    for m in ALL_SOTA_BASELINES + GUM_NET_VARIANTS:
        p = model_paradigm.get(m, 'Other').replace('_', ' ')
        row = {'Model': m, 'Paradigm': p}
        
        for h in HORIZONS:
            h_data = data[h][m]
            n_seeds = len(h_data.get('MAE', []))
            row[f'{h}_Seeds'] = n_seeds
            
            for k in ['MAE', 'RMSE', 'MAPE', 'CRPS', 'DA', 'R2']:
                vals = h_data.get(k, [])
                row[f'{h}_{k}_mean'] = np.mean(vals) if vals else np.nan
                row[f'{h}_{k}_std'] = np.std(vals) if len(vals) > 1 else 0.0
                
        rows.append(row)
        
    df = pd.DataFrame(rows).sort_values('H1_MAE_mean')
    
    os.makedirs('results_v4/reports', exist_ok=True)
    csv_path = 'results_v4/reports/table_xang_5seeds_h1_to_h7.csv'
    df.to_csv(csv_path, index=False)
    
    # Generate H1 & H3 Table
    lines_h1_h3 = []
    lines_h1_h3.append(f'# ⛽ BẢNG THỐNG KÊ TOÀN DIỆN: XĂNG (MOGAS 95) — H1 & H3 (5 SEEDS MEAN ± STD)')
    lines_h1_h3.append('')
    lines_h1_h3.append('> **Mục tiêu**: `XANG` | **Tập mẫu**: 200 ngày Walk-Forward | **Seeds**: [42, 123, 777, 2025, 9999]')
    lines_h1_h3.append('')
    lines_h1_h3.append('| STT | Mô Hình (Model) | Phân Nhóm | H1: MAE (Mean ± Std) | H1: RMSE | H1: MAPE (%) | H1: CRPS | H1: DA (%) | H3: MAE (Mean ± Std) | H3: RMSE | H3: MAPE (%) | H3: CRPS | H3: DA (%) |')
    lines_h1_h3.append('| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |')
    
    for i, r in enumerate(df.to_dict('records'), 1):
        m_name = r['Model']
        p_name = r['Paradigm']
        
        h1_mae = f"{r['H1_MAE_mean']:.4f} ± {r['H1_MAE_std']:.4f}" if r['H1_Seeds'] > 1 else f"{r['H1_MAE_mean']:.4f}"
        h1_rmse = f"{r['H1_RMSE_mean']:.4f} ± {r['H1_RMSE_std']:.4f}" if r['H1_Seeds'] > 1 else f"{r['H1_RMSE_mean']:.4f}"
        h1_mape = f"{r['H1_MAPE_mean']:.3f}% ± {r['H1_MAPE_std']:.3f}%" if r['H1_Seeds'] > 1 else f"{r['H1_MAPE_mean']:.3f}%"
        h1_crps = f"{r['H1_CRPS_mean']:.4f}" if not np.isnan(r['H1_CRPS_mean']) else "N/A"
        h1_da = f"{r['H1_DA_mean']:.1f}%" if not np.isnan(r['H1_DA_mean']) else "N/A"
        
        h3_mae = f"{r['H3_MAE_mean']:.4f} ± {r['H3_MAE_std']:.4f}" if r['H3_Seeds'] > 1 else f"{r['H3_MAE_mean']:.4f}"
        h3_rmse = f"{r['H3_RMSE_mean']:.4f} ± {r['H3_RMSE_std']:.4f}" if r['H3_Seeds'] > 1 else f"{r['H3_RMSE_mean']:.4f}"
        h3_mape = f"{r['H3_MAPE_mean']:.3f}% ± {r['H3_MAPE_std']:.3f}%" if r['H3_Seeds'] > 1 else f"{r['H3_MAPE_mean']:.3f}%"
        h3_crps = f"{r['H3_CRPS_mean']:.4f}" if not np.isnan(r['H3_CRPS_mean']) else "N/A"
        h3_da = f"{r['H3_DA_mean']:.1f}%" if not np.isnan(r['H3_DA_mean']) else "N/A"
        
        lines_h1_h3.append(f'| {i:2d} | **{m_name}** | `{p_name}` | **{h1_mae}** | {h1_rmse} | {h1_mape} | {h1_crps} | {h1_da} | **{h3_mae}** | {h3_rmse} | {h3_mape} | {h3_crps} | {h3_da} |')

    # Generate H5 & H7 Table
    df_h5_sorted = df.sort_values('H5_MAE_mean')
    lines_h5_h7 = []
    lines_h5_h7.append(f'# ⛽ BẢNG THỐNG KÊ TOÀN DIỆN: XĂNG (MOGAS 95) — H5 & H7 (5 SEEDS MEAN ± STD)')
    lines_h5_h7.append('')
    lines_h5_h7.append('> **Mục tiêu**: `XANG` | **Tập mẫu**: 200 ngày Walk-Forward | **Seeds**: [42, 123, 777, 2025, 9999]')
    lines_h5_h7.append('')
    lines_h5_h7.append('| STT | Mô Hình (Model) | Phân Nhóm | H5: MAE (Mean ± Std) | H5: RMSE | H5: MAPE (%) | H5: CRPS | H5: DA (%) | H7: MAE (Mean ± Std) | H7: RMSE | H7: MAPE (%) | H7: CRPS | H7: DA (%) |')
    lines_h5_h7.append('| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |')
    
    for i, r in enumerate(df_h5_sorted.to_dict('records'), 1):
        m_name = r['Model']
        p_name = r['Paradigm']
        
        h5_mae = f"{r['H5_MAE_mean']:.4f} ± {r['H5_MAE_std']:.4f}" if r['H5_Seeds'] > 1 else f"{r['H5_MAE_mean']:.4f}"
        h5_rmse = f"{r['H5_RMSE_mean']:.4f} ± {r['H5_RMSE_std']:.4f}" if r['H5_Seeds'] > 1 else f"{r['H5_RMSE_mean']:.4f}"
        h5_mape = f"{r['H5_MAPE_mean']:.3f}% ± {r['H5_MAPE_std']:.3f}%" if r['H5_Seeds'] > 1 else f"{r['H5_MAPE_mean']:.3f}%"
        h5_crps = f"{r['H5_CRPS_mean']:.4f}" if not np.isnan(r['H5_CRPS_mean']) else "N/A"
        h5_da = f"{r['H5_DA_mean']:.1f}%" if not np.isnan(r['H5_DA_mean']) else "N/A"
        
        h7_mae = f"{r['H7_MAE_mean']:.4f} ± {r['H7_MAE_std']:.4f}" if r['H7_Seeds'] > 1 else f"{r['H7_MAE_mean']:.4f}"
        h7_rmse = f"{r['H7_RMSE_mean']:.4f} ± {r['H7_RMSE_std']:.4f}" if r['H7_Seeds'] > 1 else f"{r['H7_RMSE_mean']:.4f}"
        h7_mape = f"{r['H7_MAPE_mean']:.3f}% ± {r['H7_MAPE_std']:.3f}%" if r['H7_Seeds'] > 1 else f"{r['H7_MAPE_mean']:.3f}%"
        h7_crps = f"{r['H7_CRPS_mean']:.4f}" if not np.isnan(r['H7_CRPS_mean']) else "N/A"
        h7_da = f"{r['H7_DA_mean']:.1f}%" if not np.isnan(r['H7_DA_mean']) else "N/A"
        
        lines_h5_h7.append(f'| {i:2d} | **{m_name}** | `{p_name}` | **{h5_mae}** | {h5_rmse} | {h5_mape} | {h5_crps} | {h5_da} | **{h7_mae}** | {h7_rmse} | {h7_mape} | {h7_crps} | {h7_da} |')

    md_h1_h3_content = '\n'.join(lines_h1_h3)
    md_h5_h7_content = '\n'.join(lines_h5_h7)
    
    with open('results_v4/reports/table_xang_h1_h3_5seeds.md', 'w') as fp:
        fp.write(md_h1_h3_content)
    with open('results_v4/reports/table_xang_h5_h7_5seeds.md', 'w') as fp:
        fp.write(md_h5_h7_content)
        
    print("Successfully generated all XANG 5-seed tables!")
    return md_h1_h3_content, md_h5_h7_content

if __name__ == '__main__':
    build_xang_summary_tables()
