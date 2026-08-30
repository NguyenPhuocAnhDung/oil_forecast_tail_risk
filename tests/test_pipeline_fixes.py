import os
import sys
import unittest
import numpy as np
import pandas as pd
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.dm_test_32models import diebold_mariano_test
from scripts.compile_32model_results import compute_metrics_from_pred

class TestPipelineFixes(unittest.TestCase):
    def test_diebold_mariano_hln_correction(self):
        """Verify that the HLN correction in scripts/dm_test_32models.py is correct and not inflated by np.sqrt(T)."""
        # Create dummy error series
        np.random.seed(42)
        err1 = np.random.normal(0, 1, 100)
        err2 = np.random.normal(0.1, 1, 100)
        horizon = 3
        
        stat, pval = diebold_mariano_test(err1, err2, horizon, loss_type='mae')
        
        # Verify the calculation manually
        d = np.abs(err1) - np.abs(err2)
        T = len(d)
        d_mean = np.mean(d)
        
        # Bandwidth selection
        q = int(max(0, min(horizon - 1, np.floor(1.2 * (T**(1/3))))))
        
        # Manual HAC variance
        from scripts.dm_test_32models import compute_hac_variance
        var_d_mean = compute_hac_variance(d, q)
        dm_stat = d_mean / np.sqrt(var_d_mean)
        
        hln_factor = np.sqrt((T + 1 - 2 * horizon + (horizon * (horizon - 1)) / T) / T)
        expected_dm_hln = dm_stat * hln_factor
        
        # The returned stat should match expected_dm_hln exactly
        self.assertAlmostEqual(stat, expected_dm_hln, places=7)

    def test_compile_metrics_division_by_zero(self):
        """Verify that compute_metrics_from_pred handles constant/near-constant true prices (std_true < 1e-5) safely."""
        # Case 1: Standard deviation is zero (constant prices)
        df_pred_const = pd.DataFrame({
            'true': [10.0, 10.0, 10.0, 10.0],
            'pred': [9.9, 10.1, 10.0, 10.2],
            'product': ['A', 'A', 'A', 'A'],
            'date': pd.date_range('2026-01-01', periods=4),
            'q10': [9.8, 9.8, 9.8, 9.8],
            'q90': [10.2, 10.2, 10.2, 10.2]
        })
        
        mae, rmse, r2, da, picp, pinaw = compute_metrics_from_pred(df_pred_const)
        
        # R2 and PINAW should be NaN due to std_true being 0.0
        self.assertTrue(np.isnan(r2), "R2 should be NaN when std_true < 1e-5")
        self.assertTrue(np.isnan(pinaw), "PINAW should be NaN when std_true < 1e-5")
        self.assertAlmostEqual(mae, 0.1, places=5)
        self.assertAlmostEqual(rmse, np.sqrt(0.06 / 4), places=5)
        
        # Case 2: Standard deviation is normal
        df_pred_normal = pd.DataFrame({
            'true': [10.0, 11.0, 12.0, 13.0],
            'pred': [10.1, 10.9, 12.1, 12.9],
            'product': ['A', 'A', 'A', 'A'],
            'date': pd.date_range('2026-01-01', periods=4),
            'q10': [9.5, 10.5, 11.5, 12.5],
            'q90': [10.5, 11.5, 12.5, 13.5]
        })
        
        mae, rmse, r2, da, picp, pinaw = compute_metrics_from_pred(df_pred_normal)
        self.assertFalse(np.isnan(r2), "R2 should NOT be NaN when std_true is normal")
        self.assertFalse(np.isnan(pinaw), "PINAW should NOT be NaN when std_true is normal")

    def test_compute_metrics_missing_columns(self):
        """Verify compute_metrics_from_pred raises KeyError if 'true' or 'pred' is missing, even when empty."""
        # Case 1: Empty DataFrame, missing columns
        df_empty_missing = pd.DataFrame(columns=['product', 'date'])
        with self.assertRaises(KeyError) as ctx:
            compute_metrics_from_pred(df_empty_missing)
        self.assertIn("Required columns 'true' and 'pred' are missing", str(ctx.exception))

        # Case 2: Non-empty DataFrame, missing 'true'
        df_no_true = pd.DataFrame({'pred': [1.0, 2.0], 'product': ['A', 'A']})
        with self.assertRaises(KeyError):
            compute_metrics_from_pred(df_no_true)

        # Case 3: Non-empty DataFrame, missing 'pred'
        df_no_pred = pd.DataFrame({'true': [1.0, 2.0], 'product': ['A', 'A']})
        with self.assertRaises(KeyError):
            compute_metrics_from_pred(df_no_pred)

        # Case 4: Empty DataFrame with correct columns should not raise KeyError
        df_empty_ok = pd.DataFrame(columns=['true', 'pred', 'product'])
        mae, rmse, r2, da, picp, pinaw = compute_metrics_from_pred(df_empty_ok)
        self.assertTrue(np.isnan(mae))
        self.assertTrue(np.isnan(rmse))

    def test_compile_main_excludes_all_nan_runs(self):
        """Verify that compile_32model_results main loop excludes runs where both MAE and RMSE are NaN."""
        from scripts.compile_32model_results import main as compile_main
        from unittest.mock import patch
        import json

        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_fixes_test')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)

        try:
            walkforward_dir = os.path.join(temp_dir, 'walkforward')
            os.makedirs(walkforward_dir, exist_ok=True)

            # Create a run that has NaN metrics (in results.json, and no predictions.csv)
            nan_model_dir = os.path.join(walkforward_dir, 'Model_All_NaN', 'XANG_H3_seed42')
            os.makedirs(nan_model_dir, exist_ok=True)
            with open(os.path.join(nan_model_dir, 'results.json'), 'w') as f:
                json.dump({
                    'datetime': '2026-07-18T00:00:00Z',
                    'metrics': {'MAE': np.nan, 'RMSE': np.nan}
                }, f)

            # Create a valid run to ensure compilation succeeds and writes records
            valid_model_dir = os.path.join(walkforward_dir, 'Model_Valid', 'XANG_H3_seed42')
            os.makedirs(valid_model_dir, exist_ok=True)
            with open(os.path.join(valid_model_dir, 'results.json'), 'w') as f:
                json.dump({
                    'datetime': '2026-07-18T00:00:00Z',
                    'metrics': {'MAE': 0.15, 'RMSE': 0.25}
                }, f)

            # Run main compile command
            with patch('sys.argv', ['compile_32model_results.py', '--results-dir', temp_dir]):
                compile_main()

            compiled_csv = os.path.join(temp_dir, 'compiled_32model_results.csv')
            self.assertTrue(os.path.exists(compiled_csv))

            df_res = pd.read_csv(compiled_csv)
            # Model_Valid should be included
            self.assertIn('Model_Valid', df_res['Model'].values)
            # Model_All_NaN should be excluded
            self.assertNotIn('Model_All_NaN', df_res['Model'].values)

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

if __name__ == '__main__':
    unittest.main()
