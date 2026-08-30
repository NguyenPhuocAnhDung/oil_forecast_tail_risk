# Codebase Configuration & Environment Setup Analysis

## Executive Summary
This report analyzes the existing `config.py` at the project root and provides structured recommendations to update it, supporting the expansion to 32 SOTA baseline models and 10 GUM-Net variants (11 GUM-Net family models in total). It also formulates the `requirements_32models.txt` and `scripts/check_environment.py` files to ensure safe and reproducible execution on Windows systems.

---

## 1. Analysis of `config.py` and Proposed Updates

### 1.1 Existing Layout
The current `config.py` defines:
- Target benchmarks and horizons (`ALL_HORIZONS = [1, 3, 5, 7, 10, 20, 60]`).
- Evaluation splits, default seeds (`SEEDS = [42, 123, 777, 2025, 9999]`), and lookbacks.
- Baseline models registry (`BASELINES = ['LSTM', 'GRU', 'BiLSTM_Attention', 'XGBoost', 'PatchTST', 'DLinear', 'TimesNet', 'iTransformer', 'TimeMixer', 'TFT', 'NHits']`).
- Unified feature configuration factory (`get_unified_config`), which returns model inputs and parameters.

### 1.2 Proposed Configuration Additions
To accommodate the expanded experimental matrix, `config.py` must include the following constants using Python-safe identifiers:
1. `SEEDS_EXTENDED`: 10 seeds to support extended robustness checks:
   ```python
   SEEDS_EXTENDED = [42, 123, 777, 2025, 9999, 101, 888, 2023, 555, 1234]
   ```
2. `SOTA_TAXONOMY_REGISTRY`: Maps 33 SOTA baselines into 7 paradigms:
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
3. `ALL_SOTA_BASELINES`: Flat list containing all SOTA models:
   ```python
   ALL_SOTA_BASELINES = [m for ms in SOTA_TAXONOMY_REGISTRY.values() for m in ms]
   ```
4. `GUM_NET_VARIANTS`: The 11 GUM-Net variants (10 modified versions + base model):
   ```python
   GUM_NET_VARIANTS = [
       "GUMNet", "GUMNet_Mamba", "GUMNet_iTrans", "GUMNet_Wavelet",
       "GUMNet_Patch", "GUMNet_Fourier", "GUMNet_Diffusion", "GUMNet_Graph",
       "GUMNet_RL", "GUMNet_MoE_Sparse", "GUMNet_Fusion",
   ]
   ```
5. `HORIZON_TEMPORAL_CONFIG`: Specifies horizon-specific hyperparameters, including updated parameters for $H=7$:
   ```python
   HORIZON_TEMPORAL_CONFIG = {
       1:  {"test_days": 100, "patience": 30, "min_epochs": 20},
       3:  {"test_days": 100, "patience": 30, "min_epochs": 20},
       5:  {"test_days": 100, "patience": 30, "min_epochs": 20},
       7:  {"test_days": 150, "patience": 30, "min_epochs": 25},
       10: {"test_days": 200, "patience": 25, "min_epochs": 30},
       20: {"test_days": 300, "patience": 30, "min_epochs": 40},
       60: {"test_days": 600, "patience": 35, "min_epochs": 50},
   }
   ```

### 1.3 Proposed Refactoring of `get_unified_config`
To align with the single source of truth, `get_unified_config` should query `HORIZON_TEMPORAL_CONFIG` for training parameters, while adaptively defining `d_feat` (64 for long horizons H10, H20, H60 to avoid convergence failure due to low signal-to-noise ratio, and 128 for short horizons H1-H7).

```python
def get_unified_config(target_type: str, horizon: int) -> dict:
    """
    Trả về cấu hình thống nhất cho 1 experiment.
    Cùng features, cùng seq_len, cùng test_days cho TẤT CẢ models.
    """
    cfg = {}

    # --- Hyperparameters theo horizon (matched to HORIZON_TEMPORAL_CONFIG) ---
    hcfg = HORIZON_TEMPORAL_CONFIG.get(horizon, {'test_days': 100, 'patience': 15, 'min_epochs': 20}).copy()
    
    # Adaptive feature dimensions based on horizon
    if horizon in [10, 20, 60]:
        hcfg['d_feat'] = 64
    else:
        hcfg['d_feat'] = 128
        
    cfg.update(hcfg)
    ...
```

---

## 2. Proposed Diff Patch for `config.py`

This patch inserts the SOTA registries, seeds, and horizon parameters, and links `get_unified_config` directly to the new constants:

```diff
--- config.py (Original)
+++ config.py (Proposed)
@@ -32,26 +32,66 @@
 ALL_HORIZONS = [1, 3, 5, 7, 10, 20, 60]
 
 # ============================================================
 # DATA SPLIT RATIOS
 # ============================================================
 SPLIT_RATIOS = {'train': 0.70, 'validation': 0.15, 'test': 0.15}
 DEFAULT_LOOKBACK = 120  # Input window length (business days)
 
 # ============================================================
 # CONFIDENCE INTERVAL & SIGNIFICANCE
 # ============================================================
 CONFIDENCE_LEVEL = 0.95
 SIGNIFICANCE_LEVEL = 0.05
 
 # ============================================================
 # BASELINES TO RUN (11 models + GUMNet)
 # ============================================================
 BASELINES = [
     'LSTM', 'GRU', 'BiLSTM_Attention', 'XGBoost', 'PatchTST', 'DLinear',
     'TimesNet', 'iTransformer', 'TimeMixer', 'TFT', 'NHits'
 ]
 
+# ============================================================
+# 32 SOTA BASELINES & GUM-NET VARIANTS TAXONOMY REGISTRY
+# ============================================================
+SOTA_TAXONOMY_REGISTRY = {
+    "P1_Linear":      ["DLinear", "RLinear", "LTSF_Linear", "NBEATS", "NHits"],
+    "P2_Transformer": ["PatchTST", "TFT", "Autoformer", "FedFormer", "Informer", "Reformer"],
+    "P3_Inverted":    ["iTransformer", "UniTS", "TimeXer", "Crossformer", "CARD"],
+    "P4_Frequency":   ["TimesNet", "TimeMixer", "TTM", "FITS", "CoST"],
+    "P5_SSM":         ["TimeMachine", "S_Mamba", "MambaFormer", "BiMamba"],
+    "P6_Foundation":  ["Chronos", "TimesFM", "Moirai", "Lag_Llama", "TEMPO", "GPT4TS"],
+    "P7_SparseMoE":   ["Time_MoE", "Gated_TabNet"],
+}
+ALL_SOTA_BASELINES = [m for ms in SOTA_TAXONOMY_REGISTRY.values() for m in ms]
+
+GUM_NET_VARIANTS = [
+    "GUMNet", "GUMNet_Mamba", "GUMNet_iTrans", "GUMNet_Wavelet",
+    "GUMNet_Patch", "GUMNet_Fourier", "GUMNet_Diffusion", "GUMNet_Graph",
+    "GUMNet_RL", "GUMNet_MoE_Sparse", "GUMNet_Fusion",
+]
+
+# ============================================================
+# HORIZON TEMPORAL CONFIG (Methodology-frozen settings)
+# ============================================================
+HORIZON_TEMPORAL_CONFIG = {
+    1:  {"test_days": 100, "patience": 30, "min_epochs": 20},
+    3:  {"test_days": 100, "patience": 30, "min_epochs": 20},
+    5:  {"test_days": 100, "patience": 30, "min_epochs": 20},
+    7:  {"test_days": 150, "patience": 30, "min_epochs": 25},
+    10: {"test_days": 200, "patience": 25, "min_epochs": 30},
+    20: {"test_days": 300, "patience": 30, "min_epochs": 40},
+    60: {"test_days": 600, "patience": 35, "min_epochs": 50},
+}
 
 # ============================================================
 # UNIFIED FEATURE SETS (FAIR COMPARISON)
 # Tất cả models dùng CÙNG feature set cho cùng (target_type, horizon)
 # ============================================================
 def get_unified_config(target_type: str, horizon: int) -> dict:
     """
     Trả về cấu hình thống nhất cho 1 experiment.
     Cùng features, cùng seq_len, cùng test_days cho TẤT CẢ models.
     """
     cfg = {}
 
-    # --- Hyperparameters theo horizon (matched to experiment.yaml) ---
-    horizon_config = {
-        1:  {'test_days': 100, 'patience': 30, 'min_epochs': 20, 'd_feat': 128},
-        3:  {'test_days': 100, 'patience': 30, 'min_epochs': 20, 'd_feat': 128},
-        5:  {'test_days': 100, 'patience': 30, 'min_epochs': 20, 'd_feat': 128},
-        7:  {'test_days': 100, 'patience': 30, 'min_epochs': 20, 'd_feat': 128},
-        10: {'test_days': 200, 'patience': 25, 'min_epochs': 30, 'd_feat': 64},
-        20: {'test_days': 300, 'patience': 30, 'min_epochs': 40, 'd_feat': 64},
-        60: {'test_days': 600, 'patience': 35, 'min_epochs': 50, 'd_feat': 64},
-    }
-    hcfg = horizon_config.get(horizon, {'test_days': 100, 'patience': 15, 'min_epochs': 20})
+    # --- Hyperparameters theo horizon (matched to HORIZON_TEMPORAL_CONFIG) ---
+    hcfg = HORIZON_TEMPORAL_CONFIG.get(horizon, {'test_days': 100, 'patience': 15, 'min_epochs': 20}).copy()
+    
+    # Adaptive feature dimensions based on horizon (avoiding convergence failure)
+    if horizon in [10, 20, 60]:
+        hcfg['d_feat'] = 64
+    else:
+        hcfg['d_feat'] = 128
+
     cfg.update(hcfg)
     
     # Add max epochs explicitly
     cfg['max_epochs'] = 200
@@ -145,5 +185,6 @@
 # ============================================================
 # EXPERIMENT SETTINGS
 # ============================================================
 SEEDS = [42, 123, 777, 2025, 9999]  # Multi-seed (5 seeds as agreed) cho confidence intervals
+SEEDS_EXTENDED = [42, 123, 777, 2025, 9999, 101, 888, 2023, 555, 1234]
 DEFAULT_SEED = 42
 BATCH_SIZE = 64
```

---

## 3. Formulation of `requirements_32models.txt`

To support all 32 SOTA baselines and GUM-Net variants on Windows, the environment must contain deep learning, tensor manipulation, and specialized modeling dependencies. Note that native compilation for selective scan operators (Mamba SSM) is problematic on Windows; thus, lightweight PyTorch-native SSM or offline wrappers are targeted, avoiding heavy native compiler dependencies.

### Proposed Content: `requirements_32models.txt`
```txt
# Core Deep Learning
torch>=2.0.0
torchvision
torchaudio

# Data Processing, Econometrics & Machine Learning
numpy>=1.22.0
pandas>=1.5.0
scikit-learn>=1.0.0
scipy>=1.10.0
xgboost>=1.7.0
statsmodels>=0.13.0

# Mathematical & Advanced Modeling
einops>=0.4.0
PyWavelets>=1.4.0
efficient-kan>=1.1.0
networkx>=3.0
ta>=0.10.0

# Foundation Models APIs & Integration
huggingface_hub>=0.16.0
transformers>=4.30.0
accelerate>=0.20.0

# Experiment Tracking & Document I/O
tqdm
python-docx
openpyxl
pyarrow

# Visualizations
matplotlib>=3.5.0
seaborn>=0.12.0
plotly>=5.10.0
streamlit>=1.20.0
```

---

## 4. Formulation of `scripts/check_environment.py`

This script maps each model name to its required packages and performs dry-import checks to identify blocked vs. ready models.

### Proposed Content: `scripts/check_environment.py`
```python
#!/usr/bin/env python3
"""
scripts/check_environment.py - Environment & Model Readiness Checker
===================================================================
Kiểm tra các thư viện đã cài đặt trong môi trường và báo cáo mức độ sẵn sàng
của 32 mô hình SOTA và 11 biến thể GUM-Net trên hệ điều hành Windows.
"""

import sys
import importlib

# Định nghĩa các thư viện cần kiểm tra và tên import tương ứng
REQUIRED_PACKAGES = {
    "torch": "PyTorch (Core Deep Learning)",
    "numpy": "NumPy (Math & Arrays)",
    "pandas": "Pandas (DataFrames)",
    "sklearn": "Scikit-Learn (ML & Metrics)",
    "xgboost": "XGBoost (Regression Baseline)",
    "einops": "Einops (Dimension Permutations)",
    "pywt": "PyWavelets (Wavelet Transformations)",
    "efficient_kan": "Efficient KAN (Basis Splines)",
    "networkx": "NetworkX (Causal ST-GCN Causal Graph)",
    "transformers": "Transformers (HuggingFace APIs)",
    "huggingface_hub": "HuggingFace Hub (Model Downloader)",
    "statsmodels": "Statsmodels (Econometric Tests)",
}

# Ánh xạ mô hình tới thư viện phụ thuộc
MODEL_DEPENDENCIES = {
    # Classical Baselines
    "LSTM": ["torch"],
    "GRU": ["torch"],
    "BiLSTM_Attention": ["torch"],
    "XGBoost": ["xgboost", "sklearn"],
    # P1_Linear (Linear Models)
    "DLinear": ["torch"],
    "RLinear": ["torch"],
    "LTSF_Linear": ["torch"],
    "NBEATS": ["torch"],
    "NHits": ["torch"],
    # P2_Transformer (Dense Attention)
    "PatchTST": ["torch", "einops"],
    "TFT": ["torch"],
    "Autoformer": ["torch", "einops"],
    "FedFormer": ["torch", "einops"],
    "Informer": ["torch", "einops"],
    "Reformer": ["torch", "einops"],
    # P3_Inverted (Channel Tokenization)
    "iTransformer": ["torch", "einops"],
    "UniTS": ["torch", "einops"],
    "TimeXer": ["torch", "einops"],
    "Crossformer": ["torch", "einops"],
    "CARD": ["torch", "einops"],
    # P4_Frequency (FFT/Spectral Domain)
    "TimesNet": ["torch"],
    "TimeMixer": ["torch"],
    "TTM": ["torch", "einops"],
    "FITS": ["torch"],
    "CoST": ["torch"],
    # P5_SSM (State Space Models)
    "TimeMachine": ["torch", "einops"],
    "S_Mamba": ["torch", "einops"],
    "MambaFormer": ["torch", "einops"],
    "BiMamba": ["torch", "einops"],
    # P6_Foundation (Pre-trained Foundation Models)
    "Chronos": ["torch", "transformers", "huggingface_hub"],
    "TimesFM": ["torch", "transformers", "huggingface_hub"],
    "Moirai": ["torch", "transformers", "huggingface_hub"],
    "Lag_Llama": ["torch", "transformers", "huggingface_hub"],
    "TEMPO": ["torch", "transformers"],
    "GPT4TS": ["torch", "transformers"],
    # P7_SparseMoE (Sparse Mixture of Experts)
    "Time_MoE": ["torch", "einops"],
    "Gated_TabNet": ["torch"],
    # GUM-Net Variants
    "GUMNet": ["torch"],
    "GUMNet_Mamba": ["torch", "einops"],
    "GUMNet_iTrans": ["torch", "einops"],
    "GUMNet_Wavelet": ["torch", "pywt", "efficient_kan"],
    "GUMNet_Patch": ["torch", "einops"],
    "GUMNet_Fourier": ["torch"],
    "GUMNet_Diffusion": ["torch"],
    "GUMNet_Graph": ["torch", "networkx"],
    "GUMNet_RL": ["torch"],
    "GUMNet_MoE_Sparse": ["torch"],
    "GUMNet_Fusion": ["torch", "einops", "pywt", "efficient_kan"],
}

def main():
    print("=" * 80)
    print(" ENVIRONMENT READINESS CHECKER FOR 32 MODELS & GUM-NET VARIANTS ")
    print("=" * 80)
    
    # 1. Kiểm tra các thư viện cài đặt
    package_status = {}
    missing_critical = []
    
    print("\n[1] Checking Packages:")
    for pkg, desc in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(pkg)
            package_status[pkg] = True
            print(f"  [+] {pkg:<16} : Installed ({desc})")
        except ImportError:
            package_status[pkg] = False
            print(f"  [-] {pkg:<16} : Missing ({desc})")
            if pkg in ["torch", "numpy", "pandas", "sklearn"]:
                missing_critical.append(pkg)
                
    if missing_critical:
        print("\n[!] CRITICAL ERROR: Key components missing: " + ", ".join(missing_critical))
        print("Please install them before running experiments.")
    
    # 2. Kiểm tra độ sẵn sàng của từng mô hình
    ready_count = 0
    blocked_models = []
    
    print("\n[2] Checking Model Readiness Matrix:")
    for model, deps in MODEL_DEPENDENCIES.items():
        missing_deps = [d for d in deps if not package_status.get(d, False)]
        if not missing_deps:
            ready_count += 1
            print(f"  [✓] {model:<20} : READY")
        else:
            blocked_models.append((model, missing_deps))
            print(f"  [X] {model:<20} : BLOCKED (Requires: {', '.join(missing_deps)})")
            
    # 3. Tổng kết
    total_models = len(MODEL_DEPENDENCIES)
    print("\n" + "=" * 80)
    print(f"SUMMARY: {ready_count}/{total_models} models are ready to run.")
    print("=" * 80)
    
    if blocked_models:
        print("\nTo enable blocked models, install the missing dependencies:")
        print("  pip install -r requirements_32models.txt")
        sys.exit(1)
    else:
        print("\nAll systems go! Ready for experimental pipeline runs.")
        sys.exit(0)

if __name__ == "__main__":
    main()
```
