# Scope: Milestone B: Scripts and Pipeline

## Architecture
- `scripts/run_all_32models.py`: Runs/orchestrates all 32 models, backups/cleans directories, calls subsequent scripts.
- `scripts/compile_32model_results.py`: Aggregates results.json files with timestamp filtering, computes MAE, RMSE, DA, PINAW.
- `scripts/dm_test_32models.py`: Performs Diebold-Mariano tests and MCS bootstrap.
- `scripts/effect_size_32models.py`: Calculates Cliff's Delta and Vargha-Delaney A effect size.
- `scripts/generate_all_outputs.py`: Generates LaTeX/Markdown tables (table1 to table4) and figures (fig1 to fig8) with title watermarks, support mock data.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Explore | Examine scripts/train_unified.py, model configs, and existing metrics calculation to match interfaces. | none | PLANNED |
| 2 | Implement scripts | Create or update compile_32model_results.py, dm_test_32models.py, effect_size_32models.py, generate_all_outputs.py, run_all_32models.py | Milestone 1 | PLANNED |
| 3 | Verification | Run tests and validation on the complete pipeline (mock and real) | Milestone 2 | PLANNED |
| 4 | Audit & Forensic | Run Forensic Auditor to ensure no cheating, hardcoding, or bypasses | Milestone 3 | PLANNED |

## Interface Contracts
- `train_unified.py` outputs results into `results_v4/{model_name}/results.json` containing metrics and/or raw forecasts.
- `compile_32model_results.py` takes `--results-dir` and `--min-timestamp` and produces `compiled_32model_results.csv` and `compiled_32model_results_by_paradigm.csv`.
- `dm_test_32models.py` takes compiled results and generates `dm_pvalue_matrix_{horizon}.csv` and `mcs_superior_set.csv`.
- `effect_size_32models.py` generates `effect_size_matrix.csv`.
- `generate_all_outputs.py` generates figures in `results_v4/figures/` (PDF + PNG 300dpi) and tables in `results_v4/tables/` with run timestamp watermark.
