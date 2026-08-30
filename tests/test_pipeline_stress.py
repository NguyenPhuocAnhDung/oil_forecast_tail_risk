import os
import sys
import json
import unittest
import numpy as np
import pandas as pd
import shutil
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.compile_32model_results import compute_metrics_from_pred, main as compile_main
from scripts.dm_test_32models import diebold_mariano_test, run_mcs, main as dm_main
from scripts.effect_size_32models import compute_effect_size_fast, main as effect_size_main
from scripts.generate_all_outputs import main as generate_main, generate_tables, generate_figures
from scripts.run_all_32models import main as run_all_main

class TestPipelineStress(unittest.TestCase):
    def setUp(self):
        self.temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_stress_results')
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ==========================================
    # 1. compile_32model_results.py Stress Tests
    # ==========================================

    def test_compile_compute_metrics_empty(self):
        """Test compute_metrics_from_pred with empty or missing columns."""
        # Empty DataFrame with correct columns
        df_empty = pd.DataFrame(columns=['true', 'pred', 'product', 'date', 'q10', 'q90'])
        mae, rmse, r2, da, picp, pinaw = compute_metrics_from_pred(df_empty)
        self.assertTrue(np.isnan(mae))
        self.assertTrue(np.isnan(rmse))
        self.assertTrue(np.isnan(r2))
        self.assertEqual(da, 0.0)
        self.assertTrue(np.isnan(picp))
        self.assertTrue(np.isnan(pinaw))

        # Missing columns - should raise KeyError (which the main script catches)
        df_invalid = pd.DataFrame(columns=['wrong_col'])
        with self.assertRaises(KeyError):
            compute_metrics_from_pred(df_invalid)

    def test_compile_compute_metrics_unexpected_types(self):
        """Test compute_metrics_from_pred with strings or other unexpected types."""
        df_str = pd.DataFrame({
            'true': ['a', 'b', 'c'],
            'pred': [1.0, 2.0, 3.0],
            'product': ['P1', 'P1', 'P1'],
            'date': ['2026-01-01', '2026-01-02', '2026-01-03']
        })
        with self.assertRaises(TypeError):
            compute_metrics_from_pred(df_str)

    def test_compile_compute_metrics_nan_inf(self):
        """Test compute_metrics_from_pred with NaN and Inf values."""
        df_nan = pd.DataFrame({
            'true': [1.0, np.nan, 3.0, 4.0],
            'pred': [1.1, 2.0, np.inf, 4.0],
            'product': ['P1', 'P1', 'P1', 'P1'],
            'date': ['2026-01-01', '2026-01-02', '2026-01-03', '2026-01-04']
        })
        mae, rmse, r2, da, picp, pinaw = compute_metrics_from_pred(df_nan)
        # Should not crash, but should return nan for arithmetic operations
        self.assertTrue(np.isnan(mae) or np.isinf(mae))
        self.assertTrue(np.isnan(rmse) or np.isinf(rmse))

    def test_compile_main_robustness(self):
        """Integration stress test for compile_32model_results main execution."""
        walkforward_dir = os.path.join(self.temp_dir, 'walkforward')
        os.makedirs(walkforward_dir, exist_ok=True)

        # 1. Model folder with missing results.json
        m1_dir = os.path.join(walkforward_dir, 'Model_Missing_Json', 'XANG_H3_seed42')
        os.makedirs(m1_dir, exist_ok=True)
        # Write predictions.csv only
        pd.DataFrame({'true': [1,2], 'pred': [1,2]}).to_csv(os.path.join(m1_dir, 'predictions.csv'), index=False)

        # 2. Model folder with corrupt results.json
        m2_dir = os.path.join(walkforward_dir, 'Model_Corrupt_Json', 'XANG_H3_seed42')
        os.makedirs(m2_dir, exist_ok=True)
        with open(os.path.join(m2_dir, 'results.json'), 'w') as f:
            f.write("{invalid json")

        # 3. Model folder with empty predictions.csv
        m3_dir = os.path.join(walkforward_dir, 'Model_Empty_Csv', 'XANG_H3_seed42')
        os.makedirs(m3_dir, exist_ok=True)
        with open(os.path.join(m3_dir, 'results.json'), 'w') as f:
            json.dump({'datetime': '2026-01-01T00:00:00Z', 'metrics': {'MAE': 0.5}}, f)
        with open(os.path.join(m3_dir, 'predictions.csv'), 'w') as f:
            f.write("") # Empty file

        # 4. Model folder with unexpected data types in predictions.csv
        m4_dir = os.path.join(walkforward_dir, 'Model_String_Csv', 'XANG_H3_seed42')
        os.makedirs(m4_dir, exist_ok=True)
        with open(os.path.join(m4_dir, 'results.json'), 'w') as f:
            json.dump({'datetime': '2026-01-01T00:00:00Z'}, f)
        pd.DataFrame({'true': ['abc', 'def'], 'pred': [1.0, 2.0]}).to_csv(os.path.join(m4_dir, 'predictions.csv'), index=False)

        # 5. Model folder with valid predictions but missing q10/q90 (fallback case)
        m5_dir = os.path.join(walkforward_dir, 'Model_Valid_Fallback', 'XANG_H3_seed42')
        os.makedirs(m5_dir, exist_ok=True)
        with open(os.path.join(m5_dir, 'results.json'), 'w') as f:
            json.dump({'datetime': '2026-01-01T00:00:00Z', 'metrics': {'MAE': 0.1, 'RMSE': 0.2}}, f)
        # Predictions exist but don't have product column, causing KeyError in compute_metrics_from_pred.
        # This will trigger fallback to results.json values.
        pd.DataFrame({'true': [1.0, 2.0], 'pred': [1.1, 1.9]}).to_csv(os.path.join(m5_dir, 'predictions.csv'), index=False)

        # Run compilation
        with patch('sys.argv', ['compile_32model_results.py', '--results-dir', self.temp_dir]):
            compile_main()

        # Verify compiled results exist
        compiled_csv = os.path.join(self.temp_dir, 'compiled_32model_results.csv')
        self.assertTrue(os.path.exists(compiled_csv))
        
        df_res = pd.read_csv(compiled_csv)
        # It should contain Model_Valid_Fallback since it falls back to results.json metrics
        self.assertIn('Model_Valid_Fallback', df_res['Model'].values)
        # Corrupt and empty predictions should be excluded from final compiled results
        self.assertNotIn('Model_Corrupt_Json', df_res['Model'].values)
        self.assertNotIn('Model_Missing_Json', df_res['Model'].values)
        self.assertNotIn('Model_String_Csv', df_res['Model'].values)

    # ==========================================
    # 2. dm_test_32models.py Stress Tests
    # ==========================================

    def test_dm_extremely_short_series(self):
        """Test Diebold-Mariano test with T < 5."""
        err1 = np.array([0.1, 0.2, 0.3])
        err2 = np.array([0.15, 0.25, 0.35])
        stat, pval = diebold_mariano_test(err1, err2, horizon=3)
        self.assertEqual(stat, 0.0)
        self.assertEqual(pval, 1.0)

    def test_dm_constant_zero_residuals(self):
        """Test Diebold-Mariano test with constant zero residuals (perfect forecasts)."""
        err1 = np.zeros(10)
        err2 = np.zeros(10)
        stat, pval = diebold_mariano_test(err1, err2, horizon=3)
        self.assertEqual(stat, 0.0)
        self.assertEqual(pval, 1.0)

    def test_dm_nan_inf_values(self):
        """Test Diebold-Mariano test with infinite/NaN values."""
        err1 = np.array([0.1, np.nan, 0.3, 0.4, 0.5])
        err2 = np.array([0.15, 0.25, np.inf, 0.35, 0.45])
        stat, pval = diebold_mariano_test(err1, err2, horizon=3)
        # Should not crash, returns NaN/sensible defaults
        self.assertTrue(np.isnan(stat))
        self.assertEqual(pval, 1.0)

    def test_mcs_extremely_short_series(self):
        """Test Hansen's MCS with very short time series (e.g. T=4)."""
        L = np.random.normal(0, 1, (4, 3))
        active_set, mcs_pvals = run_mcs(L, alpha=0.10, B=10, horizon=3)
        self.assertTrue(len(active_set) >= 1)
        self.assertEqual(len(mcs_pvals), 3)

    def test_mcs_constant_zero(self):
        """Test Hansen's MCS with constant zero loss series."""
        L = np.zeros((10, 3))
        active_set, mcs_pvals = run_mcs(L, alpha=0.10, B=10, horizon=3)
        # Should break early and keep all models in the active set with pval 1.0
        self.assertEqual(len(active_set), 3)
        for val in mcs_pvals.values():
            self.assertEqual(val, 1.0)

    def test_mcs_nan_inf_values(self):
        """Test Hansen's MCS with infinite/NaN values."""
        L = np.random.normal(0, 1, (10, 3))
        L[2, 0] = np.nan
        L[5, 1] = np.inf
        # Should execute and eliminate/return without crashing
        active_set, mcs_pvals = run_mcs(L, alpha=0.10, B=10, horizon=3)
        self.assertTrue(len(active_set) >= 1)

    # ==========================================
    # 3. effect_size_32models.py Stress Tests
    # ==========================================

    def test_effect_size_empty_groups(self):
        """Test compute_effect_size_fast with empty groups."""
        delta, a12 = compute_effect_size_fast([], [1, 2, 3])
        self.assertEqual(delta, 0.0)
        self.assertEqual(a12, 0.5)

        delta, a12 = compute_effect_size_fast([1, 2, 3], [])
        self.assertEqual(delta, 0.0)
        self.assertEqual(a12, 0.5)

    def test_effect_size_different_lengths(self):
        """Test compute_effect_size_fast with groups of different lengths."""
        group1 = np.random.normal(0.1, 1, 10)
        group2 = np.random.normal(0, 1, 15)
        delta, a12 = compute_effect_size_fast(group1, group2)
        self.assertTrue(-1.0 <= delta <= 1.0)
        self.assertTrue(0.0 <= a12 <= 1.0)

    def test_effect_size_nan_inf_values(self):
        """Test compute_effect_size_fast with infinite/NaN values."""
        group1 = [0.1, np.nan, 0.3, 0.4]
        group2 = [0.15, 0.25, np.inf, 0.35]
        delta, a12 = compute_effect_size_fast(group1, group2)
        # mannwhitneyu propagates NaNs, so delta/a12 might be nan, but should not crash
        self.assertTrue(np.isnan(delta) or (-1.0 <= delta <= 1.0))
        self.assertTrue(np.isnan(a12) or (0.0 <= a12 <= 1.0))

    # ==========================================
    # 4. generate_all_outputs.py Stress Tests
    # ==========================================

    def test_generate_outputs_missing_results(self):
        """Test main generation when results dir is empty/missing."""
        # By passing a non-existent results directory, check_results_exist fails,
        # which triggers generate_mock_results.
        # To avoid writing a massive mock dataset (which takes a long time), we can mock
        # generate_mock_results and verify that main behaves correctly.
        with patch('scripts.generate_all_outputs.generate_mock_results') as mock_mock_gen, \
             patch('scripts.generate_all_outputs.generate_tables') as mock_tables, \
             patch('scripts.generate_all_outputs.generate_figures') as mock_figures:
            with patch('sys.argv', ['generate_all_outputs.py', '--results-dir', 'non_existent_dir']):
                generate_main()
            mock_mock_gen.assert_called_once_with('non_existent_dir')
            mock_tables.assert_called_once()
            mock_figures.assert_called_once()

    def test_generate_outputs_empty_compiled(self):
        """Test generate_tables and generate_figures when compiled files are empty."""
        tables_dir = os.path.join(self.temp_dir, 'tables')
        figures_dir = os.path.join(self.temp_dir, 'figures')
        
        # Write empty compiled files
        pd.DataFrame(columns=['Model', 'Target', 'Horizon', 'MAE_mean', 'MAE_std', 'RMSE_mean', 'RMSE_std',
                             'DA_mean', 'DA_std', 'PINAW_mean', 'PINAW_std', 'PICP_mean', 'PICP_std']).to_csv(
            os.path.join(self.temp_dir, 'compiled_32model_results.csv'), index=False
        )
        pd.DataFrame(columns=['Paradigm', 'Target', 'Horizon', 'MAE_mean', 'RMSE_mean', 'DA_mean', 'PINAW_mean', 'PICP_mean']).to_csv(
            os.path.join(self.temp_dir, 'compiled_32model_results_by_paradigm.csv'), index=False
        )
        # mcs_superior_set.csv is missing or empty
        # effect_size_matrix.csv is missing or empty

        # Call generate_tables and generate_figures
        generate_tables(self.temp_dir, "2026-07-17 00:00:00")
        generate_figures(self.temp_dir, "2026-07-17 00:00:00")

        # They should complete successfully and write empty table CSVs/LaTeX or return early without crashing.
        self.assertTrue(os.path.exists(os.path.join(tables_dir, 'table1_main_results_XANG.csv')))
        self.assertTrue(os.path.exists(os.path.join(tables_dir, 'table1_main_results_DAU.csv')))

    # ==========================================
    # 5. run_all_32models.py Stress Tests
    # ==========================================

    @patch('shutil.copytree')
    @patch('shutil.rmtree')
    @patch('subprocess.run')
    def test_run_all_dry_run_orchestration(self, mock_run, mock_rmtree, mock_copytree):
        """Test run_all_32models.py dry run path without actual subprocesses or folder deletions."""
        # Setup mock behavior
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch('sys.argv', ['run_all_32models.py', '--dry-run']), \
             patch('os.path.exists', return_value=True):
            run_all_main()
            
        # Should attempt to back up the directory
        mock_copytree.assert_called_once()
        # Should attempt to clean directories
        self.assertTrue(mock_rmtree.called)
        # Should launch generate_all_outputs.py (which manages mock results in dry run)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertIn('generate_all_outputs.py', args[0][1])

if __name__ == '__main__':
    unittest.main()
