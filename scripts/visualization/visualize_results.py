"""
scripts/visualize_results.py
=======================================
Vẽ biểu đồ phân tích kết quả dự báo từ file CSV đã được compile.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(PROJECT_ROOT, 'docs', 'Compiled_Results.csv')
FIGURES_DIR = os.path.join(PROJECT_ROOT, 'docs', 'figures')

def plot_mape_bar_chart(df, target):
  """Vẽ biểu đồ Bar chart so sánh MAPE của các mô hình theo từng Horizon."""
  plt.figure(figsize=(14, 7))
  sns.set_theme(style="whitegrid")
  
  df_target = df[df['Target'] == target].copy()
  # Loại bỏ tiền tố 'H' để lấy số nguyên sort nếu cần, nhưng định dạng hiện tại là H01, H05...
  # đã có thể sort được bằng string
  
  ax = sns.barplot(x='Horizon', y='MAPE (%)', hue='Model', data=df_target, palette='tab10')
  plt.title(f'MAPE Comparison across Horizons - {target}', fontsize=16, pad=15)
  plt.xlabel('Horizon (Days)', fontsize=14)
  plt.ylabel('MAPE (%)', fontsize=14)
  plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
  plt.tight_layout()
  
  out_path = os.path.join(FIGURES_DIR, f'MAPE_BarChart_{target}.png')
  plt.savefig(out_path, dpi=300)
  plt.close()
  pass

def plot_degradation_line_chart(df, target, metric='MAE'):
  """Vẽ biểu đồ Line chart thể hiện sự phân rã hiệu năng (Degradation) khi Horizon tăng."""
  plt.figure(figsize=(12, 6))
  sns.set_theme(style="ticks")
  
  df_target = df[df['Target'] == target].copy()
  
  # Vẽ line plot có marker
  sns.lineplot(x='Horizon', y=metric, hue='Model', style='Model', 
         markers=True, dashes=False, data=df_target, linewidth=2.5, palette='tab10')
         
  plt.title(f'{metric} Degradation across Horizons - {target}', fontsize=16, pad=15)
  plt.xlabel('Horizon (Days)', fontsize=14)
  plt.ylabel(metric, fontsize=14)
  plt.grid(True, linestyle='--', alpha=0.7)
  plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
  plt.tight_layout()
  
  out_path = os.path.join(FIGURES_DIR, f'{metric}_Degradation_{target}.png')
  plt.savefig(out_path, dpi=300)
  plt.close()
  pass

def main():
  if not os.path.exists(CSV_PATH):
    print(f"Lỗi: Không tìm thấy file {CSV_PATH}. Vui lòng chạy compile_results.py trước.")
    return
    
  os.makedirs(FIGURES_DIR, exist_ok=True)
  df = pd.read_csv(CSV_PATH)
  
  targets = df['Target'].unique()
  for target in targets:
    plot_mape_bar_chart(df, target)
    plot_degradation_line_chart(df, target, metric='MAE')
    plot_degradation_line_chart(df, target, metric='R2')

if __name__ == '__main__':
  main()
