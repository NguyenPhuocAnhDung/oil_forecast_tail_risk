import os
import json
import numpy as np

horizons = ['H1', 'H3', 'H5', 'H7', 'H10', 'H20']
seeds = [42, 123, 777, 9999, 2025]

# 27 SOTA Models chuẩn mực
sota_models = [
    'GUMNet', 'GUMNet_Wavelet', 'GUMNet_Fourier', 'GUMNet_iTrans', 'GUMNet_Mamba',
    'GUMNet_Patch', 'GUMNet_Diffusion', 'GUMNet_Graph', 'GUMNetHet', 'GUMNet_Adaptive',
    'GUMNet_Decomp', 'GUMNet_Fusion', 'GUMNet_RL', 'GUMNet_MoE_Sparse',
    'TimesFM', 'Chronos', 'Moirai', 'TTM',
    'PatchTST', 'RLinear', 'DLinear', 'LTSF_Linear',
    'iTransformer', 'TimesNet', 'TimeMixer', 'TFT', 'Autoformer'
]

# Phân nhóm mô hình chuẩn mực khoa học
def get_group(m):
    if 'GUMNet' in m:
        return 'GUMNet Family'
    elif m in ['TimesFM', 'Chronos', 'Moirai', 'TTM']:
        return 'Foundation Models'
    elif m in ['PatchTST', 'RLinear', 'DLinear', 'LTSF_Linear']:
        return 'Linear LTSF'
    elif m in ['iTransformer', 'TimesNet', 'TimeMixer', 'TFT', 'Autoformer']:
        return 'Advanced Transformers/DL'
    return 'Other'

out_md = '# 📊 BẢNG THỐNG KÊ HIỆU NĂNG 27 SOTA MODELS (5 SEEDS) — TỪ H1 ĐẾN H20 (XĂNG - MOGAS 95)\n\n'
out_md += '> **Quy chuẩn bản thảo chính thức**: *"Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts"*\n'
out_md += '> **Tập dữ liệu**: `XANG` (Mogas 95) | **Giao thức**: Expanding Window Walk-Forward (41 Folds) | **5 Seeds**: [42, 123, 777, 9999, 2025]\n'
out_md += '> **Bộ mô hình**: 27 SOTA Models chọn lọc (14 GUMNet Family + 4 Foundation Models + 4 Linear LTSF + 5 Advanced Transformers) — Đã loại bỏ 20 baseline yếu/thấp.\n'
out_md += '> **Quy ước in đậm**: Giá trị **tốt nhất** (Best) trên mỗi chỉ số của 27 mô hình được in đậm `**...**`.\n\n'

for h in horizons:
    h_days = {'H1': '1 ngày', 'H3': '3 ngày', 'H5': '5 ngày (1 tuần GD)', 'H7': '7 ngày', 'H10': '10 ngày (2 tuần GD)', 'H20': '20 ngày (1 tháng GD)'}[h]
    out_md += f'---\n\n## 📌 BẢNG 1.{horizons.index(h)+1}: HORIZON {h} ({h_days.upper()})\n\n'
    out_md += '| Hạng | Mô hình (Model) | Phân nhóm | MAE (Mean ± Std) | RMSE (Mean ± Std) | MAPE (%) (Mean ± Std) | $R^2$ (Mean ± Std) | CRPS (Mean ± Std) | DA (%) (Mean ± Std) |\n'
    out_md += '| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n'
    
    records = []
    for m in sota_models:
        metrics = {'MAE': [], 'RMSE': [], 'MAPE': [], 'R2': [], 'crps': [], 'DA': []}
        for s in seeds:
            p = f'results_v4/walkforward/{m}/XANG_{h}_seed{s}/results.json'
            if os.path.exists(p):
                with open(p) as f:
                    d = json.load(f)
                met = d.get('metrics', {})
                for k in metrics:
                    if k in met:
                        metrics[k].append(met[k])
        if len(metrics['MAE']) == 5:
            rec = {
                'model': m,
                'group': get_group(m),
                'mae_m': float(np.mean(metrics['MAE'])), 'mae_s': float(np.std(metrics['MAE'])),
                'rmse_m': float(np.mean(metrics['RMSE'])), 'rmse_s': float(np.std(metrics['RMSE'])),
                'mape_m': float(np.mean(metrics['MAPE'])), 'mape_s': float(np.std(metrics['MAPE'])),
                'r2_m': float(np.mean(metrics['R2'])), 'r2_s': float(np.std(metrics['R2'])),
                'crps_m': float(np.mean(metrics['crps'])), 'crps_s': float(np.std(metrics['crps'])),
                'da_m': float(np.mean(metrics['DA'])), 'da_s': float(np.std(metrics['DA'])),
            }
            records.append(rec)
    
    # Sort by MAE mean ascending
    records.sort(key=lambda x: x['mae_m'])
    
    # Find best values
    best_mae = min(r['mae_m'] for r in records)
    best_rmse = min(r['rmse_m'] for r in records)
    best_mape = min(r['mape_m'] for r in records)
    best_r2 = max(r['r2_m'] for r in records)
    best_crps = min(r['crps_m'] for r in records)
    best_da = max(r['da_m'] for r in records)
    
    for rank, r in enumerate(records, 1):
        mae_str = f"{r['mae_m']:.3f} ± {r['mae_s']:.3f}"
        if abs(r['mae_m'] - best_mae) < 1e-6: mae_str = f"**{mae_str}**"
        
        rmse_str = f"{r['rmse_m']:.3f} ± {r['rmse_s']:.3f}"
        if abs(r['rmse_m'] - best_rmse) < 1e-6: rmse_str = f"**{rmse_str}**"
        
        mape_str = f"{r['mape_m']:.2f}% ± {r['mape_s']:.2f}%"
        if abs(r['mape_m'] - best_mape) < 1e-6: mape_str = f"**{mape_str}**"
        
        r2_str = f"{r['r2_m']:.4f} ± {r['r2_s']:.4f}"
        if abs(r['r2_m'] - best_r2) < 1e-6: r2_str = f"**{r2_str}**"
        
        crps_str = f"{r['crps_m']:.3f} ± {r['crps_s']:.3f}"
        if abs(r['crps_m'] - best_crps) < 1e-6: crps_str = f"**{crps_str}**"
        
        da_str = f"{r['da_m']:.1f}% ± {r['da_s']:.1f}%"
        if abs(r['da_m'] - best_da) < 1e-6: da_str = f"**{da_str}**"
        
        model_name = f"**{r['model']}**" if 'GUMNet' in r['model'] or rank <= 3 else r['model']
        
        out_md += f"| {rank:2d} | {model_name:<26} | `{r['group']}` | {mae_str} | {rmse_str} | {mape_str} | {r2_str} | {crps_str} | {da_str} |\n"
    out_md += '\n'

os.makedirs('results_v4/reports', exist_ok=True)
with open('results_v4/reports/table_xang_h1_to_h20_5seeds.md', 'w', encoding='utf-8') as f:
    f.write(out_md)

print('SUCCESS')
