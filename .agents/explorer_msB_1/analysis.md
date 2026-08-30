# Analysis Report: Codebase Exploration and Implementations Plan for Milestone B

## 1. Executive Summary
This report presents a comprehensive investigation of the GUM-Net-WF forecasting repository for Milestone B. It details the training, inference, and data-saving mechanics of `scripts/train_unified.py`, categorizes existing codebase utilities for reuse, and provides a structured, step-by-step implementation plan for the 5 orchestration and analysis scripts under `scripts/`. 

Key findings include:
- A systematic mapping of `train_unified.py` inputs, processing steps, and outputs (`results.json`, `predictions.csv`, `errors.npy`, `gating_weights.npy`).
- A reusable catalog identifying code blocks from `compile_results.py`, `compile_fair_results.py`, `dm_test_da.py`, `run_advanced_stats.py`, and `model_confidence_set.py`.
- An optimized rank-based $O(N \log N)$ algorithm for Cliff's Delta and Vargha-Delaney $A_{12}$ calculation, bypassing the $O(N^2)$ double loop bottleneck.
- A critical bug fix in the existing Model Confidence Set (MCS) bootstrap code, ensuring correct centering of the resampled loss differential distribution.
- A design for mock data support in visualization pipeline to enable testability under restricted execution constraints.

---

## 2. Deep Dive: `scripts/train_unified.py` Mechanics
The script `scripts/train_unified.py` is the central training and inference coordinator. It executes expanding-window walk-forward validation (and other evaluation protocols) for the designated models.

### 2.1. Feature Engineering and Data Splits
- **Features Loading**: Loads preprocessed daily time-series data from `data/processed/unified_data.csv`.
- **Target Products**: Maps to `XANG` (retail prices of `MG95` and `MG92`) and `DAU` (`DO 0.001%` and `DO 0.05%`).
- **Feature Partitioning**: Extends features with log-returns of benchmarks (`WTI_Daily`, `Brent_EU_Daily`), derived log ratio spreads (e.g. `Ratio_95_WTI`), temporal features (`Day_sin`, `Day_cos`), macroeconomic variables (`USD_Index`, `GPR`), and volatility indicators (`Vol_WTI_10d`).
- **Lookback Window & Horizon Temporal Config**: Dynamically adjusts input sequence lookback length (`seq_len`) and model parameters according to the horizon:
  - Horizons: `[1, 3, 5, 7, 10, 20, 60]`.
  - Lookback: `seq_len` ranges from `10` days (for $H=1, 3$) to `180` days (for $H=60$).
- **Walk-Forward Validation Protocol**:
  - Leverages the protocol dispatcher from `src.evaluation.protocols`.
  - Spits the dataset into expanding training windows. In each window, the model is trained from scratch on the training set, evaluated on the validation set for early stopping, and predicts the out-of-sample $H$-step future.

### 2.2. Training Loop & Instantiation
- PyTorch models (LSTM, GRU, GUM-Net, etc.) are trained using AdamW optimization.
- For GUM-Net variants, optimization targets the quantile pinball loss across the $Q_{10}, Q_{50}$ (median), and $Q_{90}$ quantiles, supplemented with a load-balancing router loss to avoid gate collapse.
- Model instance creation is handled by `get_model_instance(model_name, cfg)`, which supports standard baselines (`baselines.py`, `sota_baselines.py`), 26 extended SOTA models (`extended_sota.py`), and 10 GUM-Net family variants (`gumnet_family.py`).

### 2.3. Output Directories & Saved Artifacts
For a specific run `(model, target_type, horizon, protocol, seed)`, results are written to:
`results_v4/{protocol}/{model}/{target_type}_H{horizon}_seed{seed}/`

Within this folder, four key files are saved:
1. **`results.json`**:
   - Stores metadata and point metrics (`MSE`, `RMSE`, `MAE`, `MAPE`, `R2`, `DA`), plus prediction interval metrics (`PICP`, `PINAW`) for interval models.
   - Contains a `"datetime"` field representing the ISO UTC run completion timestamp (e.g. `"2026-07-17T09:20:54.317139Z"`).
2. **`predictions.csv`**:
   - Flat tabular structure storing columns: `date`, `product`, `true` (actual price), `pred` (point forecast).
   - For GUM-Net variants, includes `q10` and `q90` columns.
   - Values alternate by product name chronologically. For example, for `XANG`, the CSV contains rows alternating between `MG95` and `MG92`.
3. **`errors.npy`**:
   - Flat numpy array of residuals: $e_t = y_{\text{true}, t} - \hat{y}_{\text{pred}, t}$.
   - Elements are ordered chronologically and grouped by product.
4. **`gating_weights.npy`**:
   - Saved only for GUM-Net family variants.
   - Shape: `[num_windows, horizon, num_experts]` (where `num_experts = 3` representing CNN, GRU, and Wavelet-KAN branches).

---

## 3. Reusable Codebase Assets Catalog

We can reuse several components of the existing codebase to build the new Milestone B scripts:

| Target Script | Reuse Source File | Specific Functions / Logic to Reuse | Required Modifications |
|---|---|---|---|
| **`compile_32model_results.py`** | `scripts/compile_results.py` | Multi-seed directories scan loop, parsing `results.json`, loading `predictions.csv`. | Add `--results-dir` and `--min-timestamp` filters; parse the `"datetime"` JSON field; implement grouping by SOTA paradigms defined in `config.py`; export paradigm averages to a separate CSV. |
| | `scripts/compile_fair_results.py` | Product-specific metrics extraction by grouping/reshaping the flat `predictions.csv`. | Use pandas `groupby('product')` instead of naive reshaping to `(-1, 2)` to support arbitrary product dimensionalities robustly. |
| | `scripts/compute_advanced_metrics.py` | Prediction interval coverage probability (`PICP`) and normalized average width (`PINAW`). | Standardize normalization of PINAW using $4 \times \text{Std}(y_{\text{true}})$ rather than raw range to prevent distortion during extreme price spikes. |
| **`dm_test_32models.py`** | `scripts/dm_test_da.py` | Pairwise loop over models, directional accuracy correction function (`directional_correct`). | Generalize to accept all 32+ models; implement Newey-West HAC variance estimation with HLN small-sample correction. |
| | `src/evaluation/statistical_tests.py` | `diebold_mariano_test` wrapper with Newey-West HAC Bartlett kernel and HLN (1997) correction. | Align and group seed errors to avoid cross-product contamination in loss differentials. |
| | `scripts/model_confidence_set.py` | Hansen et al. (2011) Model Confidence Set (MCS) block bootstrap logic. | **Bug Fix**: Center the bootstrap distribution $\bar{d}^{*, b}_{\text{centered}} = \bar{d}^{*, b} - \bar{d}$ to calculate valid p-values. **Optimization**: Pre-generate bootstrap index matrix and reuse sample HAC standard errors to speed up execution. |
| **`effect_size_32models.py`** | `src/evaluation/statistical_tests.py` | Non-parametric effect size concepts, interpretation thresholds for Cliff's Delta and Vargha-Delaney $A_{12}$. | Replace the $O(N^2)$ double loop in `cliffs_delta` with Scipy's Mann-Whitney U statistic calculation to achieve $O(N \log N)$ execution. |
| **`generate_all_outputs.py`** | `scripts/plot_paper_figures.py` | Professional matplotlib plotting styles, figure layouts, dual-target formatting, and color schemes. | Adapt figures to generate the 8 specific plots with running watermark stamps in their titles. Add LaTeX template exporters for tables. |
| | `scripts/fill_tables_4_8.py` | LaTeX table generation template and formatting string functions. | Hook up LaTeX generators to load compiled CSVs directly instead of using hardcoded arrays. |

---

## 4. Implementation Specifications for the 5 Milestone B Scripts

This section outlines the detailed plan, architecture, and step-by-step logic for creating the five pipeline scripts under `scripts/`.

### 4.1. `scripts/run_all_32models.py`
An orchestrator script that manages the sequential execution of training for all SOTA baselines and GUM-Net variants, followed by downstream statistical compilation and plotting.

#### Key Features:
- **CLI Arguments**:
  - `--force-rerun` (boolean, default: `True`).
  - `--seeds` (list of integers, default: `SEEDS = [42, 123, 777, 2025, 9999]`).
  - `--horizons` (list of integers, default: `ALL_HORIZONS = [1, 3, 5, 7, 10, 20, 60]`).
  - `--targets` (list of strings, default: `['XANG', 'DAU']`).
- **Backup Mechanic**: Prior to any model-specific directory cleaning, copy the current `results_v4/` folder recursively to `results_v4_backup_{timestamp}/` using `shutil.copytree`.
- **Force Rerun Logic**: If `--force-rerun` is enabled, loop over all models and delete their corresponding target folders (e.g. `results_v4/walkforward/{model}/`) to ensure no checkpoint skipping occurs in `train_unified.py`. If `False`, rely on the check-skip flag.
- **Pipeline Flow**:
  1. Capture script start time: `start_timestamp = datetime.utcnow().isoformat() + 'Z'`.
  2. Backup `results_v4/`.
  3. Clean folders for the target models under `results_v4/walkforward/`.
  4. Loop over seeds, targets, horizons, and models (33 SOTA baselines in `ALL_SOTA_BASELINES` + 11 GUM-Net models in `GUM_NET_VARIANTS`), executing:
     `python scripts/train_unified.py --type {target} --model {model} --horizon {horizon} --seed {seed}` via `subprocess.run`.
     *(Note: If `GUMNET_TEST_MODE` env var is set to `1`, epochs are limited to 2 to verify pipeline execution quickly.)*
  5. Run `python scripts/compile_32model_results.py --min-timestamp {start_timestamp}`.
  6. Run `python scripts/dm_test_32models.py`.
  7. Run `python scripts/effect_size_32models.py`.
  8. Run `python scripts/generate_all_outputs.py`.

---

### 4.2. `scripts/compile_32model_results.py`
Aggregates metric files from individual runs, filtering out older historical results.

#### Key Features:
- **CLI Arguments**:
  - `--results-dir` (default: `results_v4`).
  - `--min-timestamp` (optional ISO timestamp string).
- **Filtering Logic**:
  - Loop over directories `results_v4/walkforward/{model}/{target}_H{horizon}_seed{seed}/`.
  - Locate `results.json`. Parse `"datetime"`. If the ISO completion date is less than `--min-timestamp`, exclude this directory.
- **Metrics Extraction**:
  - Average point metrics (`MAE`, `RMSE`, `R2`) across seeds.
  - Load `predictions.csv`, compute `DA` per product:
    `DA = mean(sign(true_diff) == sign(pred_diff)) * 100`.
  - Load GUM-Net variants' predictions, calculate prediction intervals:
    - `PICP` (coverage %): `mean(true >= q10 & true <= q90) * 100`.
    - `PINAW` (robust average width): `mean(q90 - q10) / (4 * std(true) + 1e-8)`.
- **Outputs**:
  - Save `results_v4/compiled_32model_results.csv` containing columns: `Model`, `Target`, `Horizon`, `MAE_mean`, `MAE_std`, `RMSE_mean`, `RMSE_std`, `DA_mean`, `DA_std`, `PINAW_mean`, `PINAW_std`, `PICP_mean`, `PICP_std`.
  - Group baselines using `SOTA_TAXONOMY_REGISTRY` paradigms, compute average metrics per paradigm, and save to `results_v4/compiled_32model_results_by_paradigm.csv`.

---

### 4.3. `scripts/dm_test_32models.py`
Performs econometric hypothesis testing using Diebold-Mariano and Hansen's Model Confidence Set.

#### Key Features:
- **Seed Alignment**:
  - For each `(model, target, horizon)`, load `predictions.csv` across all seeds.
  - Concat them to obtain a long, aligned time-series of predictions and actuals.
- **Pairwise DM Matrix**:
  - Compute a $32 \times 32$ matrix of DM p-values for each horizon.
  - Loss function: absolute error ($|e|$) for MAE, and squared error ($e^2$) for MSE.
  - HAC truncation lag: $q = \max\left(0, \min\left(h - 1, \lfloor 1.2 T^{1/3} \rfloor\right)\right)$.
  - Apply Harvey-Leybourne-Newbold small sample correction.
  - Save matrices to `results_v4/dm_pvalue_matrix_{horizon}.csv`.
- **Model Confidence Set (MCS) Algorithm**:
  - Null hypothesis of Equal Predictive Ability (EPA) evaluated at $\alpha = 0.10$.
  - **Centered Bootstrap**: Resample errors using circular block bootstrap. Subtract sample mean:
    `boot_means_centered = boot_means - sample_mean`
  - Compute two-sided bootstrap p-value:
    `p_val = mean(abs(boot_means_centered) >= abs(sample_mean))`
  - **Speed Optimization**: Pre-generate a single bootstrap index matrix of shape `[B, T]` ($B=1000$) per target/horizon. Scale bootstrapped means using the original HAC standard errors.
  - Save list of surviving models in the MCS superior set to `results_v4/mcs_superior_set.csv`.

---

### 4.4. `scripts/effect_size_32models.py`
Calculates practical significance metrics between GUM-Net models and SOTA baselines.

#### Key Features:
- **Optimized Rank-Based Computation**:
  - Combined sample size is large (5 seeds $\times$ test days $\times$ 2 products $\approx$ 3000 to 6000 values).
  - Use Mann-Whitney U statistic via `scipy.stats.mannwhitneyu(group1, group2)` to compute Vargha-Delaney $A_{12}$ in $O(N \log N)$ time:
    `A12 = U1 / (n1 * n2)`
    `delta = 2 * A12 - 1`
  - Group 1 ($X_1$) = Baseline absolute residuals ($|e_{\text{baseline}}|$).
  - Group 2 ($X_2$) = GUM-Net absolute residuals ($|e_{\text{GUMNet}}|$).
  - This ensures that if GUM-Net has smaller errors (superior), then $\delta > 0$ and $A_{12} > 0.5$.
- **Outputs**:
  - Save matrices of $\delta$ and $A_{12}$ values comparing `GUMNet_Fusion` (or other designated GUM-Net champion) against all 22 SOTAs to `results_v4/effect_size_matrix.csv`. Include Cliff's delta magnitude labels based on thresholds (`negligible`, `small`, `medium`, `large`).

---

### 4.5. `scripts/generate_all_outputs.py`
Generates the publication-ready tables and figures, with running watermarks.

#### Key Features:
- **Title Watermarks**: Include the execution timestamp (e.g. `[Run: 2026-07-17 23:20:18]`) in the title or a designated corner of each plot to verify the figures are newly generated.
- **Output Formats**: Save figures under `results_v4/figures/` in both vector PDF (for LaTeX manuscript compilation) and 300dpi PNG (for previews).
- **The 8 Required Figures**:
  1. `fig1_paradigm_rmse_barplot`: Grouped bar chart of RMSE by paradigm and horizon.
  2. `fig2_gumnet_family_radar`: Radar chart comparing point/interval metrics of the 10 GUM-Net variants.
  3. `fig3_failure_typology`: Stacked bar plot of the 4 error groups (Type A, B, C, D) per paradigm.
  4. `fig4_gating_dynamics`: Plot of gating weights ($w_1, w_2, w_3$) across the 5 GPR crisis periods.
  5. `fig5_quantile_coverage`: Plot of predictions against actuals showing the Q10-Q90 shaded bands for GUM-Net-Diffusion vs GUM-Net-Fusion.
  6. `fig6_dm_heatmap`: $32 \times 32$ heatmap of DM test p-values (in log-scale $-\log_{10}(p)$) to highlight statistical significance.
  7. `fig7_regime_error`: Line plot displaying prediction error dynamics in temporal windows surrounding the 5 GPR crisis events (pre-, during, post-crisis).
  8. `fig8_mcs_membership`: Binary heatmap showing MCS membership (in/out) for all models across the 7 horizons.
- **The 4 Required Tables**:
  - Save under `results_v4/tables/` in both CSV and LaTeX formats:
    1. `table1_main_results`: Detailed RMSE/MAE/DA metrics for 32 models × 7 horizons. Automatically find the best value (bold) and second-best (underlined) in each cell.
    2. `table2_mcs_results`: Heatmap-style table showing which models belong to the MCS superior set at each horizon.
    3. `table3_effect_size`: Vargha-Delaney $A_{12}$ and Cliff's $\delta$ of GUM-Net-Fusion vs 22 SOTAs.
    4. `table4_ablation`: Comparison of the 10 GUM-Net variants.
- **Mock Data Mode**:
  - If actual runs are missing (e.g., results directory is empty or incomplete), the script generates realistic mock datasets matching the expected structure. This ensures the visualization pipeline remains executable for validation.

---

## 5. Implementation Roadmap
The next step is to programmatically write these scripts to `scripts/` and verify their execution. The implementation order will proceed as follows:

```
+------------------------------------+
| 1. compile_32model_results.py      |  (aggregates outputs and computes base metrics)
+------------------------------------+
                  |
                  v
+------------------------------------+
| 2. dm_test_32models.py             |  (computes DM p-values and Hansen MCS)
+------------------------------------+
                  |
                  v
+------------------------------------+
| 3. effect_size_32models.py         |  (calculates fast Mann-Whitney effect size)
+------------------------------------+
                  |
                  v
+------------------------------------+
| 4. generate_all_outputs.py         |  (visualizes data and outputs LaTeX tables)
+------------------------------------+
                  |
                  v
+------------------------------------+
| 5. run_all_32models.py             |  (orchestrates and coordinates the full run)
+------------------------------------+
```

All scripts will be strictly tested under `GUMNET_TEST_MODE=1` to ensure correct integration, shape compatibility, and script outputs.
