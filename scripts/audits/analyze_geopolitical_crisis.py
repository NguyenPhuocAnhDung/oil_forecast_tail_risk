import os
import sys
import json
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config import ALL_HORIZONS, SEEDS, TARGETS

df_raw = pd.read_csv('data/processed/clean_data_exo.csv')
df_raw.columns = df_raw.columns.str.strip()
df_raw['Ngày'] = pd.to_datetime(df_raw['Ngày'])

def align_predictions_with_dates(pred_df, target_type, horizon):
    """
    Align predictions with dates.
    If date column is missing, reconstruct it based on matching true values in df_raw.
    """
    target_cols = TARGETS[target_type]
    n_cols = len(target_cols)
    
    if 'date' in pred_df.columns and 'product' in pred_df.columns:
        pred_df['date'] = pd.to_datetime(pred_df['date'])
        return pred_df
        
    # Reconstruct dates
    n_steps = len(pred_df) // n_cols
    true_vals = pred_df['true'].values.reshape(n_steps, n_cols)
    pred_vals = pred_df['pred'].values.reshape(n_steps, n_cols)
    
    # Search for start index of first window in df_raw
    raw_vals = df_raw[target_cols].values
    n_raw = len(raw_vals)
    first_window = true_vals[:horizon]
    
    # Vectorized match search for first row to speed up search by 1000x
    first_row = first_window[0]
    matches = np.where(np.all(np.abs(raw_vals - first_row) < 1e-1, axis=1))[0]
    
    found_start = -1
    for idx in matches:
        if idx + horizon <= n_raw:
            slice_vals = raw_vals[idx:idx + horizon]
            if np.allclose(slice_vals, first_window, atol=1e-1):
                found_start = idx
                break
            
    if found_start == -1:
        return None
        
    # Find step_size
    step_size = horizon
    if n_steps >= 2 * horizon:
        second_window = true_vals[horizon:2*horizon]
        second_row = second_window[0]
        matches_2 = np.where(np.all(np.abs(raw_vals - second_row) < 1e-1, axis=1))[0]
        
        for idx in matches_2:
            if idx + horizon <= n_raw:
                slice_vals = raw_vals[idx:idx + horizon]
                if np.allclose(slice_vals, second_window, atol=1e-1):
                    step_size = idx - found_start
                    break
                
    # Build date and product lists
    all_dates = []
    all_products = []
    
    n_windows = n_steps // horizon
    for w in range(n_windows):
        start_idx = found_start + w * step_size
        dates = df_raw['Ngày'].iloc[start_idx : start_idx + horizon].dt.strftime('%Y-%m-%d').tolist()
        
        if not dates:
            last_date_str = df_raw['Ngày'].iloc[-1].strftime('%Y-%m-%d')
            dates = [last_date_str] * horizon
        elif len(dates) < horizon:
            dates += [dates[-1]] * (horizon - len(dates))
            
        for d in dates:
            for p in target_cols:
                all_dates.append(d)
                all_products.append(p)
                
    # Handle remainder if any
    remainder = len(pred_df) - len(all_dates)
    if remainder > 0:
        all_dates += [all_dates[-1]] * remainder
        all_products += [all_products[-1]] * remainder
        
    aligned_df = pd.DataFrame({
        'date': pd.to_datetime(all_dates),
        'product': all_products,
        'true': pred_df['true'].values,
        'pred': pred_df['pred'].values
    })
    
    return aligned_df

def calculate_da_subset(subset_df, target_type):
    """Calculate Directional Accuracy on a subset DataFrame."""
    target_cols = TARGETS[target_type]
    n_cols = len(target_cols)
    
    # Group by date and pivot to [steps, target_cols]
    pivot_true = subset_df.pivot_table(index='date', columns='product', values='true')
    pivot_pred = subset_df.pivot_table(index='date', columns='product', values='pred')
    
    # Ensure column order matches target_cols
    pivot_true = pivot_true.reindex(columns=target_cols).dropna()
    pivot_pred = pivot_pred.reindex(columns=target_cols).dropna()
    
    if len(pivot_true) <= 1:
        return None
        
    y_true = pivot_true.values
    y_pred = pivot_pred.values
    
    true_direction = np.sign(np.diff(y_true, axis=0))
    pred_direction = np.sign(np.diff(y_pred, axis=0))
    
    da = np.mean(true_direction == pred_direction) * 100
    return da

# Define crisis windows
CRISIS_WINDOWS = {
    'May 2018 JCPOA (Iran nuclear deal withdrawal)': ('2018-05-01', '2018-06-30'),
    'May 2024 Iran President Helicopter Crash': ('2024-05-01', '2024-06-30')
}

MODELS = ['GUMNet', 'LSTM', 'GRU', 'BiLSTM_Attention', 'XGBoost', 'PatchTST', 'DLinear', 'TimesNet', 'iTransformer', 'TimeMixer', 'TFT', 'NHits']
TARGET_TYPES = ['XANG', 'DAU']

def main():
    print("Analyzing Geopolitical Crisis Windows...")
    results_wf = os.path.join('results_v4', 'walkforward')
    
    crisis_results = {}
    
    for window_name, (start_d, end_d) in CRISIS_WINDOWS.items():
        print(f"\nEvaluating crisis window: {window_name} ({start_d} to {end_d})")
        crisis_results[window_name] = {}
        
        for tt in TARGET_TYPES:
            crisis_results[window_name][tt] = {}
            for h in ALL_HORIZONS:
                crisis_results[window_name][tt][h] = {}
                
                for model in MODELS:
                    model_da_list = []
                    
                    for seed in SEEDS:
                        pred_file = os.path.join(results_wf, model, f'{tt}_H{h}_seed{seed}', 'predictions.csv')
                        if not os.path.exists(pred_file):
                            continue
                            
                        pred_df = pd.read_csv(pred_file)
                        aligned_df = align_predictions_with_dates(pred_df, tt, h)
                        
                        if aligned_df is None:
                            continue
                            
                        # Filter by date range
                        mask = (aligned_df['date'] >= start_d) & (aligned_df['date'] <= end_d)
                        subset = aligned_df[mask]
                        
                        if len(subset) > 0:
                            da = calculate_da_subset(subset, tt)
                            if da is not None:
                                model_da_list.append(da)
                            
                    if model_da_list:
                        crisis_results[window_name][tt][h][model] = {
                            'mean': np.mean(model_da_list),
                            'std': np.std(model_da_list, ddof=1) if len(model_da_list) > 1 else 0.0,
                            'n': len(model_da_list)
                        }
                        
    # Generate Report
    report_lines = [
        "# BÁO CÁO PHÂN TÍCH HIỆU NĂNG TRONG CỬA SỔ KHỦNG HOẢNG ĐỊA CHÍNH TRỊ (USA - IRAN)",
        "",
        "Báo cáo này đánh giá chuyên sâu hiệu năng dự báo Độ chính xác hướng (Directional Accuracy - DA) "
        "của GUM-Net so với 11 mô hình đối chứng trong 2 giai đoạn biến động địa chính trị lịch sử cực đoan.",
        "",
        "## 1. Định nghĩa các Cửa sổ Khủng hoảng",
        "- **May 2018 JCPOA:** Ngày 08/05/2018, Mỹ chính thức rút khỏi thỏa thuận hạt nhân JCPOA với Iran, kích hoạt chuỗi cấm vận dầu mỏ và các xung đột quân sự gián tiếp.",
        "- **May 2024 Crisis:** Sự cố rơi trực thăng của Tổng thống Iran Ebrahim Raisi vào ngày 19/05/2024, gây ra tình trạng bất ổn định địa chính trị cao độ tại Trung Đông.",
        ""
    ]
    
    for window_name in CRISIS_WINDOWS.keys():
        report_lines.append(f"## 2. Kết quả trong cửa sổ: {window_name}")
        report_lines.append("")
        
        for tt in TARGET_TYPES:
            report_lines.append(f"### Cụm sản phẩm: {tt} (Xăng dầu bán lẻ)")
            report_lines.append("")
            
            # Table headers
            headers = ["Model"] + [f"H{h}" for h in ALL_HORIZONS]
            table_header = "| " + " | ".join(headers) + " |"
            table_sep = "| " + " | ".join(["---"] * len(headers)) + " |"
            report_lines.append(table_header)
            report_lines.append(table_sep)
            
            # Gather models that have results
            valid_models = []
            for m in MODELS:
                # Check if this model has any results in this target type
                has_any = False
                for h in ALL_HORIZONS:
                    if m in crisis_results[window_name][tt][h]:
                        has_any = True
                        break
                if has_any:
                    valid_models.append(m)
                    
            # Let's sort valid_models to print GUMNet first, then others
            sorted_models = sorted(valid_models, key=lambda m: 0 if m == 'GUMNet' else 1)
            
            for m in sorted_models:
                row_vals = [m]
                for h in ALL_HORIZONS:
                    if m in crisis_results[window_name][tt][h]:
                        mean_val = crisis_results[window_name][tt][h][m]['mean']
                        std_val = crisis_results[window_name][tt][h][m]['std']
                        row_vals.append(f"{mean_val:.2f}% ± {std_val:.2f}%")
                    else:
                        row_vals.append("N/A")
                report_lines.append("| " + " | ".join(row_vals) + " |")
            report_lines.append("")
            
    report_path = 'results_v4/geopolitical_analysis_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    print(f"Report generated successfully: {report_path}")

if __name__ == '__main__':
    main()
