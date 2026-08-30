import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from collections import defaultdict
import numpy as np
import pandas as pd
from config import SOTA_TAXONOMY_REGISTRY, GUM_NET_VARIANTS, ALL_SOTA_BASELINES

SEEDS = [42, 123, 777, 2025, 9999]
HORIZON = 'H1'

# Map models to paradigms
model_paradigm = {}
for p, models in SOTA_TAXONOMY_REGISTRY.items():
    for m in models:
        model_paradigm[m] = p
for m in GUM_NET_VARIANTS:
    model_paradigm[m] = 'P8_GUMNet_Ours'

def extract_target_data(target, horizon=HORIZON):
    data = defaultdict(lambda: defaultdict(list))
    for s in SEEDS:
        for m in ALL_SOTA_BASELINES + GUM_NET_VARIANTS:
            paths = [
                f'results_v4/walkforward/{m}/{target}_{horizon}_seed{s}/results.json',
                f'results_v4/walkforward/{m}/{target}_{horizon}/results.json' if s == 42 else None
            ]
            for p in paths:
                if p and os.path.exists(p):
                    with open(p) as fp:
                        d = json.load(fp)
                    mets = d.get('metrics', {})
                    for k, v in mets.items():
                        norm_k = k.upper()
                        if norm_k in ['CRPS']:
                            data[m]['CRPS'].append(float(v))
                        elif norm_k in ['DIRECTIONAL_ACCURACY', 'DA']:
                            data[m]['DA'].append(float(v))
                        else:
                            try:
                                data[m][norm_k].append(float(v))
                            except (ValueError, TypeError):
                                pass
                    break
    return data

def generate_h1_report():
    xang = extract_target_data('XANG', HORIZON)
    dau = extract_target_data('DAU', HORIZON)
    
    rows = []
    for m in ALL_SOTA_BASELINES + GUM_NET_VARIANTS:
        p = model_paradigm.get(m, 'Other').replace('_', ' ')
        xm = xang[m]
        dm = dau[m]
        
        row = {
            'Model': m,
            'Paradigm': p,
            'XANG_Seeds': len(xm.get('MAE', [])),
            'DAU_Seeds': len(dm.get('MAE', [])),
        }
        
        for k in ['MAE', 'RMSE', 'MAPE', 'CRPS', 'DA', 'R2', 'MASE', 'SMAPE']:
            x_vals = xm.get(k, [])
            d_vals = dm.get(k, [])
            
            row[f'XANG_{k}_mean'] = np.mean(x_vals) if x_vals else np.nan
            row[f'XANG_{k}_std'] = np.std(x_vals) if len(x_vals) > 1 else 0.0
            
            row[f'DAU_{k}_mean'] = np.mean(d_vals) if d_vals else np.nan
            row[f'DAU_{k}_std'] = np.std(d_vals) if len(d_vals) > 1 else 0.0
        
        rows.append(row)
    
    df = pd.DataFrame(rows).sort_values('XANG_MAE_mean')
    
    # Save CSV
    os.makedirs('results_v4/reports', exist_ok=True)
    df.to_csv(f'results_v4/reports/summary_{HORIZON}_5seeds_all_metrics.csv', index=False)
    
    # Generate Markdown Table
    out_lines = []
    out_lines.append(f'# BẢNG THỐNG KÊ TOÀN DIỆN KHUNG DỰ BÁO {HORIZON} (5 SEEDS - XĂNG & DẦU)')
    out_lines.append('')
    out_lines.append('> Ghi chú:')
    out_lines.append('> - **XĂNG (H1)**: Đã hoàn tất 100% trên cả 5 Seeds (`42`, `123`, `777`, `2025`, `9999`) -> Thống kê Mean ± Std.')
    out_lines.append('> - **DẦU (H1)**: Đã hoàn tất Seed `42`, các seed còn lại (`123`, `777`, `2025`, `9999`) đang xếp hàng trong pipeline và sẽ tự động cập nhật Mean ± Std ngay khi hoàn thành.')
    out_lines.append('')
    out_lines.append('| STT | Mô Hình (Model) | Phân Nhóm | XĂNG: MAE (Mean ± Std) | XĂNG: RMSE (Mean ± Std) | XĂNG: MAPE (%) | XĂNG: CRPS | XĂNG: DA (%) | DẦU: MAE (Seed 42) | DẦU: RMSE | DẦU: MAPE (%) | DẦU: CRPS |')
    out_lines.append('| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |')
    
    for i, r in enumerate(df.to_dict('records'), 1):
        m_name = r['Model']
        p_name = r['Paradigm']
        
        x_mae = f"{r['XANG_MAE_mean']:.4f} ± {r['XANG_MAE_std']:.4f}" if r['XANG_Seeds'] > 1 else f"{r['XANG_MAE_mean']:.4f}"
        x_rmse = f"{r['XANG_RMSE_mean']:.4f} ± {r['XANG_RMSE_std']:.4f}" if r['XANG_Seeds'] > 1 else f"{r['XANG_RMSE_mean']:.4f}"
        x_mape = f"{r['XANG_MAPE_mean']:.3f}% ± {r['XANG_MAPE_std']:.3f}%" if r['XANG_Seeds'] > 1 else f"{r['XANG_MAPE_mean']:.3f}%"
        x_crps = f"{r['XANG_CRPS_mean']:.4f}" if not np.isnan(r['XANG_CRPS_mean']) else "N/A"
        x_da = f"{r['XANG_DA_mean']:.1f}%" if not np.isnan(r['XANG_DA_mean']) else "N/A"
        
        d_mae = f"{r['DAU_MAE_mean']:.4f} ± {r['DAU_MAE_std']:.4f}" if r['DAU_Seeds'] > 1 else f"{r['DAU_MAE_mean']:.4f}"
        d_rmse = f"{r['DAU_RMSE_mean']:.4f}" if not np.isnan(r['DAU_RMSE_mean']) else "N/A"
        d_mape = f"{r['DAU_MAPE_mean']:.3f}%" if not np.isnan(r['DAU_MAPE_mean']) else "N/A"
        d_crps = f"{r['DAU_CRPS_mean']:.4f}" if not np.isnan(r['DAU_CRPS_mean']) else "N/A"
        
        out_lines.append(f'| {i:2d} | **{m_name}** | `{p_name}` | **{x_mae}** | {x_rmse} | {x_mape} | {x_crps} | {x_da} | **{d_mae}** | {d_rmse} | {d_mape} | {d_crps} |')
    
    md_content = '\n'.join(out_lines)
    with open(f'results_v4/reports/summary_{HORIZON}_5seeds_all_metrics.md', 'w') as fp:
        fp.write(md_content)
    
    print(f'Done generating summary for {HORIZON}! Output saved to results_v4/reports/summary_{HORIZON}_5seeds_all_metrics.md')
    return md_content

if __name__ == '__main__':
    generate_h1_report()
