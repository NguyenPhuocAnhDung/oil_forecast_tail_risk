# Handoff Report — Lead Explorer for Milestone B

This report outlines the observations, logic, caveats, and conclusions from the codebase investigation regarding training/inference outputs, reusable components, and the implementation design of the 5 scripts under `scripts/` for Milestone B.

## 1. Observation
1. **`scripts/train_unified.py` (Training/Inference Output)**:
   - Line 393: `output_dir = os.path.join(RESULTS_DIR, protocol_name, model_name, f'{target_type}_H{horizon}_seed{seed}')`
   - Line 603: `with open(os.path.join(output_dir, 'results.json'), 'w') as f:`
   - Line 533: `all_errors.extend((true_prices - pred_prices).flatten().tolist())`
   - Line 601: `pred_df.to_csv(os.path.join(output_dir, 'predictions.csv'), index=False)`
   - Results are saved under `results_v4/{protocol}/{model}/{target}_H{horizon}_seed{seed}/results.json` containing a `"datetime"` field with UTC ISO format (e.g. `"2026-07-17T09:20:54.317139Z"`).
2. **`scripts/compile_results.py` (Multi-seed aggregation)**:
   - Lines 57-60:
     ```python
     dirpath = os.path.join(RESDIR, model, f'{target}_H{h}_seed{seed}')
     res_file = os.path.join(dirpath, 'results.json')
     pred_file = os.path.join(dirpath, 'predictions.csv')
     ```
3. **`scripts/dm_test_da.py` (Pairwise DM Test for DA)**:
   - Lines 57-59:
     ```python
     max_lag = min(h, int(np.floor(1.2 * n**(1/3))))
     max_lag = max(1, max_lag)
     ```
4. **`scripts/model_confidence_set.py` (Hansen MCS Bootstrap)**:
   - Lines 75-76:
     ```python
     p_val = 2 * min(np.mean(boot_means >= d_mean), np.mean(boot_means <= d_mean))
     ```
     where `boot_means` is obtained by bootstrapping `d = loss_i - loss_j` directly.
5. **`src/evaluation/statistical_tests.py` (Non-parametric Effect Size)**:
   - Lines 231-256 for Cliff's Delta:
     ```python
     for x in group1:
       for y in group2:
         if x > y:
           count += 1
         elif x < y:
           count -= 1
     ```
     which is an $O(N^2)$ nested loop computation.

## 2. Logic Chain
- **Output Directory Structure & Filter**: Based on `train_unified.py` lines 393 and 603, `compile_32model_results.py` must scan `results_v4/walkforward/{model}/` to locate `results.json` and verify the `"datetime"` field against `--min-timestamp` before aggregating.
- **Directional Accuracy (DA)**: From `train_unified.py` line 533, prediction rows in `predictions.csv` alternate by product chronologically. Thus, `DA` must be calculated by grouping by product (`df.groupby('product')`) and sorting by date to prevent cross-product sequence contamination.
- **MCS Bootstrap Bug & Correction**: Bootstrapping `d` directly yields `boot_means` centered around the sample mean `d_mean`. Consequently, testing how often they exceed `d_mean` or are less than `d_mean` yields a p-value of ~1.0 (from `model_confidence_set.py:75-76`), failing to reject the equal predictive accuracy null hypothesis. We must correct this by centering the bootstrap distribution: $\bar{d}^{*, b}_{\text{centered}} = \bar{d}^{*, b} - \bar{d}$. The p-value is the proportion of absolute centered bootstrap means exceeding the absolute observed mean: $p = \frac{1}{B} \sum I(|\bar{d}^{*, b} - \bar{d}| \ge |\bar{d}|)$.
- **MCS Computational Scaling**: Recalculating Newey-West HAC variance for 32 models ($32 \times 32$ pairs) over $B=1000$ iterations takes $O(B \cdot M^2 \cdot T)$, which is extremely slow. We optimize this by pre-generating circular block bootstrap indices once per target/horizon, and scaling studentized bootstrap statistics using the sample HAC standard error of the original series. This reduces complexity to $O(M^2 \cdot T + B \cdot M^2)$, allowing the MCS test to run in under a second.
- **Cliff's Delta & Vargha-Delaney A Optimization**: The $O(N^2)$ double loop in `statistical_tests.py:231` is a major performance bottleneck for large concatenated error series (e.g. 5 seeds $\times$ test days $\times$ 2 products). Using the Mann-Whitney U statistic rank sum ($A_{12} = U_1 / (n_1 n_2)$ and $\delta = 2 A_{12} - 1$) allows us to compute both effect sizes in $O(N \log N)$ time using Scipy.
- **Watermarking**: Matplotlib code from `plot_paper_figures.py` can be reused, but `generate_all_outputs.py` must append a running watermark string in the title (e.g. `[Run: 2026-07-17 23:20:18]`) to prove the figures are from the new runs.

## 3. Caveats
- No models were trained or evaluated as this is a read-only investigation.
- The default number of seeds is assumed to be 5 as declared in `config.py`.
- The circular block bootstrap length follows the $T^{1/4}$ rule.

## 4. Conclusion
1. The codebase paths, training, inference, and result saving configurations are thoroughly analyzed.
2. Pairwise DM test should employ Newey-West HAC variance and HLN corrections.
3. Hansen's MCS block bootstrap must center the bootstrap distribution under the null hypothesis, and is optimized using pre-generated indices and sample HAC variance scaling.
4. Cliff's Delta and Vargha-Delaney A can be computed in $O(N \log N)$ time using Mann-Whitney U statistic ranks.
5. The 5 orchestration and compilation scripts under `scripts/` have a complete implementation blueprint ready for execution.

## 5. Verification Method
- **Readiness check**: Run the checker to confirm all libraries and models are ready:
  ```bash
  python scripts/check_environment.py
  ```
- **Dispatcher & forward pass unit tests**: Run the unit test to verify that the 32+ SOTA baselines and GUM-Net variants compile and run a forward pass:
  ```bash
  python -m unittest tests/test_dispatch.py
  ```
- **Watermark & outputs check**: After running the pipeline, verify that all 8 figures are written to `results_v4/figures/` (PDF + PNG) with title watermarks, and 4 tables are generated in `results_v4/tables/` (CSV + LaTeX).
