## 2026-07-17T16:54:11Z
Your role is Pipeline Robustness Fix Worker for Milestone B.
Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/worker_msB_robustness.
Your task is to fix the following robustness vulnerabilities identified by the Challenger:

1. In scripts/dm_test_32models.py:
   - Guard against T = 0 or M = 0 in Hansen's MCS block bootstrap selection:
     At the start of `run_mcs(L, alpha, B, horizon)`, check `if T == 0 or M == 0: return list(range(M)), {i: 1.0 for i in range(M)}`.
   - Implement index-based alignment when loading predictions to prevent broadcast ValueErrors if prediction lengths vary across models:
     In `main()` where `model_errors` and `model_preds` are loaded (around lines 242-270):
     - For each model, read predictions.csv, assign a 'seed' column based on the run folder name (e.g. Parts of the run_name split by '_').
     - Set the DataFrame index to ['date', 'product', 'seed'] and deduplicate.
     - Find the common index intersection across all models.
     - Slice each model's DataFrame to only keep rows in the common index intersection, sort the index, and then extract the prediction and error values.

2. In scripts/generate_all_outputs.py:
   - Guard against empty DataFrames in `generate_tables`:
     In `generate_tables`, after calling `df_tab = pd.DataFrame(table_rows)`, check if `df_tab.empty`. If it is, construct a DataFrame with the expected columns (Model, and H{h}_MAE, H{h}_RMSE, H{h}_DA for each h) so that downstream pivoting/formatting does not throw KeyErrors like 'H1_MAE'.

After making these modifications, execute the stress test suite and the pipeline fixes unit tests to verify that they now pass perfectly:
python -m unittest tests/test_pipeline_fixes.py
python -m unittest tests/test_pipeline_stress.py

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please write your handoff report to handoff.md in your directory and report back.
