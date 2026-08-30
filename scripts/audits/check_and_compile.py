#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
import json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESDIR = os.path.join(BASE, 'results_v4', 'walkforward')
SEEDS = [42, 123, 777, 2025, 9999]
TARGETS = ['XANG', 'DAU']
HORIZONS = [1, 3, 5, 10, 20, 60]

def is_all_completed():
    missing = []
    for target in TARGETS:
        for h in HORIZONS:
            for seed in SEEDS:
                dirpath = Path(RESDIR) / 'GUMNet' / f'{target}_H{h}_seed{seed}'
                if not (dirpath / 'results.json').exists():
                    missing.append(f'GUMNet/{target}/H{h}/seed{seed}')
    return len(missing) == 0, missing

def main():
    completed, missing = is_all_completed()
    if not completed:
        print(f"Status: Training in progress. {len(missing)} GUMNet H60 runs remaining.")
        print("Missing runs:")
        for m in missing[:5]:
            print(f"  - {m}")
        return
        
    print("\n" + "="*80)
    print(" ALL GUMNET RUNS COMPLETED! STARTING COMPILATION PIPELINE")
    print("="*80)
    
    # 1. Finalize results (MCS, Average Rank, etc.)
    print("\nStep 1: Running finalize_results.py...")
    subprocess.run([sys.executable, 'scripts/finalize_results.py'], check=True)
    
    # 2. Fill tables 4-8 in Word Document
    print("\nStep 2: Running fill_tables_4_8.py...")
    subprocess.run([sys.executable, 'scripts/fill_tables_4_8.py'], check=True)
    
    # 3. Fill text placeholders (XEM LẠI) in Word Document
    print("\nStep 3: Running fill_xem_lai_final.py...")
    subprocess.run([sys.executable, 'scripts/fill_xem_lai_final.py'], check=True)
    
    # 4. Fix Equation 4 XML in Word Document
    print("\nStep 4: Running fix_equation_4.py...")
    subprocess.run([sys.executable, 'scripts/fix_equation_4.py'], check=True)
    
    print("\n" + "="*80)
    print(" === GUMNET EXPERIMENTS COMPLETED AND COMPILED ===")
    print("="*80)

if __name__ == '__main__':
    main()
