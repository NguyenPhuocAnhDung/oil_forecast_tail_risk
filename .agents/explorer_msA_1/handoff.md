# Handoff Report: 32 Models Configuration Upgrade & Environment Specification

This handoff report summarizes the analysis of `config.py` and details the implementation design for the new taxonomy registry, extended seeds, horizon configs, `requirements_32models.txt`, and `scripts/check_environment.py`.

---

## 1. Observation

- **Project Root config.py**:
  - Located at `/data/quyhv/oil_forecast_tail_risk/config.py`.
  - Defines `ALL_HORIZONS = [1, 3, 5, 7, 10, 20, 60]` (lines 33).
  - Defines `SEEDS = [42, 123, 777, 2025, 9999]` (line 148).
  - Defines `BASELINES` list of 11 baselines (lines 50-53).
  - Contains `get_unified_config(target_type, horizon)` with a local `horizon_config` dictionary mapping horizons to `test_days`, `patience`, `min_epochs`, and `d_feat` (lines 59-77).
  
- **Orchestrator Request & Project Contract**:
  - Located at `/data/quyhv/oil_forecast_tail_risk/.agents/orchestrator_32models/PROJECT.md` and `.agents/ORIGINAL_REQUEST.md`.
  - Specifies adding `SOTA_TAXONOMY_REGISTRY` mapping 7 paradigms (`P1_Linear` to `P7_SparseMoE`) containing 33 SOTA baselines.
  - Specifies adding `GUM_NET_VARIANTS` containing 11 variants.
  - Specifies adding `SEEDS_EXTENDED = [42, 123, 777, 2025, 9999, 101, 888, 2023, 555, 1234]`.
  - Specifies adding `HORIZON_TEMPORAL_CONFIG` with new values for $H=7$ (`test_days: 150`, `min_epochs: 25`, `patience: 30`).
  
- **Requirements**:
  - Existing `requirements.txt` at project root defines basic PyTorch, ML, and plotting packages.
  - Missing specialized libraries for tensor permutation (`einops`), basis splines (`efficient-kan`), wavelets (`PyWavelets`), and causal graphs (`networkx`).

---

## 2. Logic Chain

1. **Alignment of Single Source of Truth (`config.py`)**:
   - To align with Requirement R1, `SOTA_TAXONOMY_REGISTRY`, `ALL_SOTA_BASELINES`, `GUM_NET_VARIANTS`, `SEEDS_EXTENDED`, and `HORIZON_TEMPORAL_CONFIG` must be declared as global module constants in `config.py`.
   - To ensure consistent execution and prevent parameter discrepancies across script pipelines (e.g. `train_unified.py` and downstream evaluation scripts), `get_unified_config` must retrieve training params from `HORIZON_TEMPORAL_CONFIG` instead of its hardcoded local dictionary.
   - For short vs long horizons, `d_feat` must remain adaptive: `d_feat: 64` for horizons $[10, 20, 60]$ (preventing convergence collapse due to low signal-to-noise ratios), and `d_feat: 128` for other horizons $[1, 3, 5, 7]$.

2. **Formulation of Requirements (`requirements_32models.txt`)**:
   - Extended models use multi-dimensional tensor reshapes, which require `einops`.
   - `GUMNet_Wavelet` and `GUMNet_Fusion` require PyWavelets (`pywt`) and Wavelet-KAN basis functions (`efficient-kan`).
   - `GUMNet_Graph` requires `networkx` to represent ST-GCN causal connections.
   - Econometric validators (`dm_test_32models.py`) require Newey-West HAC calculations from `statsmodels`.
   - Foundation models (`Chronos`, `TimesFM`, etc.) require HuggingFace Hub APIs (`transformers`, `huggingface_hub`, `accelerate`).
   - These are consolidated into `requirements_32models.txt`.

3. **Formulation of Environment Checker (`scripts/check_environment.py`)**:
   - The check script must verify import capability for each dependency (`import einops`, `import pywt`, etc.).
   - Model readiness is computed by checking if all library requirements for a given model map to available imports, warning the user of any missing blocks.

---

## 3. Caveats

- **Windows Compilers for Mamba/Selective Scan**: Compilation of `mamba-ssm` or `causal-conv1d` fails natively on Windows without heavy custom toolchains. Recommendation: the implementer agent should use pure PyTorch-native selective scan wrappers or random weight fallback wrappers for SSM-based models (`S_Mamba`, `MambaFormer`, `BiMamba`, `GUMNet_Mamba`) to ensure Windows compatibility without compiler issues.
- **Foundation Models Checkpoints**: The foundation models wrapper is recommended to support fallback random execution when weight checkpoints are offline or unavailable.

---

## 4. Conclusion

The config changes and environment checkers are formulated and analyzed. 
Applying the proposed changes will successfully establish a single source of truth for the 32 SOTA baselines and GUM-Net variants, and provide researchers with verification scripts to validate environment health before running trials.

---

## 5. Verification Method

To verify the integration:
1. **Config Validation**: Import `config` in python and print the values to verify:
   ```python
   import config
   assert len(config.ALL_SOTA_BASELINES) == 33
   assert len(config.GUM_NET_VARIANTS) == 11
   assert config.HORIZON_TEMPORAL_CONFIG[7]["test_days"] == 150
   ```
2. **Environment Validation**: Run the environment checker script:
   ```bash
   python scripts/check_environment.py
   ```
   Verify it successfully executes and outputs a clean readiness matrix.
