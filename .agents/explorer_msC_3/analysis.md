# Academic Analysis Report: Milestone C Updates for GUM-Net

This report provides the detailed academic analysis and formulation of updates required for the five core research reports in `docs/research_os/`. These formulations are structured to align with top-tier Q1 journal requirements (e.g., *Energy Economics*, *IEEE Transactions*), ensuring mathematical rigor, clear conceptual mapping, and econometric validity.

---

## 1. Analysis & Formulations for `docs/research_os/stage2_conceptual_gaps.md`

### 1.1 SOTA Classification Matrix (22 Models across 7 Paradigms)

To expose the technical limitations of existing state-of-the-art architectures in regulated energy markets under geopolitical volatility, we classify 22 SOTA models across 7 paradigms.

| Paradigm ID & Name | SOTA Models | Key Architectural Philosophy | Critical Technical Gaps under Tail Risk & BOG Policy |
|---|---|---|---|
| **P1: Linear & Decomposition** | DLinear, RLinear, LTSF_Linear, NBEATS, NHits | Maps raw coordinates via direct linear projections, optionally employing trend/seasonal decomposition or forward/backward residual links. | Assumes stationary linear trajectories. Fails to model non-linear price spread variations and suffers from extreme phase lag under BOG step-like price adjustments (**Failure Type B: Regime Delay**). |
| **P2: Dense Attention (Transformer)** | PatchTST, TFT, Autoformer, FedFormer, Informer, Reformer | Groups time steps or patches into dense tokens and computes global pairwise attention matrices ($Q, K, V$). | Global attention matrices suffer from logit saturation under extreme geopolitical shocks (GPR > 200). Vulnerable to macro-noise overfitting during stable periods (**Failure Type C: Overshoot**). |
| **P3: Inverted Attention** | iTransformer, UniTS, TimeXer, Crossformer, CARD | Flattens the temporal sequence into a unified vector per variable, computing attention across variables instead of time. | Focuses on cross-variable alignment at the expense of local temporal dynamics. Fails to model high-frequency structural breaks and sudden pricing updates (**Failure Type C: Overshoot**). |
| **P4: Frequency-Domain** | TimesNet, TimeMixer, TTM, FITS, CoST | Applies Fast Fourier Transform (FFT) to extract periodic components, folding 1D series into 2D spatial feature tensors. | Suffers from the Gibbs phenomenon and spectral leakage when modeling discontinuous, non-periodic step-functions and geopolitical shocks, causing false oscillations (**Failure Type B: Regime Delay**). |
| **P5: State Space Models (SSM)** | TimeMachine, S_Mamba, MambaFormer, BiMamba | Formulates linear time-varying selective scan channels to capture long-range temporal dependencies with linear complexity. | The Markovian state transition assumption fails to isolate high-frequency transient geopolitical shocks. Imposed continuity smooths out discrete regulatory price adjustments. |
| **P6: Foundation Models (TSFM)** | Chronos, TimesFM, Moirai, Lag_Llama, TEMPO, GPT4TS | Large-scale pre-trained models executing zero-shot forecasting based on global, open-domain time series. | Severe extrapolation hallucination and out-of-distribution (OOD) failure due to the phase mismatch between global market datasets and regulated Vietnamese downstream price-setting formulas. |
| **P7: Sparse Mixture-of-Experts** | Time_MoE, Gated_TabNet | Employs sparse gating networks to route tokens to a subset of parallel feed-forward networks (experts). | Token-level routing decisions are static and decoupled from exogenous geopolitical risk indicators (GPR), leading to sub-optimal expert selection during crisis regimes. |

### 1.2 Target Distribution Formulation

Under the Vietnamese Price Stabilization Fund (BOG) policy, the retail petroleum price trajectory does not follow a standard continuous stochastic process. It behaves as a piece-wise constant step function punctuated by high-frequency shocks during geopolitical crises. We formalize the target price-change distribution $\mathcal{D}_{\text{target}}$ as:

$$\mathcal{D}_{\text{target}} \sim \sum_{k=1}^K C_k \cdot \mathbb{I}(t \in [T_{k-1}, T_k]) + \epsilon_t \cdot \mathbb{I}(GPR_t \ge GPR_{\text{gate}})$$

Where:
* $T_k$ is the regulatory announcement date of the $k$-th pricing adjustment decree (typically spaced 7 or 10 days apart).
* $C_k$ is the constant retail price level set by the Ministry of Finance and the Ministry of Industry and Trade for the window $[T_{k-1}, T_k]$.
* $\mathbb{I}(\cdot)$ is the indicator function mapping the temporal domain.
* $\epsilon_t$ represents the localized high-frequency shock response term, driven by spot-market price changes.
* $GPR_t$ is the daily Caldara-Iacoviello Geopolitical Risk index value.
* $GPR_{\text{gate}}$ is the hard-threshold activation gate (e.g., 120 points) below which minor geopolitical variations are filtered out to prevent phantom volatility.

### 1.3 Morphological Mismatch Analysis

The fundamental conceptual barrier in utilizing standard deep learning architectures for regulated energy markets is the **Morphological Mismatch** between the pre-training distribution ($\mathcal{D}_{\text{pretrain}}$) and the target retail distribution ($\mathcal{D}_{\text{target}}$).

1. **Pre-training Distribution ($\mathcal{D}_{\text{pretrain}}$)**:
   TSFMs and baseline neural networks are optimized on global, weakly stationary, and IID-like datasets (e.g., weather, electricity, global commodity spots). These series exhibit continuous temporal variations where the probability of zero change is negligible:
   $$P(\Delta Y_t = 0) \to 0$$
   The transition density is smooth, and the gradients of the target with respect to time are non-zero almost everywhere:
   $$\frac{\partial Y_t}{\partial t} \neq 0$$

2. **Target Distribution ($\mathcal{D}_{\text{target}}$)**:
   The BOG intervention transforms retail prices into a discontinuous step-like structure. The target change distribution is a mixture of a Dirac delta function at zero (representing the flat steps where prices are held constant) and a continuous distribution of jump sizes triggered by international crude adjustments:
   $$p(\Delta Y_t) = (1 - \pi) \delta(0) + \pi \cdot \mathcal{N}(\mu_{\text{jump}}, \sigma^2_{\text{jump}})$$
   Where $\pi \in [0, 1]$ is the probability of a regulatory adjustment on any given day. Here, the derivative of the target is zero almost everywhere:
   $$\frac{\partial Y_t}{\partial t} = 0 \quad \forall t \neq T_k$$

3. **Mathematical Consequences of Mismatch**:
   * **Gradient Collapse and Smooth Bias**: Since the loss function (typically L2/L1) calculates gradients based on continuous activations, the network is biased toward predicting the conditional mean $\mathbb{E}[Y_t | X_t]$. Because $X_t$ (international oil) fluctuates daily, the model outputs continuous fluctuations. This introduces *phantom volatility* in flat steps ($\Delta Y_t = 0$) and *phase lag* (transition smearing) at boundaries ($T_k$).
   * **Unbounded KL Divergence**: If the true distribution $P$ contains a Dirac delta point mass at zero and the predicted distribution $Q$ is fully continuous ($q(0) < 1$), the Kullback-Leibler divergence diverges to infinity:
     $$D_{KL}(P \parallel Q) = \int p(x) \log\left(\frac{p(x)}{q(x)}\right) dx \to \infty$$
     This divergence proves the absolute theoretical limitation of continuous neural architectures in matching step-like regulated targets.

### 1.4 Detailed Specification of 5 Strategic Research Gaps

* **GAP 1: Uniform Joint Embedding Contamination**: SOTA architectures map gasoline (stationary, mean-reverting due to local environmental tax offsets) and diesel (non-stationary, trend-following due to direct commercial usage) into a unified representation space. This joint mapping causes signal contamination, where diesel's trend degrades gasoline's mean-reversion, and gasoline's stationary variance degrades diesel's trend tracking.
* **GAP 2: Inability to Absorb Geopolitical Shocks**: Existing models lack structural mechanisms to isolate and process sudden geopolitical shock impulses. Global self-attention or linear weights are contaminated by transient spikes, leading to performance collapse during crises.
* **GAP 3: Static / Horizon-Blind Routing**: Multi-model ensembles or mixture-of-experts (MoE) employ static routing gates. They fail to adaptively shift routing weights as the forecasting horizon extends from short-term momentum (e.g., $H=1$) to long-term macroeconomic trend (e.g., $H=60$).
* **GAP 4: Unsound Validation in Regulated Markets**: Standard time-series validation protocols use random splits (leading to data leakage) or standard cross-validation, and perform model evaluation based on global, average metrics. They fail to account for serial correlation (autocorrelation in residuals) and multiple hypothesis testing bias in regulated environments.
* **GAP 5: Distribution Mismatch under BOG Policy**: Continuous neural outputs fail to represent the step-like trajectory of regulated retail prices. Standard models optimize L2/L1 losses, leading to regression-to-the-mean bias, which manifests as phantom volatility in flat price regimes and phase lag at adjustment boundaries.

---

## 2. Analysis & Formulations for `docs/research_os/stage5_hypothesis_design.md`

### 2.1 Four-Layer Structural Blueprint of the GUM-Net Family

We formalize the mathematical operations of the 10 GUM-Net family variants across four functional layers.

```
+-----------------------------------------------------------------------------+
| TẦNG 4: ĐỊNH TUYẾN & HỢP NHẤT (Routing & Fusion Layer)                     |
| - GUM-Net MoE-Sparse: Top-K Switch Router (K=1, 2)                         |
| - GUM-Net Fusion: GPR-conditioned Temp Gate + Residual Scaling (Champion)   |
+-----------------------------------------------------------------------------+
                                       ^
                                       |
+-----------------------------------------------------------------------------+
| TẦNG 3: GENERATIVE / CAUSAL (Generative, Graph & Control Layer)             |
| - GUM-Net Diffusion: Conditional Denoising Diffusion Probabilistic Model    |
| - GUM-Net Graph: Spatio-Temporal GCN on Brent/WTI -> Platts -> retail price  |
| - GUM-Net RL: PPO agent adjusting gate temp via Sign Loss Reward            |
+-----------------------------------------------------------------------------+
                                       ^
                                       |
+-----------------------------------------------------------------------------+
| TẦNG 2: BỘ LỌC VÀ THAM SỐ (Filtering & Tokenization Layer)                 |
| - GUM-Net Patch: Semantic Patch-attention before CNN/GRU experts            |
| - GUM-Net Fourier: FFT Multi-period Mixing & spectral noise filtering       |
+-----------------------------------------------------------------------------+
                                       ^
                                       |
+-----------------------------------------------------------------------------+
| TẦNG 1: CHUYÊN GIA CƠ SỞ (Base Experts Layer)                               |
| - GUM-Net Mamba: Selective State Space Scan (GRU replacement)               |
| - GUM-Net iTrans: Inverted Channel Attention (CNN replacement)              |
| - GUM-Net Wavelet: Localized Mexican Hat Wavelet KAN (Shock absorber)       |
+-----------------------------------------------------------------------------+
```

#### Tầng 1: Chuyên gia cơ sở (Base Experts Layer)
1. **GUM-Net Mamba (SSM Expert)**:
   Replaces the GRU temporal expert with a selective state-space block scanning along time:
   $$h_t = \mathbf{A}_t h_{t-1} + \mathbf{B}_t x_t, \quad y_t = \mathbf{C}_t h_t + \mathbf{D}_t x_t$$
   Where selectivity is introduced by parameterizing the discretization step $\Delta_t$ and projection matrices as functions of input $x_t$:
   $$\mathbf{B}_t = \text{Linear}_B(x_t), \quad \mathbf{C}_t = \text{Linear}_C(x_t), \quad \Delta_t = \text{softplus}\left(\text{Linear}_\Delta(x_t)\right)$$
   $$\mathbf{A}_t = \exp\left(\Delta_t \mathbf{A}\right)$$
2. **GUM-Net iTrans (Inverted Attention Expert)**:
   Replaces the CNN expert with a channel-wise inverted Transformer. Instead of computing attention across time steps, it flattens the temporal sequence for each variable and computes attention across the variable dimension to capture feature alignment:
   $$\mathbf{T}_i = \text{Linear}(X_{:,i}) \quad \forall i \in [1, D]$$
   $$\mathbf{Q} = \mathbf{T} W_Q, \quad \mathbf{K} = \mathbf{T} W_K, \quad \mathbf{V} = \mathbf{T} W_V$$
   $$\mathbf{A} = \text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{Softmax}\left(\frac{\mathbf{Q} \mathbf{K}^T}{\sqrt{d_k}}\right) \mathbf{V}$$
3. **GUM-Net Wavelet (Localized KAN Expert)**:
   A Pure Wavelet-KAN architecture replacing splines with Mexican Hat wavelets on KAN edges:
   $$\psi_{j,k}(x) = C_{j,k} \cdot \left( 1 - z_{j,k}^2 \right) \exp\left( -0.5 \cdot z_{j,k}^2 \right)$$
   $$z_{j,k} = \frac{x - \mu_k}{\sigma_j}, \quad C_{j,k} = \frac{2}{\sqrt{3 \sigma_j} \pi^{1/4}}$$
   The scale parameter $\sigma_j > 0$ and translation parameter $\mu_k$ are updated via backpropagation:
   $$\frac{\partial \psi}{\partial \sigma_j} = \frac{\psi(z_{j,k})}{\sigma_j} \cdot \left[ \frac{-z_{j,k}^4 + 3.5 z_{j,k}^2 - 0.5}{1 - z_{j,k}^2} \right] \quad \text{for } z_{j,k}^2 \neq 1$$

#### Tầng 2: Bộ lọc (Filtering & Tokenization Layer)
4. **GUM-Net Patch (Semantic Patch Tokenization)**:
   Divides the input time series into overlapping patches of length $P$ and stride $S$ to capture local semantic correlation before routing:
   $$x_p \in \mathbb{R}^{P \times D} \quad \forall p \in \left[1, \left\lfloor \frac{L-P}{S} \right\rfloor + 1\right]$$
   $$\mathbf{E}_p = \text{Linear}(x_p) + \mathbf{Pos}_p$$
   $$\mathbf{Z} = \text{SelfAttention}(\mathbf{E})$$
5. **GUM-Net Fourier (FFT Multi-Period Mixing)**:
   Extracts periodic signatures and filters high-frequency noise using the Discrete Fourier Transform:
   $$\mathcal{F}(X)_k = \sum_{t=0}^{L-1} X_t \exp\left(-i \frac{2\pi k t}{L}\right)$$
   $$\mathcal{F}(X)_k^{\text{filtered}} = \mathcal{F}(X)_k \cdot \mathbb{I}(k \le f_{\text{cutoff}})$$
   $$X^{\text{mixed}} = \text{InverseDFT}\left(\mathcal{F}(X)^{\text{filtered}} \cdot W_f\right)$$

#### Tầng 3: Generative / Causal (Generative, Graph & Control Layer)
6. **GUM-Net Diffusion (DDPM Probabilistic)**:
   Formulates a conditional Denoising Diffusion Probabilistic Model to generate future cumulative log-returns:
   $$p_\theta(y_{0:T} | x) = p(y_T) \prod_{t=1}^T p_\theta(y_{t-1} | y_t, x)$$
   $$p_\theta(y_{t-1} | y_t, x) = \mathcal{N}\left(y_{t-1}; \mu_\theta(y_t, t, x), \Sigma_\theta(y_t, t, x)\right)$$
7. **GUM-Net Graph (Spatio-Temporal GCN)**:
   Captures energy supply chain causal transmission (Brent/WTI $\to$ Platt's Singapore $\to$ retail gasoline/diesel) using Spatio-Temporal Graph Convolutional Networks (ST-GCN):
   $$Z^{(l+1)} = \sigma\left(\tilde{D}^{-1/2} \tilde{A} \tilde{D}^{-1/2} Z^{(l)} W^{(l)}\right)$$
   Where $A$ is the causal adjacency matrix, $\tilde{A} = A + I_N$, and $\tilde{D}$ is the diagonal degree matrix of $\tilde{A}$.
8. **GUM-Net RL (Reinforcement Learning Control)**:
   Employs a Proximal Policy Optimization (PPO) agent to control the routing temperature $\tau_t$ based on a Sign-Loss penalized reward:
   $$R_t = \text{sgn}(y_{t+H} \cdot \hat{y}_{t+H}) \cdot \log\left(1 + |y_{t+H}|\right) - \gamma \cdot \mathbb{I}\left(\text{sgn}(y_{t+H}) \neq \text{sgn}(\hat{y}_{t+H})\right) \cdot \left|y_{t+H} - \hat{y}_{t+H}\right|$$

#### Tầng 4: Định tuyến và Hợp nhất (Routing & Fusion Layer)
9. **GUM-Net MoE-Sparse (Top-K Switch Router)**:
   Routes tokens to a subset of experts using a sparse gating mechanism:
   $$G(x) = \text{Softmax}\left(\text{Top-K}\left(x \cdot W_g + \epsilon, K\right)\right), \quad \epsilon \sim \mathcal{N}(0, \sigma^2)$$
10. **GUM-Net Fusion (Champion Model)**:
    Integrates iTransformer (inverted attention), Mamba SSM, and Wavelet-KAN.
    * **Dynamic Temperature Routing Gate**:
      $$\tau_t = \tau_0 \cdot \exp\left(-\gamma \cdot \left[|GPR_t| + \beta \cdot |\Delta GPR_t|\right]\right)$$
      $$w_i(x_t) = (1 - \lambda) \cdot \frac{\exp\left(\frac{g_i(x_t)}{\tau_t}\right)}{\sum_{j=1}^3 \exp\left(\frac{g_j(x_t)}{\tau_t}\right)} + \frac{\lambda}{3}$$
      Where $\tau_0 = 1.5$, $\gamma = 0.05$ (geopolitical level sensitivity), $\beta = 0.1$ (geopolitical velocity sensitivity), and $\lambda = 0.1$ is the residual scaling hyperparameter ensuring gradient flow.
    * **Residual Scaling**:
      $$\hat{R}_{t \to t+H} = \text{head}(f_{\text{fused}}) + X_t \cdot \beta_H$$

### 2.2 Falsifiable Hypotheses

* **RQ1: Stationarity-Aware Decoupled Modelling**
  * Null Hypothesis ($H_0$): $\text{MAE}_{\text{decoupled}} \ge \text{MAE}_{\text{joint}}$ and $R^2_{\text{decoupled}} \le R^2_{\text{joint}}$
  * Alternative Hypothesis ($H_1$): $\text{MAE}_{\text{decoupled}} < \text{MAE}_{\text{joint}}$ and $R^2_{\text{decoupled}} > R^2_{\text{joint}}$
* **RQ2: Wavelet-KAN Shock Absorption & GPR Filtering**
  * Null Hypothesis ($H_0$): $\text{DA}_{\text{Wavelet-KAN}} \le \text{DA}_{\text{MLP/B-Spline}}$ and $\text{MAPE}_{\text{crisis, Wavelet-KAN}} \ge \text{MAPE}_{\text{crisis, MLP/B-Spline}}$
  * Alternative Hypothesis ($H_1$): $\text{DA}_{\text{Wavelet-KAN}} > \text{DA}_{\text{MLP/B-Spline}}$ and $\text{MAPE}_{\text{crisis, Wavelet-KAN}} < \text{MAPE}_{\text{crisis, MLP/B-Spline}}$
* **RQ3: Horizon-Aware Gating & Temperature Scaling**
  * Null Hypothesis ($H_0$): $\mathcal{L}_{\text{dynamic\_routing}} \ge \mathcal{L}_{\text{static\_ensemble}}$
  * Alternative Hypothesis ($H_1$): $\mathcal{L}_{\text{dynamic\_routing}} < \mathcal{L}_{\text{static\_ensemble}}$
* **RQ4: Extrapolation Error Bounding (Residual Scaling)**
  * Null Hypothesis ($H_0$): $\text{MAPE}_{H60, \text{scaling}} \ge \text{MAPE}_{H60, \text{raw}}$ or $\text{MAE}_{H1, \text{scaling}} > \text{MAE}_{H1, \text{raw}}$
  * Alternative Hypothesis ($H_1$): $\text{MAPE}_{H60, \text{scaling}} < \text{MAPE}_{H60, \text{raw}}$ and $\text{MAE}_{H1, \text{scaling}} \approx \text{MAE}_{H1, \text{raw}}$

---

## 3. Analysis & Formulations for `docs/research_os/stage7_baseline_taxonomy.md`

### 3.1 Benchmark Taxonomy & Architectural Rationale

To validate the theoretical advantages of GUM-Net, it is evaluated against 22 SOTA baselines mapped into 7 distinct paradigms:

| Paradigm | Baselines | Core Architectural Arguments | Key Vuln. under Tail Risk |
|---|---|---|---|
| **P1: Linear** | DLinear, RLinear, LTSF_Linear, NBEATS, NHits | Relies on direct linear projection matrices, bypassing attention to prevent overfitting. | Inability to capture non-linear geopolitical shocks and BOG step-jumps. |
| **P2: Transformer** | PatchTST, TFT, Autoformer, FedFormer, Informer, Reformer | Computes global multi-head self-attention on temporal coordinates or patches. | Softmax attention collapse and macro-noise overfitting during spikes. |
| **P3: Inverted** | iTransformer, UniTS, TimeXer, Crossformer, CARD | Learns independent token representations per variable, computing cross-variable attention. | Loss of local temporal dynamics and structural break synchronization. |
| **P4: Frequency** | TimesNet, TimeMixer, TTM, FITS, CoST | Maps 1D sequences to 2D matrices using FFT, extracting multi-period overlapping cycles. | Spectral leakage and Gibbs oscillations near discontinuous step boundaries. |
| **P5: SSM** | TimeMachine, S_Mamba, MambaFormer, BiMamba | Scans sequences linearly using Selective State Space Models. | Linearity of the state updates smooths out discrete regulatory price adjustments. |
| **P6: Foundation** | Chronos, TimesFM, Moirai, Lag_Llama, TEMPO, GPT4TS | Pre-trained global forecasting models executing zero-shot prediction. | Out-of-distribution extrapolation errors in highly regulated local markets. |
| **P7: Sparse MoE** | Time_MoE, Gated_TabNet | Routes inputs dynamically to subsets of feed-forward experts. | Static token-level routing ignores macro-risk variables like GPR. |

### 3.2 The Verbatim R8 Selection Policy Rule
To ensure absolute academic integrity and prevent selective reporting bias, the evaluation registry implements the following rule verbatim:

> "Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu."

### 3.3 Python Dispatch Code for Benchmark Registry

This implementation dispatch code maps string identifiers to PyTorch classes for model initialization, adhering to the `get_model_instance` signature.

```python
# benchmark_registry.py
import torch
import torch.nn as nn
from src.models.baselines import LSTMModel, GRUModel, BiLSTMAttn, XGBoostRegressorWrapper
from src.models.sota_baselines import PatchTST, DLinear, TimesNet, iTransformer, TimeMixer, TFT, NHits
from src.models.extended_sota import (
    RLinear, LTSF_Linear, NBEATS, Autoformer, FedFormer, Informer, Reformer,
    UniTS, TimeXer, Crossformer, CARD, FITS, CoST, TTM, TimeMachine,
    S_Mamba, MambaFormer, BiMamba, Time_MoE, Gated_TabNet
)
from src.models.gumnet_family import (
    GUMNet, GUMNet_Mamba, GUMNet_iTrans, GUMNet_Wavelet, GUMNet_Patch,
    GUMNet_Fourier, GUMNet_Diffusion, GUMNet_Graph, GUMNet_RL,
    GUMNet_MoE_Sparse, GUMNet_Fusion
)

MODEL_REGISTRY = {
    # Baselines
    "LSTM": LSTMModel,
    "GRU": GRUModel,
    "BiLSTM_Attention": BiLSTMAttn,
    "XGBoost": XGBoostRegressorWrapper,
    # SOTA Baselines
    "PatchTST": PatchTST,
    "DLinear": DLinear,
    "TimesNet": TimesNet,
    "iTransformer": iTransformer,
    "TimeMixer": TimeMixer,
    "TFT": TFT,
    "NHits": NHits,
    # P1: Linear & Decomposition
    "RLinear": RLinear,
    "LTSF_Linear": LTSF_Linear,
    "NBEATS": NBEATS,
    # P2: Transformer-based
    "Autoformer": Autoformer,
    "FedFormer": FedFormer,
    "Informer": Informer,
    "Reformer": Reformer,
    # P3: Inverted attention
    "UniTS": UniTS,
    "TimeXer": TimeXer,
    "Crossformer": Crossformer,
    "CARD": CARD,
    # P4: Frequency-domain
    "TTM": TTM,
    "FITS": FITS,
    "CoST": CoST,
    # P5: State Space Models (SSM)
    "TimeMachine": TimeMachine,
    "S_Mamba": S_Mamba,
    "MambaFormer": MambaFormer,
    "BiMamba": BiMamba,
    # P7: Sparse MoE
    "Time_MoE": Time_MoE,
    "Gated_TabNet": Gated_TabNet,
    # GUM-Net Family
    "GUMNet": GUMNet,
    "GUMNet_Mamba": GUMNet_Mamba,
    "GUMNet_iTrans": GUMNet_iTrans,
    "GUMNet_Wavelet": GUMNet_Wavelet,
    "GUMNet_Patch": GUMNet_Patch,
    "GUMNet_Fourier": GUMNet_Fourier,
    "GUMNet_Diffusion": GUMNet_Diffusion,
    "GUMNet_Graph": GUMNet_Graph,
    "GUMNet_RL": GUMNet_RL,
    "GUMNet_MoE_Sparse": GUMNet_MoE_Sparse,
    "GUMNet_Fusion": GUMNet_Fusion
}

def get_model_instance(name: str, cfg: dict) -> nn.Module:
    """
    Unified model dispatcher. Maps string identifiers to PyTorch modules.
    Guarantees no KeyError for any model registered in MODEL_REGISTRY.
    """
    if name not in MODEL_REGISTRY:
        raise KeyError(
            f"Model '{name}' is not registered in the benchmark suite. "
            f"Please register it in MODEL_REGISTRY. Available models: {list(MODEL_REGISTRY.keys())}"
        )
    return MODEL_REGISTRY[name](**cfg)
```

---

## 4. Analysis & Formulations for `docs/research_os/stage9_failure_diagnostics.md`

### 4.1 Anti-Fabrication Constraints & Post-Experimental Estimation Protocol

To enforce absolute empirical honesty, this research prohibits the use of hardcoded pre-computed values for diagnostic evaluation (e.g., hardcoded skewness, kurtosis, or Value-at-Risk parameters). Instead, all validation metrics must be derived dynamically through the **Post-experimental Estimation Protocol**:
1. **Dynamic Metric Computation**: All statistical indicators (Kurtosis, Skewness, $\text{VaR}_\alpha$, $\text{CVaR}_\alpha$) must be calculated on the actual validation residuals ($e_t$) of the model run:
   $$\text{Kurtosis} = \frac{\frac{1}{N} \sum_{t=1}^N (e_t - \bar{e})^4}{\left(\frac{1}{N} \sum_{t=1}^N (e_t - \bar{e})^2\right)^2}$$
2. **Dynamic Quantile Evaluation**: Quantile boundaries are determined based on the empirical distribution of test-set price predictions ($q=0.10, 0.50, 0.90$), preventing synthetic boundary definitions.

### 4.2 Systematic Error Classification Grouping

We categorize forecasting residuals into four systematic error groups to isolate architectural failures:

* **Type A: Trend Miss (Shock Saturation)**:
  * *Description*: Underestimation of extreme price spikes during sudden geopolitical crises (e.g., Brent spikes during initial shocks of the 2022 Russia-Ukraine War).
  * *Mathematical Indicator*: $Y_{t+H} > \hat{Y}_{t+H|t}^{(q=0.90)}$ during periods where $GPR_t > 200$.
  * *Architectural Cause*: Delay in Wavelet-KAN expert activation and lag in softmax temperature adjustments.
* **Type B: Regime Delay (Lagged BOG Adjustment)**:
  * *Description*: Temporal delay in capturing discrete price updates governed by the Price Stabilization Fund (BOG).
  * *Mathematical Indicator*: $\text{Corr}(e_t, e_{t-k}) \gg 0$ for $k \in [1, 10]$ during flat regimes, followed by an error spike on announcement day.
  * *Architectural Cause*: The continuous activation functions of neural networks smooth out step-like boundaries.
* **Type C: Overshoot (Macro-Noise Pollution)**:
  * *Description*: Prediction of false fluctuations ("phantom volatility") during stable, flat price periods.
  * *Mathematical Indicator*: $\text{Var}(\hat{Y}_{t+H|t}) \gg \text{Var}(Y_{t+H}) \approx 0$ when $GPR_t < 120$.
  * *Architectural Cause*: Leakage of minor geopolitical variations through KAN activation functions when the GPR Noise Gate is bypassed.
* **Type D: Policy Plateau (Horizon-Dependent Phase Shift)**:
  * *Description*: Temporal delay (time shift) of predicted peaks and turning points relative to actual target changes at long horizons.
  * *Mathematical Indicator*: $\arg\max_k \text{CrossCorr}\left(Y_t, \hat{Y}_{t-k|t-H-k}\right) = d > 0$ as $H \to 60$.
  * *Architectural Cause*: Loss of high-frequency temporal alignment in multi-step direct projections, causing the network to favor the stable but slow GRU expert.

### 4.3 Two-Phase Stress-Testing Protocol for Window 5 (2026 US-Iran Crisis)

To evaluate model resilience under structural breaks, the benchmark pipeline executes a two-phase temporal audit on the simulated 2026 US-Iran crisis window (01/2026 - 05/2026):

```
                       2026 US-IRAN TEST PROTOCOL
                                   |
                  +----------------+----------------+
                  |                                 |
                  v                                 v
        [ PHASE 1: Right-Censoring ]       [ PHASE 2: Worst-case ]
        - Cutoff Date: 2026-04-30          - Cutoff Date: 2026-05-31
        - Evaluates shock anticipation     - Evaluates peak performance
        - Right-censors H60 labels         - Full sequence evaluated
        - Gating: w_3 (KAN) -> 0.933       - Gating: w_2 (GRU) -> 0.75
```

1. **Phase 1: 2026-04-30 Cutoff (Right-Censoring)**:
   * *Protocol*: The test set sequence is truncated at `2026-04-30`. Because the target forecasting horizon extends up to $H=60$, the ground-truth target labels for the subsequent 60 trading days are right-censored. The model must forecast cumulative log-returns using only context up to April 30, 2026, during the peak of the Strait of Hormuz blockade simulation (normalized $\overline{GPR}_t \approx 3.50$).
   * *Verification*: Measures if the dynamic router correctly triggers the low-temperature gate:
     $$\tau_t \to 1.25 \implies w_3 \to 0.933$$
     This routes signals to the Wavelet-KAN expert to capture local shock dynamics, mitigating Type A (Trend Miss) errors.
2. **Phase 2: 2026-05-31 Cutoff (Worst-Case Robustness)**:
   * *Protocol*: The test sequence is evaluated up to `2026-05-31` after the BOG buffer is depleted, causing retail prices to spike by $15\%$. Ground-truth labels are fully released for the $H=60$ horizon.
   * *Verification*: Checks if the model avoids out-of-distribution drift. As GPR decays, the router must shift weight back to the GRU expert ($w_2 \to 0.75$), and the residual scaling mechanism must bound the maximum error:
     $$\text{MAPE}_{H60} \le 5.15\%$$
     This prevents Type D temporal smearing and performance collapse.

---

## 5. Analysis & Formulations for `docs/research_os/stage10_econometric_validation.md`

To establish econometric validity, all statistical testing and effect size formulas are specified in LaTeX suitable for peer-reviewed journal submission.

### 5.1 Diebold-Mariano Test with Newey-West HAC Correction

To evaluate the statistical significance of GUM-Net's forecasting accuracy improvement over baseline models under autocorrelation, we implement the Diebold-Mariano (DM) test.

Let $e_{1,t+H|t}$ and $e_{2,t+H|t}$ be the $H$-step ahead forecast residuals of GUM-Net and a candidate baseline model, respectively. The loss differential series $d_t$ is defined as:

$$d_t = \mathcal{L}(e_{1,t+H|t}) - \mathcal{L}(e_{2,t+H|t})$$

Where $\mathcal{L}(\cdot)$ represents the loss function (absolute error $|e|$ for MAE, or squared error $e^2$ for MSE). The null hypothesis of equal predictive accuracy is:

$$H_0: \mathbb{E}[d_t] = 0$$

Against the one-sided alternative hypothesis that GUM-Net is statistically superior:

$$H_1: \mathbb{E}[d_t] < 0$$

The Diebold-Mariano test statistic is defined as:

$$DM = \frac{\bar{d}}{\sqrt{\hat{\sigma}^2_{\bar{d}}}} \xrightarrow{d} \mathcal{N}(0, 1)$$

Where $\bar{d}$ is the sample mean loss differential:

$$\bar{d} = \frac{1}{T} \sum_{t=1}^{T} d_t$$

And $\hat{\sigma}^2_{\bar{d}}$ is the Newey-West heteroskedasticity and autocorrelation consistent (HAC) variance estimator:

$$\hat{\sigma}^2_{\bar{d}} = \frac{1}{T} \left[ \hat{\gamma}_0 + 2 \sum_{k=1}^{J} \left( 1 - \frac{k}{J+1} \right) \hat{\gamma}_k \right]$$

Where:
* $\hat{\gamma}_k$ is the sample autocovariance at lag $k$:
  $$\hat{\gamma}_k = \frac{1}{T} \sum_{t=k+1}^{T} \left(d_t - \bar{d}\right) \left(d_{t-k} - \bar{d}\right)$$
* The truncation lag (bandwidth limit) $J$ is set to correct for overlapping forecast correlations:
  $$J = \min\left(H - 1, \left\lfloor 1.2 \cdot T^{1/3} \right\rfloor\right)$$
  To ensure first-order autocorrelation correction at $H=1$, we enforce $J \ge 1$.

### 5.2 Model Confidence Set (MCS) Superior Set Selection ($\alpha = 0.05$)

To isolate the subset of superior models from the initial set of candidate baselines $\mathcal{M}_0$ (where $|\mathcal{M}_0| = 32$) without pairwise comparison bias, we execute the Model Confidence Set (Hansen et al., 2011) procedure at a significance level of $\alpha = 0.05$.

The MCS procedure iteratively tests the null hypothesis of Equal Predictive Ability (EPA) for the subset $\mathcal{M} \subseteq \mathcal{M}_0$:

$$H_{0, \mathcal{M}}: \mathbb{E}[d_{ij, t}] = 0 \quad \forall i, j \in \mathcal{M}$$

Where $d_{ij, t} = \mathcal{L}(e_{i,t}) - \mathcal{L}(e_{j,t})$ is the loss differential between model $i$ and model $j$ at time $t$. We utilize the $T_{\max}$ test statistic:

$$T_{\max} = \max_{i \in \mathcal{M}} t_i$$

Where $t_i$ is the studentized performance of model $i$ relative to the average of all other models in the active set $\mathcal{M}$:

$$t_i = \frac{\bar{d}_{i\cdot}}{\sqrt{\widehat{\text{Var}}\left(\bar{d}_{i\cdot}\right)}}$$

Here, $\bar{d}_{i\cdot}$ is the mean loss differential of model $i$:

$$\bar{d}_{i\cdot} = \frac{1}{|\mathcal{M}| - 1} \sum_{j \in \mathcal{M} \setminus \{i\}} \bar{d}_{ij}$$

$$\bar{d}_{ij} = \frac{1}{T} \sum_{t=1}^{T} d_{ij, t}$$

The distribution of $T_{\max}$ and the variance estimator $\widehat{\text{Var}}\left(\bar{d}_{i\cdot}\right)$ are estimated using a **Stationary Block Bootstrap** (Politis & Romano, 1994) with $B = 1000$ bootstrap iterations and an adaptive block length:

$$b = \lfloor T^{1/4} \rfloor$$

If the bootstrap $p$-value is less than $\alpha = 0.05$, the EPA null hypothesis is rejected, and the worst-performing model $i^*$ is eliminated from $\mathcal{M}$:

$$i^* = \arg\max_{i \in \mathcal{M}} t_i$$

The procedure is repeated until the null hypothesis $H_{0, \mathcal{M}}$ cannot be rejected. The remaining set of models constitutes the superior set $\widehat{\mathcal{M}}_{0.95}^*$.

### 5.3 Non-Parametric Effect Size Metrics

To quantify the magnitude of GUM-Net's performance gains over baseline models without relying on assumptions of normality, we compute Cliff's Delta and Vargha-Delaney $A_{12}$ on the absolute prediction residuals.

#### Cliff's Delta ($\delta$)
Cliff's Delta is a non-parametric effect size measure representing the probability that a random residual from a baseline model ($e_{\text{baseline}}$) is larger than a random residual from GUM-Net ($e_{\text{GUM-Net}}$):

$$\delta = \frac{1}{N_1 N_2} \sum_{i=1}^{N_1} \sum_{j=1}^{N_2} \text{sgn}\left(\left|e_{i, \text{baseline}}\right| - \left|e_{j, \text{GUM-Net}}\right|\right)$$

Where:
* $N_1$ and $N_2$ are the sizes of the residual vectors (number of test instances).
* $\text{sgn}(\cdot)$ is the signum function.
* The effect size thresholds are interpreted as:
  $$\text{Effect Size} = \begin{cases}
  \text{Negligible}, & \text{if } |\delta| < 0.147 \\
  \text{Small}, & \text{if } 0.147 \le |\delta| < 0.330 \\
  \text{Medium}, & \text{if } 0.330 \le |\delta| < 0.474 \\
  \text{Large}, & \text{if } |\delta| \ge 0.474
  \end{cases}$$

#### Vargha-Delaney $A_{12}$
The Vargha-Delaney $A_{12}$ statistic measures the probability of stochastic superiority of GUM-Net over a baseline:

$$A_{12} = \frac{1}{N_1 N_2} \sum_{i=1}^{N_1} \sum_{j=1}^{N_2} \left[ \mathbb{I}\left(\left|e_{i, \text{baseline}}\right| > \left|e_{j, \text{GUM-Net}}\right|\right) + 0.5 \cdot \mathbb{I}\left(\left|e_{i, \text{baseline}}\right| == \left|e_{j, \text{GUM-Net}}\right|\right) \right]$$

Where:
* $\mathbb{I}(\cdot)$ is the indicator function.
* $A_{12} = 0.5$ represents stochastic equality.
* $A_{12} > 0.5$ indicates GUM-Net is stochastically superior (producing smaller errors).
* The effect size thresholds are interpreted as:
  $$\text{Effect Size} = \begin{cases}
  \text{Negligible}, & \text{if } |A_{12} - 0.5| < 0.06 \\
  \text{Small}, & \text{if } 0.06 \le |A_{12} - 0.5| < 0.14 \\
  \text{Medium}, & \text{if } 0.14 \le |A_{12} - 0.5| < 0.21 \\
  \text{Large}, & \text{if } |A_{12} - 0.5| \ge 0.21
  \end{cases}$$
