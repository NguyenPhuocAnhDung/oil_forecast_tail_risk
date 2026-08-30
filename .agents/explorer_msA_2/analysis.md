# Analysis of Model Implementations for GUM-Net Research OS

This document provides the read-only analysis and implementation recommendations for integrating the 26 SOTA models (including 6 foundation models) and 10 GUM-Net variants into the experimental pipeline of the retail gasoline and diesel price forecasting research.

---

## 1. Interface Contracts

To maintain fair comparison and seamless integration with the existing `scripts/train_unified.py` pipeline, all models must strictly comply with the following contracts:

### A. SOTA Baselines (`extended_sota.py`)
- **Initialization Signature**:
  ```python
  def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
  ```
  - `input_dim`: number of input features (channels) as configured by `config.py` for the current horizon.
  - `output_dim`: number of target variables (e.g., 2 target columns for XANG/DAU).
  - `horizon`: forecasting steps.
  - `seq_len`: temporal lookback window length.
- **Forward Pass Signature**:
  - Input: PyTorch tensor `x` of shape `[B, seq_len, input_dim]`
  - Output: PyTorch tensor of shape `[B, horizon, output_dim]`

### B. GUM-Net Variants (`gumnet_family.py`)
- **Initialization Signature**:
  ```python
  def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
               horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
               feature_cols: Optional[list] = None):
  ```
- **Forward Pass Signature**:
  - Input: PyTorch tensor `x` of shape `[B, seq_len, input_dim]`
  - Output: Tuple of `(predictions, gating_weights)`
    - `predictions`: PyTorch tensor of shape `[B, horizon, output_dim, num_quantiles]` containing quantile predictions (Q10, Q50/Median, Q90).
    - `gating_weights`: PyTorch tensor of shape `[B, horizon, num_experts]` (e.g., `[B, horizon, 3]`) representing dynamic routing gates.

---

## 2. Analysis of Existing Models

### A. `gumnet_het.py` (v3 Architecture)
The core architecture consists of three heterogeneous experts:
1. **Multi-Scale CNN Expert**: Convolutions along time dimension with kernels `[3, 7, 15]` to capture multi-resolution temporal features.
2. **GRU Expert**: A 2-layer GRU capturing sequential macro dynamics.
3. **Wavelet-KAN Expert**: A Kolmogorov-Arnold Network with Mexican Hat basis functions capturing non-linear feature interactions.

**Feature Partitioning**:
- CNN receives price/crude benchmark features.
- GRU receives macroeconomic/geopolitical risk (GPR) indicators.
- KAN receives derived ratio and momentum features.

### B. Baseline Models (`baselines.py` & `sota_baselines.py`)
- Standard neural baselines: `LSTM`, `GRU`, `BiLSTM_Attention`, `PatchTST`, `DLinear`.
- Non-neural baseline: `XGBoost`.
- SOTA baselines: `TimesNet`, `iTransformer`, `TimeMixer`, `SimplifiedTFT`, `SimplifiedNHits`.
- All baseline outputs are shaped as `[B, horizon, output_dim]`.

---

## 3. Implementation Recommendations for `extended_sota.py`

We recommend writing 26 models into `src/models/extended_sota.py`. This includes the 20 contemporary SOTA models and 6 Time Series Foundation Models (TSFMs). 

### Architectural Designs for Contemporary SOTA:
1. **RLinear (Reversible Linear)**: Combines Reversible Instance Normalization (RevIN) with temporal projection to handle distribution shifts.
2. **LTSF_Linear**: Direct temporal projection mapping history directly to horizon.
3. **NBEATS**: Doubly residual blocks with backcast and forecast projections.
4. **Autoformer**: Auto-correlation mechanism via FFT instead of standard self-attention, and series decomposition.
5. **FedFormer**: Frequency-enhanced attention (Fourier block) and decomposition.
6. **Informer**: ProbSparse self-attention to select top active queries.
7. **Reformer**: Locality Sensitive Hashing (LSH) bucket-based attention to reduce space complexity.
8. **UniTS**: Unified temporal-channel mixer for multi-task time-series.
9. **TimeXer**: Cross-attention between variable (channel) tokens and temporal tokens.
10. **Crossformer**: Dimension-Segment-Wise (DSW) patching and Two-Stage Attention (TSA).
11. **CARD**: Conditional diffusion-based forecasting proxy using a light conditional denoising MLP.
12. **FITS**: Frequency interpolation using discrete Fourier transform.
13. **CoST**: Contrastive seasonal-trend representation learning.
14. **TTM (Tiny Time Mixers)**: Lightweight patch mixing MLP.
15. **TimeMachine**: State Space Model (Mamba) routed across time and channel dimensions.
16. **S_Mamba**: Mamba-style selective SSM block along time.
17. **MambaFormer**: Alternating Mamba SSM layers and Self-Attention layers.
18. **BiMamba**: Bidirectional Mamba SSM scans.
19. **Time_MoE**: Dynamic mixture of experts along time.
20. **Gated_TabNet**: Tabular gating applied to temporal series forecasting.

### Foundation Model Offline Wrappers:
To support running in a strict offline environment without needing heavy pre-trained weights or downloading checkpoints, we recommend implementing **offline wrappers with random weights**:
21. **Chronos**: Simulates token quantization and a T5 encoder-decoder module.
22. **TimesFM**: Patch-based decoder-only transformer simulation.
23. **Moirai**: Multi-patch size attention simulation.
24. **Lag_Llama**: Lags-based feature extraction fed to LLaMA-like Transformer.
25. **TEMPO**: Prompt-pool matching, decomposition, and transformer.
26. **GPT4TS**: Channel-wise patching and GPT-like multi-head attention.

> **Verification Status**: Complete Python implementations of all 26 SOTA classes have been written to `proposed_extended_sota.py` and verified using `test_proposed_models.py` for shape safety under different lookbacks and horizons.

---

## 4. Implementation Recommendations for `gumnet_family.py`

We recommend subclassing `GUMNetHet` from `src/models/gumnet_het.py` to inherit the feature partitioning and gating logic, while surgically swapping key experts or outputs:

1. **GUMNetMamba**: Swap GRU expert with a Mamba SSM selective scan block.
2. **GUMNetiTrans**: Swap CNN expert with an iTransformer inverted attention block.
3. **GUMNetWavelet**: Replace all experts with Wavelet-KAN blocks (Mexican Hat basis functions) for a KAN-only model.
4. **GUMNetPatch**: Group input time steps into patches before feeding them to the CNN expert.
5. **GUMNetFourier**: Mix features in the frequency domain using FFT before expert projection.
6. **GUMNetDiffusion**: Swap the linear prediction head with a conditional DDPM denoising head (simulating reverse diffusion steps).
7. **GUMNetGraph**: Apply a Spatio-Temporal Graph Convolutional Network (ST-GCN) layer on the input channels before routing.
8. **GUMNetRL**: Model the gate as a policy network producing routing actions.
9. **GUMNetMoESparse**: Top-K Switch routing (e.g., Top-2 routing) that zeroes out low-weight experts to enforce sparsity.
10. **GUMNetFusion (Champion)**: Fuses iTransformer (CNN replacement), Mamba SSM (GRU replacement), Wavelet KAN, and temperature-controlled gating.

> **Verification Status**: Complete Python implementations of all 10 variants have been written to `proposed_gumnet_family.py` and successfully tested.

---

## 5. System Integration & Dispatch Updates

### A. Updating `config.py`
Register all models within `SOTA_TAXONOMY_REGISTRY` and `GUM_NET_VARIANTS` inside `config.py` using Python-safe identifiers:
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
ALL_SOTA_BASELINES = [m for ms in SOTA_TAXONOMY_REGISTRY.values() for m in ms]

GUM_NET_VARIANTS = [
    "GUMNet", "GUMNet_Mamba", "GUMNet_iTrans", "GUMNet_Wavelet",
    "GUMNet_Patch", "GUMNet_Fourier", "GUMNet_Diffusion", "GUMNet_Graph",
    "GUMNet_RL", "GUMNet_MoE_Sparse", "GUMNet_Fusion",
]
```

### B. Updating model dispatch in `scripts/train_unified.py`
Implement `get_model_instance(name, cfg)` inside `scripts/train_unified.py` mapping string names to class instances:
```python
def get_model_instance(name: str, cfg: dict):
    from src.models.baselines import BASELINE_REGISTRY
    from src.models.extended_sota import SOTA_CLASS_REGISTRY
    from src.models.gumnet_family import GUMNET_FAMILY_REGISTRY
    from src.models.gumnet import GUMNet
    from src.models.gumnet_het import GUMNetHet

    input_dim = len(cfg['feature_cols'])
    output_dim = len(cfg['target_cols'])
    horizon = cfg['horizon']
    seq_len = cfg['seq_len']
    d_feat = cfg.get('d_feat', 64)

    # GUM-Net variants
    if name == "GUMNet":
        return GUMNet(seq_len=seq_len, input_dim=input_dim, output_dim=output_dim, horizon=horizon, d_feat=d_feat)
    elif name == "GUMNetHet":
        return GUMNetHet(seq_len=seq_len, input_dim=input_dim, output_dim=output_dim, horizon=horizon, d_feat=d_feat, feature_cols=cfg['feature_cols'])
    elif name in GUMNET_FAMILY_REGISTRY:
        return GUMNET_FAMILY_REGISTRY[name](seq_len=seq_len, input_dim=input_dim, output_dim=output_dim, horizon=horizon, d_feat=d_feat, feature_cols=cfg['feature_cols'])

    # SOTA models from extended registry
    elif name in SOTA_CLASS_REGISTRY:
        return SOTA_CLASS_REGISTRY[name](input_dim=input_dim, output_dim=output_dim, horizon=horizon, seq_len=seq_len)

    # Baseline models
    elif name in BASELINE_REGISTRY:
        model_class = BASELINE_REGISTRY[name]
        if name in ['PatchTST', 'DLinear', 'TimesNet', 'iTransformer', 'TimeMixer', 'TFT', 'NHits']:
            return model_class(input_dim=input_dim, output_dim=output_dim, horizon=horizon, seq_len=seq_len)
        else:
            return model_class(input_dim=input_dim, output_dim=output_dim, horizon=horizon)

    raise ValueError(f"Unknown model name: {name}")
```

This ensures that the dispatch functions correctly handle the full portfolio of 32+ models.
