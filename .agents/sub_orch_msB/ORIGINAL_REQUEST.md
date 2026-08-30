# Original User Request

## 2026-07-17T16:20:18Z

You are a Sub-orchestrator (archetype teamwork_preview_orchestrator).
Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/sub_orch_msB.
Your mission is to coordinate Milestone B: Scripts and Pipeline.
Your scope:
Create or update the following experimental and validation scripts under scripts/:
1. run_all_32models.py:
   - Orchestrates the training/inference of 32 models (all SOTA baselines + GUM-Net variants) across 7 horizons and seeds.
   - Support command line arguments: --paradigm, --horizon, --seeds, --dry-run.
   - CRITICAL REQUIREMENT (Force Rerun Mode): Must have a flag --force-rerun defaulting to True.
     When --force-rerun=True: delete all results_v4/{model_name}/ of each model before running (do not skip any run even if checkpoints exist).
     When --force-rerun=False: use checkpoint-aware skip (for resume case).
     Before deleting, copy results_v4/ to results_v4_backup_{timestamp}/.
   - Pipeline execution order in run_all_32models.py:
     Step 1: Backup results_v4/ to results_v4_backup_{timestamp}/.
     Step 2: Clean results_v4/ (keep folder structure).
     Step 3: Run all 32 models × 7 horizons × seeds.
     Step 4: Call compile_32model_results.py to aggregate.
     Step 5: Call dm_test_32models.py to perform testing.
     Step 6: Call effect_size_32models.py to compute effect size.
     Step 7: Call generate_all_outputs.py to generate plots and tables.
2. compile_32model_results.py:
   - Aggregates results.json of the 32 models into a DataFrame.
   - Computes metrics: MAE, RMSE, DA, and PINAW.
   - Outputs: compiled_32model_results.csv and compiled_32model_results_by_paradigm.csv.
   - CRITICAL REQUIREMENT (New Results Only): Add parameters --results-dir (default results_v4/) and --min-timestamp. Filter results.json files with timestamp >= min-timestamp to ensure only new results are aggregated.
3. dm_test_32models.py:
   - Performs Diebold-Mariano (DM) test with Newey-West HAC estimator + MCS (Model Confidence Set) bootstrap 1000 iterations for 32 models × 7 horizons.
   - Outputs: dm_pvalue_matrix_{horizon}.csv and mcs_superior_set.csv.
4. effect_size_32models.py:
   - Calculates Cliff's Delta and Vargha-Delaney A effect size.
   - Outputs: effect_size_matrix.csv.
5. generate_all_outputs.py:
   - Generates tables: table1_main_results, table2_mcs_results, table3_effect_size, table4_ablation (under results_v4/tables/).
   - Generates figures: fig1 to fig8 (under results_v4/figures/). Ensure the figures are PDF + PNG 300dpi, IEEE/Elsevier compatible.
   - CRITICAL REQUIREMENT: Generate figures from the new results of the 32 models. Add a watermark/timestamp in the title of each figure (e.g. "Run: [timestamp]").
   - Must run successfully with mock/simulated data when real results are not yet fully generated.

Run the Explorer -> Worker -> Reviewer cycle to implement and verify these scripts. Make sure that all scripts are thoroughly tested. Your parent is d5f5707c-d383-4212-a14c-d6c762312691. Report back once Milestone B is complete.
