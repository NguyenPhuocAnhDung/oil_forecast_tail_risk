import os
import glob
import json
import pandas as pd
import numpy as np

def main():
    root = 'results_v4/walkforward'
    seeds = [42, 123, 777, 2025, 9999]
    targets = ['XANG', 'DAU']
    # CHỈ CÁC KHUNG H ĐÃ ĐẠT 100% HOÀN THÀNH
    horizons = [1, 3, 5, 7, 10, 20, 60]

    records = []
    
    # Scan all models
    if os.path.exists(root):
        for model in os.listdir(root):
            model_path = os.path.join(root, model)
            if os.path.isdir(model_path):
                for h in horizons:
                    for seed in seeds:
                        for target in targets:
                            run_dir = f'{target}_H{h}_seed{seed}'
                            run_path = os.path.join(model_path, run_dir)
                            results_json = os.path.join(run_path, 'results.json')
                            if os.path.exists(results_json):
                                try:
                                    with open(results_json) as f:
                                        d = json.load(f)
                                        m_dict = d.get('metrics', {})
                                        
                                        # Hỗ trợ cả hai kiểu lưu 'crps' hoặc 'CRPS', 'mql' hoặc 'MQL'
                                        crps_val = m_dict.get('crps', m_dict.get('CRPS'))
                                        mql_val = m_dict.get('mql', m_dict.get('MQL'))
                                        
                                        records.append({
                                            'model': d.get('model', model),
                                            'target': d.get('target_type', target),
                                            'horizon': h,
                                            'seed': d.get('seed', seed),
                                            'MAE': m_dict.get('MAE'),
                                            'MSE': m_dict.get('MSE'),
                                            'RMSE': m_dict.get('RMSE'),
                                            'MAPE': m_dict.get('MAPE'),
                                            'SMAPE': m_dict.get('SMAPE'),
                                            'R2': m_dict.get('R2'),
                                            'CRPS': crps_val,
                                            'MQL': mql_val,
                                            'PICP': m_dict.get('PICP'),
                                            'PINAW': m_dict.get('PINAW')
                                        })
                                except Exception as e:
                                    pass

    df = pd.DataFrame(records)
    if len(df) == 0:
        print("No records found!")
        return

    # Generate tables
    md_content = "# Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts\n\n"
    md_content += "# BẢNG KẾT QUẢ THỰC NGHIỆM TRUNG BÌNH CỘNG 5 SEEDS (42, 123, 777, 2025, 9999)\n\n"
    md_content += f"**Trạng thái:** Báo cáo dành riêng cho các khung H đã hoàn tất 100% (H=3, H=5, H=7).\n"
    md_content += f"**Ngày tổng hợp:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} (Giờ hệ thống)\n\n"
    
    for h in horizons:
        md_content += f"# KẾT QUẢ KHUNG H{h}\n\n"
        for target in targets:
            df_t = df[(df['target'] == target) & (df['horizon'] == h)].copy()
            if len(df_t) == 0:
                continue
                
            # Group by model and compute mean
            df_avg = df_t.groupby('model')[['MAE', 'MSE', 'RMSE', 'MAPE', 'SMAPE', 'R2', 'CRPS', 'MQL', 'PICP', 'PINAW']].mean().reset_index()
            
            # Rank by CRPS (or MAE if CRPS is missing)
            sort_col = 'CRPS' if df_avg['CRPS'].notna().any() else 'MAE'
            df_avg = df_avg.sort_values(by=sort_col, ascending=True).reset_index(drop=True)
            
            # Determine best value in each column
            best_vals = {
                'MAE': df_avg['MAE'].min(),
                'MSE': df_avg['MSE'].min() if df_avg['MSE'].notna().any() else None,
                'RMSE': df_avg['RMSE'].min(),
                'MAPE': df_avg['MAPE'].min(),
                'SMAPE': df_avg['SMAPE'].min() if df_avg['SMAPE'].notna().any() else None,
                'R2': df_avg['R2'].max(),
                'CRPS': df_avg['CRPS'].min() if df_avg['CRPS'].notna().any() else None,
                'MQL': df_avg['MQL'].min() if df_avg['MQL'].notna().any() else None,
                'PICP': df_avg['PICP'].max() if df_avg['PICP'].notna().any() else None,
                'PINAW': df_avg['PINAW'].min() if df_avg['PINAW'].notna().any() else None,
            }
            
            # Convert to string and bold best values
            df_display = df_avg.copy()
            df_display.index += 1
            df_display.index.name = 'STT'
            
            for idx, row in df_avg.iterrows():
                model = row['model']
                
                # Format model name (bold GUMNet family)
                is_gumnet = 'GUMNet' in model
                model_fmt = f"**{model}**" if is_gumnet else model
                df_display.loc[idx+1, 'model'] = model_fmt
                
                for m in ['MAE', 'MSE', 'RMSE', 'SMAPE', 'R2', 'CRPS', 'MQL', 'PICP', 'PINAW']:
                    val = row[m]
                    if pd.isna(val):
                        df_display.loc[idx+1, m] = 'nan'
                        continue
                    
                    # Check if this is the best value
                    is_best = False
                    if m in ['R2', 'PICP']:
                        is_best = (val >= best_vals[m] - 1e-6)
                    else:
                        is_best = (val <= best_vals[m] + 1e-6)
                    
                    val_str = f"{val:.4f}"
                    if is_best:
                        df_display.loc[idx+1, m] = f"**{val_str}**"
                    else:
                        df_display.loc[idx+1, m] = val_str
                
                # Format MAPE separately (percentage)
                mape = row['MAPE']
                if pd.isna(mape):
                    df_display.loc[idx+1, 'MAPE'] = 'nan'
                else:
                    is_best = (mape <= best_vals['MAPE'] + 1e-6)
                    mape_str = f"{mape:.2f}%"
                    if is_best:
                        df_display.loc[idx+1, 'MAPE'] = f"**{mape_str}**"
                    else:
                        df_display.loc[idx+1, 'MAPE'] = mape_str

            # Rename columns for presentation
            df_display = df_display.rename(columns={
                'model': 'Mô hình (Model)',
                'MAE': 'MAE ↓',
                'MSE': 'MSE ↓',
                'RMSE': 'RMSE ↓',
                'MAPE': 'MAPE ↓',
                'SMAPE': 'SMAPE ↓',
                'R2': 'R² ↑',
                'CRPS': 'CRPS ↓',
                'MQL': 'MQL ↓',
                'PICP': 'PICP ↑',
                'PINAW': 'PINAW ↓'
            })
            
            title = f"⛽ XĂNG (GASOLINE) - KHUNG H{h}" if target == 'XANG' else f"🛢️ DẦU (DIESEL) - KHUNG H{h}"
            md_content += f"## 🏆 {title}\n\n"
            md_content += df_display.to_markdown() + "\n\n"
            
    # Write to target file
    output_path = 'results_v4/COMPLETE_ALL_HORIZONS_TABLES_5SEEDS_AVERAGE.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print(f"Successfully generated 5-seed average report for H3, H5, H7 at: {output_path}")

if __name__ == '__main__':
    main()
