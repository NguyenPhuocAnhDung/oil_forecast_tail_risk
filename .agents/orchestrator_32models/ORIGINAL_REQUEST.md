# Original User Request

## Request — 2026-07-17T23:08:55+07:00

Your identity: Pure Orchestrator (teamwork_preview_orchestrator).
Your workspace directory is: /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator_32models
Your task is to coordinate the upgrade of the Research OS for the GUM-Net paper based on the latest user request.
The request details are in: /data/quyhv/oil_forecast_tail_risk/.agents/ORIGINAL_REQUEST.md under the header "## Follow-up — 2026-07-17T16:08:07Z".

Requirements to fulfill:
1. Update `config.py` at the project root to include the new taxonomy registry SOTA_TAXONOMY_REGISTRY (32 models total), ALL_SOTA_BASELINES, GUM_NET_VARIANTS, SEEDS_EXTENDED, and HORIZON_TEMPORAL_CONFIG. Keep existing horizons and seeds.
2. Update the 5 Markdown reports in `docs/research_os/`:
   - `stage2_conceptual_gaps.md` (specifically `## CORE_RESEARCH_GAP_MATRIX` with the 22 SOTAs table, target distribution equation, Morphological Mismatch, and 5 research gaps)
   - `stage5_hypothesis_design.md` (specifically `## EXPERIMENTAL_ARCHITECTURE_BLUEPRINT` with expert, filter, generative/causal, routing layers mathematical descriptions, 4 RQs, and falsifiable hypotheses)
   - `stage7_baseline_taxonomy.md` (specifically `## BENCHMARK_TAXONOMY_MATRIX` with SOTA baseline matrix, R8 rule text verbatim, and python dispatch code)
   - `stage9_failure_diagnostics.md` (specifically `## POST_MORTEM_DIAGNOSTICS_REPORT` with anti-fabrication constraints, 4 groups of errors, and 2-phase protocol)
   - `stage10_econometric_validation.md` (specifically `## STATISTICAL_VALIDATION_VERDICT` with DM, MCS, effect size, and equations)
3. Implement `src/models/extended_sota.py` containing forward-pass implementations for the new SOTA models.
4. Implement `src/models/gumnet_family.py` containing the 10 variants of GUM-Net.
5. Update `get_model_instance` in `scripts/train_unified.py` to dispatch to the correct classes.
6. Create/update experimental scripts under `scripts/` (`run_all_32models.py`, `compile_32model_results.py`, `dm_test_32models.py`, `effect_size_32models.py`).
7. Create table and plot generation pipeline `scripts/generate_all_outputs.py`. Ensure tables and figures are correctly outputted under `results_v4/tables/` and `results_v4/figures/`.
8. Create `requirements_32models.txt` and `scripts/check_environment.py`.

Please make sure to:
- Write coordination files ONLY in your folder `/data/quyhv/oil_forecast_tail_risk/.agents/orchestrator_32models/`. Do not write code or documentation to this directory, only plans (`plan.md`), progress (`progress.md`), etc.
- Maintain academic integrity: no hardcoded statistical values in Stage 9.
- Use `self` or other subagent types from the subagent catalog (like `teamwork_preview_explorer` or `worker` or `reviewer` or `challenger`) to handle the detailed analysis, editing, and code writing.
- Update `progress.md` in your directory regularly so the Sentinel can monitor your progress. When complete, send a message to the Sentinel claiming victory.

## Critical Override — 2026-07-17T16:10:04Z

The user requested a full rerun from scratch.

Required changes in R6 and R7:
1. `scripts/run_all_32models.py` — FORCE RERUN MODE
   - Default `--force-rerun=True`.
   - When `--force-rerun=True`: Delete `results_v4/{model_name}/` for each model before running, no skipping.
   - When `--force-rerun=False`: use checkpoint-aware skip.
   - Backup: Copy `results_v4/` to `results_v4_backup_{timestamp}/` before deletion.
2. `scripts/compile_32model_results.py` — ONLY COLLECT NEW RESULTS
   - Add `--results-dir` and `--min-timestamp` parameters to filter `results.json` files with timestamp >= start of run.
3. `scripts/generate_all_outputs.py` — GENERATE FROM NEW RESULTS
   - All 8 figures and 4 tables must be generated from the new runs.
   - Add watermark/timestamp to each figure.
4. Pipeline execution order in `run_all_32models.py`:
   - Step 1: Backup `results_v4/`
   - Step 2: Clean `results_v4/` (keep folder structure)
   - Step 3: Run all 32 models × 7 horizons × seeds
   - Step 4: Call `compile_32model_results.py`
   - Step 5: Call `dm_test_32models.py`
   - Step 6: Call `effect_size_32models.py`
   - Step 7: Call `generate_all_outputs.py`

