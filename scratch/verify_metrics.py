import pandas as pd

df = pd.read_csv('seed42_metrics.csv')
print('Columns:', df.columns.tolist())
print('Targets:', df['target'].unique().tolist())

models_paper = ['GUMNetHet', 'PatchTST', 'iTransformer', 'TimesNet', 'DLinear', 'BiMamba', 'Chronos']

for t_name, t_code in [('MG95', 'XANG'), ('DO 0.001%', 'DAU')]:
    print(f"\n==================== {t_name} ({t_code}) ====================")
    for h in [1, 3, 5, 7, 10, 20, 60]:
        sub = df[(df['target'] == t_code) & (df['horizon'] == h) & (df['model'].isin(models_paper))]
        sub = sub.sort_values('MAE')
        print(f"\n--- Horizon H{h} ---")
        for _, row in sub.iterrows():
            print(f"{row['model']:15s} | MAE: {row['MAE']:.4f} | RMSE: {row['RMSE']:.4f} | MAPE: {row['MAPE']:.2f}% | R2: {row['R2']:.4f} | DA: {row['DA']:.2f}%")
