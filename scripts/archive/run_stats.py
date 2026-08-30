import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('data/processed/unified_data.csv')
targets = {'Xang RON95': 'MG95', 'Xang RON92/E5': 'MG92', 'Diesel DO 0,05%S': 'DO 0.05%', 'Diesel DO 0,001%S-V': 'DO 0.001%'}

print('--- DESCRIPTIVE STATS ---')
for name, col in targets.items():
    series = df[col].dropna()
    diffs = series.diff().dropna()
    num_changes = (diffs != 0).sum()
    print(f'{name}: Mean={series.mean():.2f}, Std={series.std():.2f}, Min={series.min():.2f}, Max={series.max():.2f}, Changes={num_changes}')

print('\n--- ADF & KPSS TESTS ---')
for name, col in targets.items():
    series = df[col].dropna()
    adf_res = adfuller(series, autolag='AIC')
    kpss_res = kpss(series, regression='c', nlags='auto')
    print(f'{name}:')
    print(f'  ADF: stat={adf_res[0]:.4f}, p-value={adf_res[1]:.4f}, lags={adf_res[2]}')
    print(f'  KPSS: stat={kpss_res[0]:.4f}, p-value={kpss_res[1]:.4f}')

