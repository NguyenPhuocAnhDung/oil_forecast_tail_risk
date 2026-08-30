import pandas as pd
import numpy as np
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

data_path = 'data/processed/unified_data.csv'
df = pd.read_csv(data_path)
date_col = 'Ngày' if 'Ngày' in df.columns else ('date' if 'date' in df.columns else df.columns[0])
df['Date'] = pd.to_datetime(df[date_col])
df = df.sort_values('Date').reset_index(drop=True)

df_freeze = df[df['Date'] <= '2026-04-30'].copy().reset_index(drop=True)
print(f"Dataset up to 2026-04-30: N = {len(df_freeze)} rows")
print(f"Date span: {df_freeze['Date'].iloc[0].strftime('%d/%m/%Y')} to {df_freeze['Date'].iloc[-1].strftime('%d/%m/%Y')}")

df_freeze['MG95_ret'] = np.log(df_freeze['MG95'] / df_freeze['MG95'].shift(1))
df_freeze['DO_ret'] = np.log(df_freeze['DO 0.001%'] / df_freeze['DO 0.001%'].shift(1))

full_mg95_vol = df_freeze['MG95_ret'].std() * np.sqrt(252) * 100
full_do_vol = df_freeze['DO_ret'].std() * np.sqrt(252) * 100
full_gpr_mean = df_freeze['GPR'].mean()

print(f"\nFull period (2008-2026): MG95 Ann Vol = {full_mg95_vol:.2f}%, DO Ann Vol = {full_do_vol:.2f}%, GPR Mean = {full_gpr_mean:.2f}")

test_days_map = {
    1: 100,
    3: 100,
    5: 100,
    7: 150,
    10: 200,
    20: 300,
    60: 600
}

print("\n" + "="*80)
print("TEST SET DETAILED CHARACTERISTICS (FROZEN DATASET N=4512)")
print("="*80)

for h, td in test_days_map.items():
    test_slice = df_freeze.iloc[-td:]
    start_dt = test_slice['Date'].iloc[0].strftime('%d/%m/%Y')
    end_dt = test_slice['Date'].iloc[-1].strftime('%d/%m/%Y')
    
    mg95_vol = test_slice['MG95_ret'].std() * np.sqrt(252) * 100
    do_vol = test_slice['DO_ret'].std() * np.sqrt(252) * 100
    
    mg95_min, mg95_max = test_slice['MG95'].min(), test_slice['MG95'].max()
    do_min, do_max = test_slice['DO 0.001%'].min(), test_slice['DO 0.001%'].max()
    
    mg95_swing = (mg95_max - mg95_min) / mg95_min * 100
    do_swing = (do_max - do_min) / do_min * 100
    
    gpr_mean = test_slice['GPR'].mean()
    gpr_max = test_slice['GPR'].max()
    gpr_p90 = test_slice['GPR'].quantile(0.9)
    
    # Train slice before test
    train_slice = df_freeze.iloc[:-td]
    train_mg95_vol = train_slice['MG95_ret'].std() * np.sqrt(252) * 100
    train_do_vol = train_slice['DO_ret'].std() * np.sqrt(252) * 100
    
    print(f"Horizon H{h:02d} | Test Days: {td:3d} | Date Range: {start_dt} to {end_dt}")
    print(f"  - Volatility MG95: Test = {mg95_vol:.2f}% vs Train = {train_mg95_vol:.2f}% (Ratio: {mg95_vol/train_mg95_vol:.2f}x)")
    print(f"  - Volatility DO:   Test = {do_vol:.2f}% vs Train = {train_do_vol:.2f}% (Ratio: {do_vol/train_do_vol:.2f}x)")
    print(f"  - Price Amplitude MG95: [{mg95_min:.2f}, {mg95_max:.2f}] USD/bbl (+{mg95_swing:.1f}%)")
    print(f"  - Price Amplitude DO:   [{do_min:.2f}, {do_max:.2f}] USD/bbl (+{do_swing:.1f}%)")
    print(f"  - GPR Index: Mean = {gpr_mean:.2f} (Full sample mean = {full_gpr_mean:.2f}), Max = {gpr_max:.2f}, P90 = {gpr_p90:.2f}")
    print("-" * 80)
