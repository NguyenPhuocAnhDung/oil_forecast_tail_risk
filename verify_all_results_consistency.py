import pandas as pd
import numpy as np

# Load seed42_metrics.csv
df_metrics = pd.read_csv('seed42_metrics.csv')
print("=== METRICS DATASET SHAPE ===", df_metrics.shape)
print("Unique models:", df_metrics['model'].unique())
print("Unique targets:", df_metrics['target'].unique())
print("Unique horizons:", df_metrics['horizon'].unique())

# Key models to inspect
key_models = ['GUMNetHet', 'PatchTST', 'iTransformer', 'TimesNet', 'DLinear', 'BiMamba', 'Chronos']

print("\n=== VERIFYING TABLE 5 (XANG) VALUES ===")
for h in [1, 3, 5, 7, 10, 20, 60]:
    print(f"\n--- Horizon H{h} ---")
    for m in key_models:
        row = df_metrics[(df_metrics['target']=='XANG') & (df_metrics['horizon']==h) & (df_metrics['model']==m)]
        if not row.empty:
            mae = row['MAE'].values[0]
            rmse = row['RMSE'].values[0]
            mape = row['MAPE'].values[0]
            r2 = row['R2'].values[0]
            da = row['DA'].values[0]
            crps = row['crps'].values[0] if 'crps' in row.columns and pd.notna(row['crps'].values[0]) else 'N/A'
            mase = row['MASE'].values[0] if 'MASE' in row.columns and pd.notna(row['MASE'].values[0]) else 'N/A'
            print(f"{m:15s} | MAE={mae:.4f} | RMSE={rmse:.4f} | MAPE={mape:5.2f}% | R2={r2:.4f} | DA={da:5.2f}% | CRPS={crps} | MASE={mase}")

print("\n=== VERIFYING TABLE 6 (DAU) VALUES ===")
for h in [1, 3, 5, 7, 10, 20, 60]:
    print(f"\n--- Horizon H{h} ---")
    for m in key_models:
        row = df_metrics[(df_metrics['target']=='DAU') & (df_metrics['horizon']==h) & (df_metrics['model']==m)]
        if not row.empty:
            mae = row['MAE'].values[0]
            rmse = row['RMSE'].values[0]
            mape = row['MAPE'].values[0]
            r2 = row['R2'].values[0]
            da = row['DA'].values[0]
            crps = row['crps'].values[0] if 'crps' in row.columns and pd.notna(row['crps'].values[0]) else 'N/A'
            mase = row['MASE'].values[0] if 'MASE' in row.columns and pd.notna(row['MASE'].values[0]) else 'N/A'
            print(f"{m:15s} | MAE={mae:.4f} | RMSE={rmse:.4f} | MAPE={mape:5.2f}% | R2={r2:.4f} | DA={da:5.2f}% | CRPS={crps} | MASE={mase}")
