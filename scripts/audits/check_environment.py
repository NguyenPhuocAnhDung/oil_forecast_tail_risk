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
            print(f"  [OK] {model:<20} : READY")
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
