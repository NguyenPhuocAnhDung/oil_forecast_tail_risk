## 2026-07-17T16:26:18Z

Your role is Worker for Milestone B.
Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/worker_msB.
Your task is to implement and update the 5 scripts under scripts/:
1. compile_32model_results.py
2. dm_test_32models.py
3. effect_size_32models.py
4. generate_all_outputs.py
5. run_all_32models.py

Please read the following documents for design, requirements, and codebase details:
- Synthesis Report: /data/quyhv/oil_forecast_tail_risk/.agents/sub_orch_msB/synthesis_report.md
- Lead Explorer Analysis: /data/quyhv/oil_forecast_tail_risk/.agents/explorer_msB_1/analysis.md
- Secondary Explorer Analysis: /data/quyhv/oil_forecast_tail_risk/.agents/explorer_msB_2/analysis.md
- Tertiary Explorer Analysis: /data/quyhv/oil_forecast_tail_risk/.agents/explorer_msB_3/analysis.md

Ensure all requirements are strictly satisfied, including:
- Force-rerun mode (--force-rerun flag defaulting to True) in run_all_32models.py.
- Backup of results_v4/ to results_v4_backup_{timestamp}/.
- Cleaning of results_v4/ (but preserve non-model/non-active protocol directories, only clean results_v4/walkforward/{model}/).
- In compile_32model_results.py, support --results-dir and --min-timestamp filtering against the results.json 'datetime' field. Robust PINAW calculation using 4*std(y_true). Grouping by paradigm using config.py's SOTA_TAXONOMY_REGISTRY.
- Corrected and studentized MCS bootstrap in dm_test_32models.py (with centering bug fix and speed optimization using pre-generated index matrix).
- Fast O(N log N) effect size using Mann-Whitney U rank statistic. Group 1 baseline absolute errors, Group 2 GUMNet absolute errors, positive effect size indicating GUMNet superiority.
- In generate_all_outputs.py, generate LaTeX/CSV tables (table1 to table4) and 300dpi PDF+PNG figures (fig1 to fig8) with timestamp/watermark in titles. Full mock data fallback generation support if actual results are missing.
- Verification command support: Verify your work by running:
  $env:GUMNET_TEST_MODE="1"
  python scripts/run_all_32models.py --force-rerun=True --dry-run (or with mock data/actual training test run) to check pipeline links.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please report back when you are finished, specifying the absolute paths of all created/updated scripts and the verification log.
