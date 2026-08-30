## 2026-07-17T16:39:53Z
Your role is Pipeline Fix Worker for Milestone B.
Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/worker_msB_fix.
Your task is to fix the following issues in the scripts under scripts/:

1. Correct the Harvey-Leybourne-Newbold (HLN) correction bug in scripts/dm_test_32models.py:
   - In the function `diebold_mariano_test` (around line 73), the formula for `dm_hln` is currently:
     `dm_hln = dm_stat * hln_factor * np.sqrt(T)`
   - This contains an extra `* np.sqrt(T)` multiplier which artificially inflates the statistic.
   - Correct it to:
     `dm_hln = dm_stat * hln_factor`
   - Verify that this aligns with the correct implementation in `src/evaluation/statistical_tests.py`.

2. Improve backup failure safety in scripts/run_all_32models.py:
   - In Step 1 (the backup process), if the backup fails, the script currently prints a warning and continues to Step 2 (which clears active results), risking permanent data loss.
   - Modify the `except` block so that if the backup fails, it raises an exception or exits the script with an error instead of silently continuing.

3. Prevent division-by-zero instability in scripts/compile_32model_results.py and scripts/generate_all_outputs.py:
   - If the standard deviation of actual prices (`std_true` or `ss_tot` in R2) is zero or very close to zero (e.g., < 1e-5), division will fail or result in unstable values.
   - Add a check to handle this case gracefully (e.g. if `std_true < 1e-5`, set robust PINAW or other normalized values to np.nan or 0.0, and similarly for R2).

After making these modifications, verify that the verification pipeline still runs successfully:
$env:GUMNET_TEST_MODE="1"
python scripts/run_all_32models.py --force-rerun=True --dry-run

And check that the generated p-values in dm_pvalue_matrix_{horizon}.csv are now mathematically correct and not artificially deflated.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please write your handoff report to handoff.md in your directory and report back.
