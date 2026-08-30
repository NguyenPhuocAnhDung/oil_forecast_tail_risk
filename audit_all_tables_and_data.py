import os
import sys
import pandas as pd
import numpy as np
from scipy.stats import jarque_bera, skew, kurtosis
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
import warnings
warnings.filterwarnings('ignore')

# 1. Load Data
df = pd.read_csv('data/processed/clean_data_exo.csv')
# Clean whitespace in column names
df.columns = [c.strip() for c in df.columns]
print(f"=== 1. DATASET PROPERTIES ===", flush=True)
print(f"Shape: {df.shape}", flush=True)
print(f"Date range: {df['Ngày'].iloc[0]} to {df['Ngày'].iloc[-1]}", flush=True)

# Derive moving averages, ratios, volatilities
if 'WTI' in df.columns:
    df['WTI_Daily'] = df['WTI']
if 'BRT DTD' in df.columns:
    df['BRT_DTD'] = df['BRT DTD']
if 'GPR' in df.columns:
    df['GPR_MA30'] = df['GPR'].rolling(30, min_periods=1).mean()
if 'USD_Index' in df.columns:
    df['USD_Index_MA30'] = df['USD_Index'].rolling(30, min_periods=1).mean()

wti_safe = np.maximum(df['WTI'].values, 1e-4)
df['Ratio_95_WTI'] = df['MG95'] / wti_safe
df['Ratio_92_WTI'] = df['MG92'] / wti_safe
df['Ratio_DO001_WTI'] = df['DO 0.001%'] / wti_safe
df['Ratio_DO05_WTI'] = df['DO 0.05%'] / wti_safe

# Volatility
ret_wti = np.diff(np.log(np.maximum(df['WTI'].values, 1e-4)), prepend=0)
df['Vol_WTI_10d'] = pd.Series(ret_wti).rolling(10, min_periods=1).std() * np.sqrt(252) * 100
df['Vol_WTI_30d'] = pd.Series(ret_wti).rolling(30, min_periods=1).std() * np.sqrt(252) * 100

# Calendar cyclical
t_idx = np.arange(len(df))
df['Day_sin'] = np.sin(2 * np.pi * (t_idx % 252) / 252)
df['Day_cos'] = np.cos(2 * np.pi * (t_idx % 252) / 252)

# Variables for Table 2
table2_vars = [
    ('MG95', 'MG95 (P_t^95)', 'Mục tiêu Xăng', 'USD/thùng (Platts)'),
    ('MG92', 'MG92 (P_t^92)', 'Mục tiêu Xăng', 'USD/thùng (Platts)'),
    ('DO 0.001%', 'DO 0.001% (P_t^DO1)', 'Mục tiêu Dầu', 'USD/thùng (Platts)'),
    ('DO 0.05%', 'DO 0.05% (P_t^DO5)', 'Mục tiêu Dầu', 'USD/thùng (Platts)'),
    ('MG97', 'MG97', 'Ngoại sinh Liên sản phẩm', 'USD/thùng (Platts)'),
    ('NAPHTHA', 'NAPHTHA', 'Ngoại sinh Liên sản phẩm', 'USD/thùng (Platts)'),
    ('KERO', 'KERO', 'Ngoại sinh Liên sản phẩm', 'USD/thùng (Platts)'),
    ('FO 180', 'FO 180', 'Ngoại sinh Liên sản phẩm', 'USD/tấn (Platts)'),
    ('WTI_Daily', 'WTI_Daily', 'Dầu thô Chuẩn', 'USD/thùng (NYMEX/EIA)'),
    ('BRT_DTD', 'BRT_DTD', 'Dầu thô Chuẩn', 'USD/thùng (Platts)'),
    ('GPR', 'GPR', 'Rủi ro Địa chính trị', 'Chỉ số (Caldara-Iacoviello)'),
    ('GPR_MA30', 'GPR_MA30', 'GPR Làm mịn', 'Chỉ số (MA 30 ngày)'),
    ('USD_Index', 'USD_Index (DXY)', 'Động lực Tiền tệ Vĩ mô', 'Chỉ số (FRED/St. Louis)'),
    ('USD_Index_MA30', 'USD_Index_MA30', 'DXY Làm mịn', 'Chỉ số (MA 30 ngày)'),
    ('Ratio_95_WTI', 'Ratio_95_WTI', 'Tỷ lệ Crack Spread', 'Tỷ lệ (MG95 / WTI)'),
    ('Ratio_DO001_WTI', 'Ratio_DO001_WTI', 'Tỷ lệ Crack Spread', 'Tỷ lệ (DO1 / WTI)'),
    ('Vol_WTI_10d', 'Vol_WTI_10d / 30d', 'Độ biến động Thực tế', '% Năm (Cửa sổ trượt)'),
    ('Day_sin', 'Day_sin / Day_cos', 'Chu kỳ Lịch', 'Mã hóa Lượng giác')
]

print("\n=== 2. EXACT EMPIRICAL TABLE 2 RESULTS ===", flush=True)
table2_rows = []
for col_key, name_label, category, unit in table2_vars:
    if col_key in df.columns:
        s = df[col_key].dropna().values
        m = np.mean(s)
        std = np.std(s)
        min_v = np.min(s)
        max_v = np.max(s)
        adf_stat, adf_p, _, _, _, _ = adfuller(s, autolag='AIC')
        stat_status = "I(0) Dừng" if adf_p < 0.05 else "I(1) Phi dừng"
        table2_rows.append({
            'Ký hiệu': name_label,
            'Danh mục': category,
            'Đơn vị': unit,
            'Mean ± Std': f"{m:.2f} ± {std:.2f}",
            'Min / Max': f"{min_v:.2f} / {max_v:.2f}",
            'ADF Stat (p-val)': f"{adf_stat:.3f} ({adf_p:.4f})" if adf_p >= 0.0001 else f"{adf_stat:.3f} (<0.0001)",
            'Tính dừng': stat_status
        })
df_t2_computed = pd.DataFrame(table2_rows)
print(df_t2_computed.to_string(index=False), flush=True)

# 3. Econometric Diagnostics for Table 3
print("\n=== 3. EXACT EMPIRICAL TABLE 3 RESULTS ===", flush=True)
table3_vars = ['MG95', 'MG92', 'DO 0.001%', 'DO 0.05%', 'WTI', 'GPR', 'USD_Index']
table3_rows = []
for col in table3_vars:
    s = df[col].dropna().values
    # Level ADF & KPSS
    adf_lvl, p_adf_lvl, _, _, _, _ = adfuller(s, autolag='AIC')
    kpss_lvl, p_kpss_lvl, _, _ = kpss(s, regression='c', nlags='auto')
    
    # Return series
    if (s > 0).all():
        ret = np.diff(np.log(s))
    else:
        ret = np.diff(s)
        
    adf_ret, p_adf_ret, _, _, _, _ = adfuller(ret, autolag='AIC')
    sk = skew(ret)
    kurt = kurtosis(ret) # Excess kurtosis
    jb_stat, jb_p = jarque_bera(ret)
    lb_res = acorr_ljungbox(ret, lags=[10], return_df=True)
    lb_stat = lb_res['lb_stat'].values[0]
    lb_p = lb_res['lb_pvalue'].values[0]
    
    # ARCH-LM test on residuals (demeaned return)
    arch_stat, arch_p, _, _ = het_arch(ret - np.mean(ret))
    
    table3_rows.append({
        'Chuỗi': col,
        'ADF Mức (p)': f"{adf_lvl:.2f} ({p_adf_lvl:.3f})",
        'KPSS Mức (p)': f"{kpss_lvl:.2f} ({p_kpss_lvl:.2f})",
        'ADF Lợi suất (p)': f"{adf_ret:.2f} ({p_adf_ret:.4f})" if p_adf_ret >= 0.001 else f"{adf_ret:.2f} (<0.001)",
        'Skew': f"{sk:.2f}",
        'Kurt': f"{kurt:.2f}",
        'JB Stat (p)': f"{jb_stat:.1f} ({jb_p:.4f})" if jb_p >= 0.001 else f"{jb_stat:,.1f} (<0.001)",
        'LB Q(10) (p)': f"{lb_stat:.2f} ({lb_p:.3f})",
        'ARCH-LM (p)': f"{arch_stat:.2f} ({arch_p:.4e})"
    })
df_t3_computed = pd.DataFrame(table3_rows)
print(df_t3_computed.to_string(index=False), flush=True)
