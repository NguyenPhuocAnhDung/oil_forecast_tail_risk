# Synthesis Report: Milestone B Scripting & Validation Design

This report synthesizes the findings from the Lead, Secondary, and Tertiary Explorers for Milestone B of GUM-Net Research OS upgrade.

## 1. Codebase Overview and Assets to Reuse
- **results_v4/ structure**: `results_v4/walkforward/{model}/{target}_H{horizon}_seed{seed}/` containing:
  - `results.json`: metadata, metrics, ISO UTC timestamp `"datetime"`.
  - `predictions.csv`: flat table containing `date`, `product`, `true`, `pred`, plus `q10`, `q90` for GUM-Net models.
  - `errors.npy` and `gating_weights.npy` (only for GUM-Net).
- **Existing Scripts**: We can adapt logic from `scripts/compile_results.py`, `scripts/dm_test_da.py`, `scripts/model_confidence_set.py`, and `scripts/plot_paper_figures.py`.

## 2. Core Statistical Validation Specifications

### 2.1. Model Confidence Set (MCS) Bug Fix & Optimization
- **The Bug**: The original `model_confidence_set.py` did not center bootstrap loss differentials, yielding bootstrap means centered around the sample mean. Testing `boot_means >= sample_mean` always resulted in p-values near 1.0 (no models rejected).
- **The Fix**: Center the bootstrap distribution under the null hypothesis ($E[d] = 0$) by subtracting the sample mean:
  $$\bar{d}^{*, b}_{\text{centered}} = \bar{d}^{*, b} - \bar{d}$$
  Calculate p-value as the proportion of absolute centered bootstrap means exceeding the absolute sample mean:
  $$p = \frac{1}{B} \sum_{b=1}^B I(|\bar{d}^{*, b} - \bar{d}| \geq |\bar{d}|)$$
- **Optimization**: To avoid running Newey-West HAC variance estimation for all $B=1000$ replicates across 32 models, pre-generate circular block bootstrap index matrix `[B, T]` and scale bootstrap statistics with the original series Newey-West HAC standard error:
  $$t^{*, b} \approx \frac{\bar{d}^{*, b} - \bar{d}}{\sqrt{\widehat{\text{Var}}_{HAC}(\bar{d})}}$$
  This drops complexity from $O(B \cdot M^2 \cdot T)$ to $O(M^2 \cdot T + B \cdot M^2)$, allowing the script to execute in milliseconds.

### 2.2. Fast $O(n \log n)$ Effect Size Calculation
- Cliff's Delta ($\delta$) and Vargha-Delaney A ($A_{12}$) are linearly related:
  $$A_{12} = \frac{\delta + 1}{2}$$
- Instead of a slow $O(n^2)$ double loop, compute via the Mann-Whitney U statistic:
  $$A_{12} = \frac{U_1}{n_1 n_2}$$
  using `scipy.stats.mannwhitneyu(group1, group2)`.
- Group 1 is baseline absolute errors ($|e_{\text{baseline}}|$), Group 2 is GUMNet absolute errors ($|e_{\text{GUMNet}}|$). A positive $\delta$ and $A_{12} > 0.5$ indicate GUMNet superiority.

### 2.3. Metrics Compilation and Normalization
- Compute standard MAE, RMSE, and group-by product Directional Accuracy (DA).
- Normalize PINAW using robust scaling:
  $$PINAW_{\text{robust}} = \frac{\text{Mean}(q_{90} - q_{10})}{4 \times \text{Std}(y_{\text{true}}) + 1e-8}$$
- Filter results by ISO completion date in `results.json` field `"datetime"` being $\geq$ `min-timestamp`.

## 3. Implementation Plan for the 5 Scripts
The Worker will create/update:
1. `scripts/compile_32model_results.py`: Multi-seed metrics compiler with timestamp filtering.
2. `scripts/dm_test_32models.py`: Pairwise DM tests and optimized MCS.
3. `scripts/effect_size_32models.py`: Fast Cliff's Delta and Vargha-Delaney A.
4. `scripts/generate_all_outputs.py`: Generates the 4 tables and 8 watermarked figures, with mock data generation fallback.
5. `scripts/run_all_32models.py`: Backup results, clean active folders, run models via subprocess, and invoke downstream scripts sequentially.
