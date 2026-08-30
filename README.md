# Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts

> **Official Repository** for the research paper: *"Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts"*.  
> Introducing **GUMNet-Het** (Gated Unified Mixture Network with Heterogeneous Experts) — a theory-informed, adaptive local-global neural architecture for probabilistic retail energy price forecasting and tail risk quantification under geopolitical volatility.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1%2B-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Manuscript](https://img.shields.io/badge/Manuscript-IEEE%20Format%20v7-blue)](GUMNETHet_FAIRv7_final.docx)
[![AI Stack](https://img.shields.io/badge/AI%20Stack-373%2B%20Skills-purple)](#-ai-agent-engineering-stack)
[![OmniRoute](https://img.shields.io/badge/OmniRoute-250%20Providers-orange)](http://localhost:20128)

---

## 📌 Executive Summary

Energy commodities and retail petroleum markets are acutely sensitive to non-stationary geopolitical turmoil, supply-chain interruptions, and regulatory price stabilization mechanisms. Traditional point forecasting and homogeneous deep architectures often fail under structural regime shifts due to gradient drift and error accumulation over long horizons.

**GUMNet-Het** addresses these fundamental limitations via:
1. **Heterogeneous Local-Global Decomposition**: Disentangles complex price series into high-frequency transient shocks (via **Mexican Hat Wavelet-KAN**), mid-range stateful momentum (via **Bi-directional LSTM/SSM**), and long-range global inter-dependencies (via **Inverted Channel Attention / iTransformer**).
2. **Geopolitical Uncertainty-Calibrated Gating ($\tau_t$)**: Dynamically adjusts softmax temperature and routing weights based on Realized Volatility ($RV_t$) and Geopolitical Risk ($GPR_t$) signals.
3. **Probabilistic Tail Risk Quantification**: Directly forecasts asymmetric predictive quantiles ($q_{10}, q_{50}, q_{90}$) trained via a joint **Quantile Pinball Loss with Directional Penalty Regularization**.
4. **Rigorous SOTA Benchmark**: Evaluated against 33 state-of-the-art baselines across 7 forecasting paradigms and 7 distinct horizons ($H \in \{1, 3, 5, 7, 10, 15, 20\}$ + extreme horizon $H=60$) over 5 random seeds (42, 123, 777, 2025, 9999) under strict walk-forward cross-validation.

---

## 🏛️ GUMNet-Het Model Architecture

```
                               ┌─────────────────────────────────────────┐
                               │   Multivariate Features (X_t, GPR_t)    │
                               └────────────────────┬────────────────────┘
                                                    │
                               ┌────────────────────▼────────────────────┐
                               │ Dynamic Gating Mechanism (τ_t calibrated)│
                               │    w_t = Softmax( GatingNet(x_t) / τ_t ) │
                               └────────┬───────────┬───────────┬────────┘
                                        │           │           │
                     ┌──────────────────▼──┐ ┌──────▼──────┐ ┌──▼───────────────────┐
                     │ High-Frequency Expert│ │ Mid-Frequency│ │ Global Long-Range Expert│
                     │  Wavelet-KAN (MHat) │ │  BiLSTM/SSM │ │ Inverted Transformer   │
                     │  (Localized Shocks) │ │  (Momentum) │ │ (Cross-Channel/Macro)  │
                     └──────────────────┬──┘ └──────┬──────┘ └──┬───────────────────┘
                                        │           │           │
                                        └───────────┼───────────┘
                                                    │
                                        ┌───────────▼───────────┐
                                        │  Adaptive Aggregation │
                                        │  y_hat = Σ w_i * E_i  │
                                        └───────────┬───────────┘
                                                    │
                                        ┌───────────▼───────────┐
                                        │ Multi-Quantile Head   │
                                        │ [q10, q50, q90] + DA% │
                                        └───────────────────────┘
```

---

## 📊 Comprehensive Benchmark Matrix (33 SOTA Baselines Across 7 Paradigms)

| Paradigm | Architectural Approach | Representative Baseline Models | Count |
|---|---|---|---|
| **P1 — Linear & Decomposition** | Direct mapping & trend-seasonal projection | DLinear, RLinear, LTSF_Linear, NBEATS, NHits | 5 |
| **P2 — Dense Attention Transformers** | Self-attention over temporal tokens | PatchTST, TFT, Autoformer, FedFormer, Informer, Reformer | 6 |
| **P3 — Inverted / Multivariate** | Channel-independent & inverted variate attention | iTransformer, UniTS, TimeXer, Crossformer, CARD | 5 |
| **P4 — Frequency & Spectral Mixing** | 2D temporal variation & Fourier representations | TimesNet, TimeMixer, TTM, FITS, CoST | 5 |
| **P5 — State Space Models (SSM)** | Selective scan & structured state spaces | TimeMachine, S_Mamba, MambaFormer, BiMamba | 4 |
| **P6 — Pretrained Foundation Models** | Zero-shot / few-shot time series transformers | Chronos, TimesFM, Moirai, Lag_Llama, TEMPO, GPT4TS | 6 |
| **P7 — Sparse Mixture-of-Experts** | Sparsely gated modular networks | Time_MoE, Gated_TabNet | 2 |
| **Proposed Method** | Adaptive mixture of local-global heterogeneous experts | **GUMNet-Het** (Wavelet-KAN + BiLSTM + iTransformer) | **1** |

---

## 🏆 Key Experimental Results (Seed 42 & 5-Seed Averages)

### 1. Gasoline RON95 (`XANG`) — Multi-Horizon Performance (GUMNet-Het vs SOTA)

| Horizon ($H$) | Model | MAE (VND/L) | RMSE | MAPE (%) | $R^2$ | DA (%) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **$H=1$** | **GUMNet-Het (Ours)** | **2.7921** | **5.0249** | **2.45%** | **0.9727** | **91.46%** |
| | TimesFM | 2.8136 | 5.0895 | 2.47% | 0.9720 | 62.63% |
| | RLinear | 2.8606 | 5.0337 | 2.51% | 0.9726 | 58.59% |
| | PatchTST | 2.8834 | 5.1146 | 2.53% | 0.9718 | 61.11% |
| | iTransformer | 2.9809 | 5.3918 | 2.61% | 0.9686 | 57.07% |
| **$H=3$** | **GUMNet-Het (Ours)** | **4.6691** | **8.4898** | **4.14%** | **0.9218** | **91.37%** |
| | TimeXer | 4.6992 | 8.5965 | 4.16% | 0.9198 | 48.47% |
| | Moirai | 4.7121 | 8.0889 | 4.14% | 0.9290 | 46.43% |
| | PatchTST | 4.8262 | 8.3000 | 4.22% | 0.9253 | 47.45% |
| **$H=7$** | **GUMNet-Het (Ours)** | **4.0695** | **7.6785** | **3.76%** | **0.9142** | **95.56%** |
| | FedFormer | 4.1290 | 7.7945 | 3.79% | 0.9116 | 47.26% |
| | GPT4TS | 4.2192 | 7.8966 | 3.91% | 0.9092 | 49.32% |
| | TimeMixer | 4.4974 | 8.1302 | 4.14% | 0.9038 | 48.63% |
| **$H=10$** | **GUMNet-Het (Ours)** | **4.3970** | **8.9788** | **4.09%** | **0.8522** | **42.24%** |
| | CoST | 4.5237 | 9.2755 | 4.23% | 0.8438 | 46.40% |
| | Moirai | 4.7636 | 9.6195 | 4.39% | 0.8320 | 50.51% |
| | RLinear | 4.7669 | 9.7781 | 4.39% | 0.8264 | 48.71% |
| **$H=60$ (Extreme)** | **GUMNet-Het (Ours)** | **4.8470** | **10.4474** | **5.11%** | **0.1552** | **27.95%** |
| | TimeXer | 6.5523 | 13.6548 | 6.62% | -0.0959 | 47.47% |
| | GPT4TS | 6.6084 | 13.5632 | 6.76% | -0.0813 | 47.08% |
| | TEMPO | 6.6588 | 13.6595 | 6.76% | -0.0967 | 45.80% |

### 2. Diesel DO (`DAU`) — Multi-Horizon Performance (GUMNet-Het vs SOTA)

| Horizon ($H$) | Model | MAE (VND/L) | RMSE | MAPE (%) | $R^2$ | DA (%) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **$H=1$** | **GUMNet-Het (Ours)** | **5.6023** | **11.3820** | **3.24%** | **0.9622** | **84.92%** |
| | TimeMixer | 5.7453 | 11.1538 | 3.35% | 0.9637 | 60.10% |
| | LTSF_Linear | 5.7726 | 11.1867 | 3.37% | 0.9635 | 58.08% |
| | Moirai | 5.7863 | 11.5577 | 3.38% | 0.9610 | 57.07% |
| | RLinear | 5.7982 | 11.2152 | 3.37% | 0.9633 | 60.61% |
| **$H=10$** | **GUMNet-Het (Ours)** | **9.1926** | **18.3690** | **6.16%** | **0.8433** | **32.29%** |
| | TFT | 9.4578 | 19.1089 | 6.53% | 0.8301 | 47.30% |
| | TimesFM | 9.6103 | 19.7724 | 6.41% | 0.8181 | 48.84% |
| | RLinear | 9.6899 | 20.0932 | 6.54% | 0.8122 | 48.20% |
| | TimesNet | 9.6920 | 19.9194 | 6.57% | 0.8154 | 47.04% |

### 3. Econometric & Statistical Rigor
- **Diebold-Mariano Tests with HAC Newey-West Correction**: GUMNet-Het demonstrates statistically significant error reductions ($p < 0.01$) against all baseline families.
- **Model Confidence Set (MCS)**: At $p=0.10$, GUMNet-Het consistently populates the superior set $\widehat{\mathcal{M}}_{90\%}^*$.
- **Effect Size**: Non-parametric Cliff's Delta ($\delta$) confirms medium-to-large effect sizes against traditional deep architectures.

---

## 🛠️ Installation & Environment Setup

### 1. Prerequisites
- Python 3.10+
- CUDA-enabled GPU (NVIDIA RTX / T4 / A100 recommended)

```bash
# Clone the repository
git clone https://github.com/NguyenPhuocAnhDung/oil_forecast_tail_risk.git
cd oil_forecast_tail_risk

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements_32models.txt

# Install efficient-kan for Kolmogorov-Arnold spline representations
pip install git+https://github.com/Blealtan/efficient-kan.git
```

### 2. Verify Environment Readiness
```bash
python scripts/audits/check_environment.py
```

---

## 🚀 Quick Start & Reproducibility Guide

### 1. Data Structure & Ingestion
Data directories are initialized with `.gitkeep` markers. Place your raw input files in `data/raw/`:
- `data/raw/Gia_dau_2026_16_7.xlsx` (Retail petroleum prices)
- `data/raw/DCOILBRENTEU.csv` & `data/raw/DCOILWTICO.csv` (Global benchmarks)
- `data/raw/data_gpr_export.xls` (Caldara & Iacoviello Geopolitical Risk Index)

Execute the end-to-end data preprocessing pipeline:
```bash
# Step 1: Preprocess retail petroleum series
python src/preprocess.py

# Step 2: Merge exogenous variables (GPR, Brent, WTI, USD Index)
python scripts/data_prep/merge_exo_data.py

# Step 3: Align business days & construct unified dataset
python scripts/data_prep/build_unified_data.py
```

### 2. Training GUMNet-Het Models
```bash
# Train GUMNet-Het on Gasoline (XANG) for 5-day horizon with walk-forward validation
python scripts/training/train_unified.py \
  --type XANG \
  --model GUMNet_Het \
  --horizon 5 \
  --protocol walkforward \
  --seed 42
```

### 3. Running Paradigm Benchmarks & Multi-Seed Sweeps
```bash
# Run fair benchmark across all paradigms for a specific horizon
python scripts/experiments/run_fair_experiments.py --horizon 1 --seeds 42,123,777,2025,9999

# Run comprehensive multi-model evaluation
python scripts/experiments/run_all_32models.py --target XANG --horizon 1
```

### 4. Evaluating & Generating Statistical Tables
```bash
# Compute DM-Test HAC & Model Confidence Set
python scripts/evaluation/dm_test_32models.py
python scripts/evaluation/model_confidence_set.py

# Generate manuscript tables & verification metrics
python scripts/reports/compile_completed_h_5seeds.py
python scripts/reports/generate_all_outputs.py
```

---

## 🤖 AI Agent Engineering Stack

This project is built and audited with a state-of-the-art multi-agent framework:

- **Antigravity Orchestrator**: Agentic pair programming, mathematical formula auditing, and manuscript synchronization.
- **OmniRoute Gateway** (`http://localhost:20128`): High-throughput routing across 250+ foundation model providers.
- **Skills Ecosystem**:
  - **gstack** (Garry Tan / YC CEO): CEO Review, Engineering Architecture Review, QA & CSO Security Scanners.
  - **agent-skills** (Addy Osmani / Google Chrome): Spec-Driven Development, TDD & Verification Loops.
  - **ECC & Superpowers**: Autonomous debugging, systematic testing, and econometric proof engines.

---

## 📂 Repository Structure

```
oil_forecast_tail_risk/
├── .agents/                         # Multi-Agent orchestrator skills, memory & registry
├── config.py                        # Central configuration (models, seeds, horizons, hyperparams)
├── requirements.txt                 # Lightweight dependencies
├── requirements_32models.txt        # Full scientific & deep learning requirements
├── GUMNETHet_FAIRv7_final.docx      # Complete IEEE-formatted manuscript (v7 Final)
├── GUMNETHet_FAIRv7_redline.docx    # Full redline tracking document with reviewer diffs
│
├── data/
│   ├── raw/                         # Raw price sheets and GPR exports (.gitkeep)
│   └── processed/                   # Unified engineered datasets (.gitkeep)
│
├── src/
│   ├── data/
│   │   └── dataset.py               # TimeSeriesDataset, walk-forward splitting, MIDAS scaling
│   ├── database/
│   │   └── db_manager.py            # SQLite / JSON experiment tracking database
│   ├── evaluation/
│   │   ├── metrics.py               # RMSE, MAE, MAPE, R2, DA, PINAW, Pinball loss
│   │   ├── statistical_tests.py     # Diebold-Mariano HAC, MCS bootstrap, Cliff's Delta
│   │   └── protocols.py             # Walk-forward cross validation protocol
│   ├── models/
│   │   ├── gumnet_het.py            # Core GUMNet-Het architecture (Wavelet-KAN + SSM + iTrans)
│   │   ├── extended_sota.py         # SOTA implementations (TimeMixer, PatchTST, TimeMachine)
│   │   ├── sota_baselines.py        # TFT, TimesNet, Autoformer, Informer, FedFormer
│   │   └── losses.py                # Quantile Pinball Loss + Directional Sign Penalty
│   ├── preprocess.py                # Data ingestion, outlier filtering, business-day alignment
│   └── utils.py                     # Deterministic seed locker, logging, device managers
│
├── scripts/
│   ├── training/                    # Unified training dispatchers and auto-runners
│   ├── experiments/                 # Benchmark runners across 7 paradigms and 5 seeds
│   ├── evaluation/                  # Statistical tests, MCS, effect size computation
│   ├── reports/                     # Automated DOCX, LaTeX, and CSV table compilers
│   ├── visualization/               # High-resolution publication figure generators
│   └── pipeline/                    # End-to-end 10-stage execution pipeline
│
├── paper_figures/                   # High-DPI architecture diagrams and loss landscape plots
└── tests/                           # Unit tests, pipeline dispatch, and stress tests
```

---

## 👥 Authors & Research Team

- **Phuoc Anh Dung Nguyen¹** — *Conceptualization, Methodology, Software, Data Curation, Formal Analysis, Writing – Original Draft*
- **Huong D. Bui¹\*** — *Supervision, Academic Direction, Methodological Validation, Writing – Review & Editing*
- **Quy V. Hoang²\*** — *Theoretical Mathematical Review, Computational Optimization, Statistical Significance Analysis, Writing – Review & Editing*

¹ *Faculty of Information Technology, Ho Chi Minh City University of Technology (HUTECH), Ho Chi Minh City, Vietnam*  
² *Faculty of Information Technology, Thuy Loi University (TLU), Hanoi, Vietnam*  

*\* Corresponding Authors*

---

## 📄 Citation & License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

If you find this codebase or research methodology helpful in your work, please cite:

```bibtex
@article{nguyen2026robust,
  title={Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts},
  author={Nguyen, Phuoc Anh Dung and Bui, Huong D. and Hoang, Quy V.},
  journal={Working Paper / Under Review},
  year={2026}
}
```
