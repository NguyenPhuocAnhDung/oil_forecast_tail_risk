import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-8))) * 100

results_dir = 'results_v4/walkforward'
print('--- PERSISTENCE BASELINE (SHIFTED) ---')
for target in ['XANG', 'DAU']:
    for h in [1, 3, 5, 10, 60]:
        path = f'{results_dir}/GUMNet/{target}_H{h}/predictions.csv'
        if os.path.exists(path):
            df = pd.read_csv(path)
            true_vals = df['true'].values
            preds = np.roll(true_vals, h)
            preds[:h] = true_vals[0] # pad with first value
            mae = mean_absolute_error(true_vals, preds)
            rmse = np.sqrt(mean_squared_error(true_vals, preds))
            r2 = r2_score(true_vals, preds)
            mape = mean_absolute_percentage_error(true_vals, preds)
            print(f'{target}_H{h}: MAE={mae:.4f}, RMSE={rmse:.4f}, MAPE={mape:.2f}%, R2={r2:.4f}')

