import os
import numpy as np
import pandas as pd
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_unified_config, DATA_PATH, RESULTS_DIR, ALL_HORIZONS
from src.utils import calculate_metrics
from src.evaluation.protocols import WalkForwardProtocol

def main():
    df_raw = pd.read_csv(DATA_PATH)
    
    # We just need df_raw for absolute prices
    # Wait, the walkforward splits are done on df, df_raw. 
    # df has log returns, df_raw has actual prices.
    # We can just load df and df_raw normally as in train_unified.py
    
    from scripts.train_unified import load_and_preprocess_data
    
    results = []
    
    for target_type in ['DAU', 'XANG']:
        for horizon in ALL_HORIZONS:
            cfg = get_unified_config(target_type, horizon)
            df, df_raw = load_and_preprocess_data(target_type, cfg)
            
            target_cols = cfg['target_cols']
            protocol = WalkForwardProtocol(seq_len=cfg['seq_len'], horizon=horizon, seed=42)
            
            all_true = []
            all_pred = []
            
            for df_train, df_val, df_raw_train, df_raw_val, df_test, df_raw_test, split_info in \
                protocol.get_splits(df, df_raw, cfg['test_days']):
                
                test_start_row = split_info.get('train_end', split_info.get('test_row', len(df) - cfg['test_days']))
                
                # Persistence: P_t+h = P_t
                # Where P_t is the last known price before the test window.
                # The test window starts at test_start_row. So P_t is at test_start_row - 1.
                
                last_known_prices = df_raw.iloc[test_start_row - 1][target_cols].values
                true_prices = df_raw.iloc[test_start_row:test_start_row + horizon][target_cols].values
                
                if len(true_prices) == 0:
                    continue
                    
                # Repeat last known price for the entire horizon
                pred_prices = np.tile(last_known_prices, (len(true_prices), 1))
                
                all_true.extend(true_prices.tolist())
                all_pred.extend(pred_prices.tolist())
                
            all_true = np.array(all_true).flatten()
            all_pred = np.array(all_pred).flatten()
            
            m = calculate_metrics(all_true, all_pred)
            results.append({
                'Target': target_type,
                'Horizon': horizon,
                'Model': 'Persistence',
                'MAE': m['MAE'],
                'RMSE': m['RMSE'],
                'MAPE (%)': m['MAPE'],
                'R2': m['R2']
            })
            
            print(f"Target: {target_type} | H{horizon} | Persistence | MAE: {m['MAE']:.3f} | RMSE: {m['RMSE']:.3f} | MAPE: {m['MAPE']:.2f}% | R2: {m['R2']:.4f}")

if __name__ == "__main__":
    main()
