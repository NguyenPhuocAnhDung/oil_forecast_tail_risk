# Handoff Report: Tertiary Explorer for Milestone B

## 1. Observation
1. **Model Registries**:
   - `config.py` lines 58-66 defines `SOTA_TAXONOMY_REGISTRY` mapping 7 paradigms to 33 models:
     ```python
     SOTA_TAXONOMY_REGISTRY = {
         "P1_Linear":      ["DLinear", "RLinear", "LTSF_Linear", "NBEATS", "NHits"],
         "P2_Transformer": ["PatchTST", "TFT", "Autoformer", "FedFormer", "Informer", "Reformer"],
         "P3_Inverted":    ["iTransformer", "UniTS", "TimeXer", "Crossformer", "CARD"],
         "P4_Frequency":   ["TimesNet", "TimeMixer", "TTM", "FITS", "CoST"],
         "P5_SSM":         ["TimeMachine", "S_Mamba", "MambaFormer", "BiMamba"],
         "P6_Foundation":  ["Chronos", "TimesFM", "Moirai", "Lag_Llama", "TEMPO", "GPT4TS"],
         "P7_SparseMoE":   ["Time_MoE", "Gated_TabNet"],
     }
     ```
   - `config.py` lines 69-73 defines `GUM_NET_VARIANTS` containing 11 variants:
     ```python
     GUM_NET_VARIANTS = [
         "GUMNet", "GUMNet_Mamba", "GUMNet_iTrans", "GUMNet_Wavelet",
         "GUMNet_Patch", "GUMNet_Fourier", "GUMNet_Diffusion", "GUMNet_Graph",
         "GUMNet_RL", "GUMNet_MoE_Sparse", "GUMNet_Fusion",
     ]
     ```
2. **Output Structure**:
   - `scripts/train_unified.py` line 393 writes model outputs to:
     `results_v4/{protocol}/{model_name}/{target_type}_H{horizon}_seed{seed}`
     Which contains `results.json`, `predictions.csv`, `errors.npy`, and `gating_weights.npy`.
3. **Environment and Mock Mode**:
   - `config.py` lines 165-170 includes mock-support scaling for verification:
     ```python
     if os.environ.get('GUMNET_TEST_MODE') == '1':
         cfg['max_epochs'] = 2
         cfg['min_epochs'] = 1
         cfg['patience'] = 1
         cfg['test_days'] = 10
     ```
4. **Critical Overrides**:
   - `.agents/orchestrator_32models/ORIGINAL_REQUEST.md` lines 31-54 contains specific rules:
     - `run_all_32models.py` must support a `--force-rerun` flag defaulting to `True` which deletes `results_v4/{model_name}/` after backing up.
     - Backup must copy `results_v4/` to `results_v4_backup_{timestamp}/` before deletion.
     - `compile_32model_results.py` must take `--results-dir` and `--min-timestamp` to only collect new results.
     - `generate_all_outputs.py` must output vector PDF and 300dpi PNG formats, embed watermarks in each figure, and support mock data.
5. **Figure and Table Specifications**:
   - `.agents/explorer_msB_1/analysis.md` lines 172-188 details the 8 required figures (`fig1` to `fig8`) and 4 required tables (`table1` to `table4`).

---

## 2. Logic Chain
1. **Force-Rerun Safety**:
   - In `run_all_32models.py`, setting `--force-rerun=True` (default) should only clean the model-specific directories under the active evaluation protocol (e.g. `results_v4/walkforward/{model}/`) rather than purging the root `results_v4/` folder. This preserves important non-model directories such as `evaluation_database/` and `figures/` (Observation 2 & 4).
2. **Watermarking for Provenance**:
   - To guarantee figures are generated from the latest run, `generate_all_outputs.py` must append the execution timestamp (e.g. `[Run: 2026-07-17 23:20:18]`) to the title or plot canvas using matplotlib text annotation (Observation 4).
3. **Fast Verification via Test Mode**:
   - Running the complete pipeline across all 44 models × 7 horizons × 5 seeds × 2 targets under walk-forward takes ~17 hours.
   - Setting the environment variable `GUMNET_TEST_MODE=1` forces the model configuration to train for a maximum of 2 epochs and test for 10 days. The pipeline run-through can therefore be completed in less than 3 minutes, proving scripts are linked correctly without spending excessive runtime (Observation 3).

---

## 3. Caveats
- **Offline Foundation Wrappers**: The 6 foundation models are initialized with randomized weights because no pre-trained weights are packaged with the codebase. They function as execution placeholders.
- **Windows System Paths**: Paths inside Python scripts must use `os.path.join` to handle backwards slash (`\`) separators on Windows correctly.

---

## 4. Conclusion
- The pipeline architecture, force-rerun cleanup, backup mechanics, and LaTeX/figure visualization specifications for Milestone B have been thoroughly analyzed. The design is complete, and the next step is programmatically writing the scripts to `scripts/`.

---

## 5. Verification Method
1. **Test Command**:
   Execute the pipeline in test mode using PowerShell:
   ```powershell
   $env:GUMNET_TEST_MODE="1"
   python scripts/run_all_32models.py --force-rerun=True
   ```
2. **Files to Inspect**:
   - Verify `results_v4_backup_{timestamp}/` is created.
   - Verify `results_v4/compiled_32model_results.csv` and `results_v4/compiled_32model_results_by_paradigm.csv` are compiled.
   - Verify `results_v4/tables/` contains `.tex` and `.csv` files for tables 1 to 4.
   - Verify `results_v4/figures/` contains PDF and PNG copies of figures 1 to 8, with watermark timestamps in their titles.
3. **Invalidation Conditions**:
   - Purging `results_v4` deletes `results_v4/evaluation_database/` or `results_v4/figures/`.
   - Figures or tables lack timestamp watermarks.
   - Script throws `FileNotFoundError` or shape mismatch exceptions during execution.
