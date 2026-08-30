# Handoff Report — Secondary Explorer for Milestone B

This report summarizes the read-only investigation of the codebase's statistical/validation scripts, Cliff's Delta, Vargha-Delaney A effect sizes, and the metrics formulation for compiling 32 model results.

## 1. Observation
We observed the following files and code patterns in the repository:
1. **`scripts/model_confidence_set.py`**:
   - Computes the block bootstrap for the Model Confidence Set (MCS).
   - In lines 75-76, it computes the p-value:
     ```python
     p_val = 2 * min(np.mean(boot_means >= d_mean), np.mean(boot_means <= d_mean))
     ```
     where `boot_means` is obtained by block-bootstrapping the loss differentials `d = loss_i - loss_j` directly.
   - It runs the MCS test using $B = 499$ bootstrap replicates.
2. **`scripts/dm_test_da.py`**:
   - Computes the Diebold-Mariano test for directional accuracy.
   - In lines 57-65, it defines the lag truncation bandwidth for Newey-West HAC variance:
     ```python
     max_lag = min(h, int(np.floor(1.2 * n**(1/3))))
     max_lag = max(1, max_lag)
     ```
     where $h$ is the forecast horizon.
   - In lines 125-128, it concatenates error arrays across seeds:
     ```python
     g_err_concat = np.concatenate(all_g_errors)
     d_err_concat = np.concatenate(all_d_errors)
     dm_stat, p_val = dm_test_da(g_err_concat, d_err_concat, h=min(h, 5))
     ```
3. **`src/evaluation/statistical_tests.py`**:
   - Contains implementations for standard statistical tests including `diebold_mariano_test`, `cliffs_delta` (non-parametric effect size), `friedman_test`, `nemenyi_critical_distance`, `rank_instability_index`, and `protocol_sensitivity_score`.
   - In line 45, it uses the lag truncation bandwidth:
     ```python
     max_lag = min(horizon - 1, int(np.floor(1.2 * T**(1/3))))
     ```
   - In line 59, it implements the Harvey, Leybourne, and Newbold (1997) correction factor:
     ```python
     hln_factor = (T + 1 - 2 * horizon + (horizon / T) * (horizon - 1)) / T
     ```
   - In lines 231-271, `cliffs_delta(group1, group2)` implements Cliff's Delta using a nested double-loop of comparisons.
4. **`scripts/compute_advanced_metrics.py`**:
   - Computes average rank and prediction interval metrics.
   - In lines 96-99, it calculates PINAW:
     ```python
     covered = ((y_true >= q10) & (y_true <= q90)).mean() * 100
     width   = (q90 - q10).mean()
     y_range = y_true.std() * 4  # approx range
     pinaw   = width / (y_range + 1e-8)
     ```
5. **`scripts/train_unified.py`**:
   - In line 600, it writes unnormalized PIAW as PINAW to `results.json`:
     ```python
     results['metrics']['PINAW'] = round(float((q90_np - q10_np).mean()), 4)
     ```

## 2. Logic Chain
Based on these observations, we reasoned as follows:
1. **Model Confidence Set Bug**:
   - In `scripts/model_confidence_set.py`, bootstrapping `d` directly yields `boot_means` centered around `d_mean` (the sample mean).
   - Thus, checking how often the bootstrapped means exceed `d_mean` or are less than `d_mean` will always yield approximately 50%, resulting in a p-value of near 1.0 (since $2 \times \min(0.5, 0.5) = 1.0$).
   - This means the null hypothesis of equal predictive ability is never rejected, and no models are eliminated, making the MCS test useless.
   - **Correction**: We must center the bootstrap distribution under the null hypothesis ($E[d] = 0$) by subtracting the sample mean from the bootstrapped values: $\bar{d}^{*, b}_{\text{centered}} = \bar{d}^{*, b} - \bar{d}$. The p-value is then the proportion of absolute centered bootstrap means that exceed the absolute observed sample mean: $p = \frac{1}{B} \sum_{b=1}^B I(|\bar{d}^{*, b} - \bar{d}| \geq |\bar{d}|)$.
2. **Computational Scale-up for 32 Models**:
   - Running MCS with 1000 iterations for 32 models naively requires recalculating the Newey-West HAC variance for each bootstrap series. This would take $O(B \cdot M^2 \cdot T)$ computations ($1000 \times 1024 \times T$ operations per horizon/target), which is very slow.
   - **Optimization**: Under standard asymptotic theory, the bootstrap t-statistics can be studentized using the original series Newey-West HAC variance: $t_{i\cdot}^{*, b} \approx \frac{\bar{d}_{i\cdot}^{*, b} - \bar{d}_{i\cdot}}{\sqrt{\widehat{\text{Var}}_{HAC}(\bar{d}_{i\cdot})}}$. By pre-generating bootstrap indices once and using the original HAC standard error, the complexity is reduced to $O(M^2 \cdot T + B \cdot M^2)$, allowing execution in milliseconds.
3. **Cliff's Delta and Vargha-Delaney A**:
   - Cliff's Delta $\delta$ and Vargha-Delaney $A_{12}$ are non-parametric effect sizes measuring stochastic dominance.
   - Substituting $P(X_1 < X_2) = 1 - P(X_1 > X_2) - P(X_1 = X_2)$ into Cliff's Delta yields $\delta = 2 A_{12} - 1$, showing their exact linear relationship.
   - Computing Cliff's Delta naively via nested loops takes $O(n^2)$ time.
   - **Optimization**: By utilizing the relationship $A_{12} = \frac{U_1}{n_1 n_2}$ (where $U_1$ is the Mann-Whitney U statistic), we can calculate both metrics in $O(n \log n)$ time using Scipy's optimized ranking functions.
4. **Compilation Metrics Formulation**:
   - **MAE/RMSE**: Standard formulations computed over predictions and averaged across multi-seed files.
   - **Directional Accuracy (DA)**: Formulating a group-by product approach ensures robustness regardless of target dimensions.
   - **PINAW**: Normalization using the test range or $4 \times \text{Std}(y_{\text{true}})$ is required since `train_unified.py` outputs unnormalized widths.
   - **Temporal filtering**: Comparing `"datetime"` in `results.json` against `--min-timestamp` filters out old runs.

## 3. Caveats
- We assumed the number of seeds is fixed at 5 as defined in `config.py`.
- The analysis was conducted under read-only mode, so we did not execute the scripts or write the proposed implementations.
- The block bootstrap size was assumed to follow the standard $T^{1/4}$ rule, but other optimal block size selection methods (e.g. Politis and Romano, 1994) could be used if necessary.

## 4. Conclusion
1. Diebold-Mariano test with Newey-West HAC estimator can be performed using $q = \max\left(0, \min\left(h - 1, \lfloor 1.2 T^{1/3} \rfloor\right)\right)$ lag truncation. The Model Confidence Set bootstrap must use centered bootstrap distributions to correct the original script's bug, and can be optimized to run in milliseconds.
2. Cliff's Delta and Vargha-Delaney A are exactly linearly related and can be computed in $O(n \log n)$ time using the Mann-Whitney U statistic.
3. `compile_32model_results.py` should average point metrics, use group-by for DA, normalize PINAW by $4 \times \text{Std}(y_{\text{true}})$, and filter results using the `"datetime"` field.

## 5. Verification Method
1. **P-value Correction Validation**: Check if the bootstrap p-values in `dm_test_32models.py` reject the null hypothesis for obviously different series.
2. **Speed Benchmarking**: Verify that the optimized MCS bootstrap runs within 1-2 seconds for 32 models.
3. **Effect Size Identity**: Verify that the relation $A_{12} = \frac{\delta + 1}{2}$ holds for all computed output pairs.
4. **Range Normalization Verification**: Verify that the compiled PINAW results match the values in `results_v4/fair_gumnet_results.md`.
