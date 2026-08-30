# Handoff Report

## 1. Observation

- **HLN Correction Bug**:
  In `scripts/dm_test_32models.py` (lines 71-73), the formula for calculating `dm_hln` was:
  ```python
  # HLN small sample correction
  hln_factor = np.sqrt((T + 1 - 2 * horizon + (horizon * (horizon - 1)) / T) / T)
  dm_hln = dm_stat * hln_factor * np.sqrt(T)
  ```
  In comparison, `src/evaluation/statistical_tests.py` (lines 58-61) uses the standard implementation:
  ```python
  # Harvey, Leybourne, and Newbold (1997) small-sample correction
  hln_factor = (T + 1 - 2 * horizon + (horizon / T) * (horizon - 1)) / T
  hln_factor = max(hln_factor, 1e-8)  # safety
  dm_stat = dm_stat * np.sqrt(hln_factor)
  ```

- **Backup Safety Handling**:
  In `scripts/run_all_32models.py` (lines 52-56), the backup logic was catching errors but letting execution continue:
  ```python
  try:
      shutil.copytree(results_dir, backup_dir)
      print("Backup completed successfully.")
  except Exception as e:
      print(f"Warning: Backup failed: {e}. Continuing execution...")
  ```

- **Division-by-Zero Instability**:
  - In `scripts/compile_32model_results.py` (lines 45-48 and 70-72), calculations for `r2` and `pinaw` divided by `ss_tot + 1e-8` and `std_true + 1e-8` respectively, which could cause extreme or unstable values when `std_true` is extremely close to zero:
    ```python
    r2 = 1.0 - (ss_res / (ss_tot + 1e-8))
    # ...
    pinaw = np.mean(q90 - q10) / (4.0 * std_true + 1e-8)
    ```
  - In `scripts/generate_all_outputs.py` (lines 163 and 181), similar calculations were observed:
    ```python
    r2 = 1.0 - (np.sum((df_pred['true'] - df_pred['pred'])**2) / (np.sum((df_pred['true'] - np.mean(df_pred['true']))**2) + 1e-8))
    # ...
    results_json['metrics']['PINAW'] = float(2 * 1.28 * noise_scale / (4 * np.std(df_pred['true']) + 1e-8))
    ```

## 2. Logic Chain

- **HLN Correction Bug**:
  The Harvey-Leybourne-Newbold statistic is defined as:
  $$DM^* = DM \times \sqrt{ \frac{T + 1 - 2h + h(h-1)/T}{T} }$$
  The variable `hln_factor` in `scripts/dm_test_32models.py` is calculated as the square root of the ratio inside the square root, meaning it already includes the division by $T$ inside the square root:
  $$\text{hln\_factor} = \sqrt{ \frac{T + 1 - 2h + h(h-1)/T}{T} }$$
  Multiplying `dm_stat * hln_factor * np.sqrt(T)` effectively computes:
  $$DM \times \sqrt{ T + 1 - 2h + h(h-1)/T }$$
  This completely cancels out the $\frac{1}{\sqrt{T}}$ reduction intended by the small-sample correction, inflating the statistic by a factor of $\sqrt{T}$. Consequently, this inflated statistic leads to artificially deflated p-values (approaching 0). Removing `* np.sqrt(T)` aligns it with the mathematical definition and the correct implementation in `src/evaluation/statistical_tests.py`.

- **Backup Safety Handling**:
  Continuing pipeline execution after a backup failure can lead to silent data loss since Step 2 immediately clears active results. Raising a `RuntimeError` on backup failure terminates the script instantly, preventing any data erasure.

- **Division-by-Zero Instability**:
  If the actual prices series has zero or near-zero variance (e.g., constant prices `std_true < 1e-5`), division by a value close to 0 results in unstable metrics. Checking `if std_true < 1e-5` and setting `r2 = np.nan` and `pinaw = np.nan` handles this boundary condition safely and correctly.

## 3. Caveats

- Since execution permission requests timed out in this network/unattended environment, physical execution of the pipeline could not be completed here. However, logical verification and unit tests have been written to ensure correct behavior.

## 4. Conclusion

The pipeline issues have been resolved cleanly by:
1. Correcting the HLN formula in `scripts/dm_test_32models.py` to `dm_stat * hln_factor`.
2. Raising a `RuntimeError` on backup failure in `scripts/run_all_32models.py`.
3. Adding checks for `std_true < 1e-5` to set `r2` and `pinaw` to `np.nan` in `scripts/compile_32model_results.py` and `scripts/generate_all_outputs.py`.
4. Writing comprehensive unit tests in `tests/test_pipeline_fixes.py`.

## 5. Verification Method

To verify the changes, execute the following commands in the terminal:
1. Run the newly added unit tests:
   ```powershell
   python -m unittest tests/test_pipeline_fixes.py
   ```
2. Run the dry-run pipeline verification:
   ```powershell
   $env:GUMNET_TEST_MODE="1"
   python scripts/run_all_32models.py --force-rerun=True --dry-run
   ```
3. Inspect `results_v4/dm_pvalue_matrix_{horizon}.csv` to verify that p-values are no longer artificially deflated (close to 0.0 or e-16 due to the inflated test statistic).
