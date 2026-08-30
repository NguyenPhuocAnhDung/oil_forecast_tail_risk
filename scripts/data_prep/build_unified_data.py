"""
build_unified_data.py
=====================
Script hợp nhất 2 nguồn dữ liệu (clean_data_exo.csv + trading_data_business_days.csv)
thành 1 file unified_data.csv chứa TẤT CẢ features cần thiết.

Output: data/processed/unified_data.csv
"""

import pandas as pd
import numpy as np
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

current_dir = os.path.dirname(os.path.abspath(__file__))
print("=" * 80)
print(" BUILD UNIFIED DATA — FAIR COMPARISON FIX (EXTENDED TO APRIL 30)")
print("=" * 80)

# 1. Đọc 2 nguồn dữ liệu
exo_path = os.path.join(current_dir, 'data', 'processed', 'clean_data_exo.csv')
trading_path = os.path.join(current_dir, 'data', 'processed', 'trading_data_business_days.csv')

df_exo = pd.read_csv(exo_path)
df_exo.columns = df_exo.columns.str.strip()
df_exo['Ngày'] = pd.to_datetime(df_exo['Ngày'])
print(f"📥 clean_data_exo.csv: {df_exo.shape}, cols: {list(df_exo.columns)}")

df_trading = pd.read_csv(trading_path)
df_trading.columns = df_trading.columns.str.strip()
df_trading['Ngày'] = pd.to_datetime(df_trading['Ngày'])
print(f"📥 trading_data_business_days.csv: {df_trading.shape}, cols: {list(df_trading.columns)}")

# 2. Bắt đầu từ df_exo
df_unified = df_exo.copy()

# 3. Rename các cột trong exo để khớp convention
rename_map = {
    'BRT DTD': 'BRT_DTD',
    'BRT KH': 'BRT_KH',
    'KERO ': 'KERO',
}
df_unified.rename(columns=rename_map, inplace=True)

# Drop duplicate columns that are also in trading_data to prefer trading_data values
cols_to_drop = ['MG95', 'MG92', 'DO 0.001%', 'DO 0.05%', 'WTI', 'USD_Index', 'GPR']
df_unified.drop(columns=[c for c in cols_to_drop if c in df_unified.columns], inplace=True, errors='ignore')

# 4. Merge với df_trading bằng right merge để lấy toàn bộ ngày trong trading_data (đến 30/04/2026)
df_unified = pd.merge(df_unified, df_trading, on='Ngày', how='right')

# 5. Xử lý trường hợp WTI_Daily và Brent_EU_Daily
if 'WTI_Daily' not in df_unified.columns and 'WTI' in df_unified.columns:
    df_unified['WTI_Daily'] = df_unified['WTI']
if 'Brent_EU_Daily' not in df_unified.columns and 'BRT_DTD' in df_unified.columns:
    df_unified['Brent_EU_Daily'] = df_unified['BRT_DTD']

# 6. Fill NaN cho các cột từ trading
fill_cols = ['Brent_EU_Daily', 'WTI_Daily', 'Brent_Global_Monthly', 'WTI_Monthly',
             'DayOfWeek', 'Day_sin', 'Day_cos', 'USD_Index', 'GPR']
for col in fill_cols:
    if col in df_unified.columns:
        df_unified[col] = df_unified[col].ffill()

# 7. Tính Day_sin, Day_cos cho các dòng thiếu
if 'DayOfWeek' in df_unified.columns:
    mask = df_unified['Day_sin'].isna() & df_unified['DayOfWeek'].notna()
    if mask.any():
        df_unified.loc[mask, 'Day_sin'] = np.sin(2 * np.pi * df_unified.loc[mask, 'DayOfWeek'] / 5)
        df_unified.loc[mask, 'Day_cos'] = np.cos(2 * np.pi * df_unified.loc[mask, 'DayOfWeek'] / 5)

# 8. Drop các cột không cần
if 'WTI' in df_unified.columns:
    df_unified.drop(columns=['WTI'], inplace=True)

# 9. Forward fill + drop NaN cho numeric columns
numeric_cols = [c for c in df_unified.columns if c != 'Ngày']
df_unified[numeric_cols] = df_unified[numeric_cols].ffill()
df_unified.dropna(subset=numeric_cols, inplace=True)

# 10. Sort theo ngày
df_unified = df_unified.sort_values('Ngày').reset_index(drop=True)

# 11. Cutoff
df_unified = df_unified[df_unified['Ngày'] <= '2026-04-30'].reset_index(drop=True)

# 12. Save
output_path = os.path.join(current_dir, 'data', 'processed', 'unified_data.csv')
df_unified.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n✅ HOÀN TẤT! unified_data.csv")
print(f"   Shape: {df_unified.shape}")
print(f"   Columns ({len(df_unified.columns)}): {list(df_unified.columns)}")
print(f"   Date range: {df_unified['Ngày'].min()} → {df_unified['Ngày'].max()}")
print(f"   Saved to: {output_path}")

# 13. Kiểm tra các features cần thiết có đủ không
required = {
    'Petroleum Products': ['MG97', 'MG95', 'MG92', 'NAPHTHA', 'KERO', 'DO 0.001%', 'DO 0.05%', 'FO 180'],
    'Crude Benchmarks': ['WTI_Daily', 'Brent_EU_Daily', 'BRT_DTD', 'BRT_KH'],
    'Macro': ['USD_Index', 'GPR'],
    'Monthly': ['WTI_Monthly', 'Brent_Global_Monthly'],
    'Calendar': ['Day_sin', 'Day_cos'],
}
print(f"\n📋 KIỂM TRA FEATURES:")
all_ok = True
for group, cols in required.items():
    present = [c for c in cols if c in df_unified.columns]
    missing = [c for c in cols if c not in df_unified.columns]
    status = "✅" if not missing else "❌"
    print(f"  {status} {group}: {len(present)}/{len(cols)} {'(thiếu: ' + str(missing) + ')' if missing else ''}")
    if missing:
        all_ok = False

if all_ok:
    print("\n🎉 TẤT CẢ features cần thiết đều có mặt!")
else:
    print("\n⚠️ Có features thiếu, cần kiểm tra lại nguồn dữ liệu.")
