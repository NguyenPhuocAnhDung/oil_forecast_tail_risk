# Academic Analysis Report: Milestone C Updates for GUM-Net Research

**Author**: teamwork_preview_explorer (Explorer 1)  
**Date**: 2026-07-17  
**Working Directory**: `/data/quyhv/oil_forecast_tail_risk/.agents/explorer_msC_1`  
**Mission**: Perform a detailed academic analysis of the 5 reports in `docs/research_os/` to prepare for Milestone C updates.

---

## 1. Analysis of `docs/research_os/stage2_conceptual_gaps.md`

### 1.1 SOTA Taxonomy & Technical Gap Matrix (33 Models across 7 Paradigms)
To establish a rigorous theoretical benchmark, we classify the 33 models (consisting of 11 historical baselines and 22 modern SOTAs) into 7 core paradigms, detailing the structural limitation of each paradigm under regulated oil price regimes and extreme geopolitical shocks:

| Paradigm ID | Paradigm Name | Representative Models (33 total) | Core Architectural Philosophy | Critical Vulnerability & Technical Gaps |
| :--- | :--- | :--- | :--- | :--- |
| **P1** | **Linear & Decomp** | DLinear, RLinear, LTSF_Linear, NBEATS, NHits | Bypasses complex attention mappings. Uses linear projections coupled with trend/seasonal decomposition or backward/forward residual mappings. | **Fixed Linear Projection Flaw**: Assumes linear state transitions. Fails to capture non-linear, dynamic policy shifts and asymmetric price adjustment lags under the Vietnamese BOG regime, leading to *Regime Delay (Failure Type B)*. |
| **P2** | **Dense Attention** | PatchTST, TFT, Autoformer, FedFormer, Informer, Reformer | Maps time series variables or patches into dense tokens and computes global pairwise attention matrices ($Q, K, V$). | **Attention Saturation & Macro-Noise Overfitting**: Attention logits saturate and collapse under extreme out-of-distribution (OOD) exogenous spikes ($GPR_t > 200$), smoothing out local shock peaks. |
| **P3** | **Inverted** | iTransformer, UniTS, TimeXer, Crossformer, CARD | Inverts the mapping to treat channels as tokens and time steps as features, computing attention across variables. | **Local Temporal Dynamics Neglect**: By modeling channel interactions globally, it fails to capture localized, high-frequency temporal dynamics during sudden structural breaks, resulting in *Overshoot (Failure Type C)*. |
| **P4** | **Frequency** | TimesNet, TimeMixer, TTM, FITS, CoST | Maps 1D series into the frequency domain (e.g., via FFT or multi-periodic 2D folding) to capture overlapping cycles. | **Gibbs Phenomenon & Spectral Leakage**: Forcing step-like constant intervals (BOG price steps) into the frequency domain results in mathematical smearing of sudden adjustments and severe phase lag. |
| **P5** | **State Space (SSM)** | TimeMachine, S_Mamba, MambaFormer, BiMamba | Formulates sequences as continuous linear state-space models using selective scanning (Mamba). | **Linear Markovian State Assumption**: The continuous selective scan mechanism cannot isolate or adapt to high-frequency, non-linear GPR impulse shocks without parameter saturation. |
| **P6** | **Foundation** | Chronos, TimesFM, Moirai, Lag_Llama, TEMPO, GPT4TS | Zero-shot time-series forecasters pre-trained on massive, diverse global datasets. | **Extrapolation Hallucination**: Pre-trained on smooth, continuous, global IID datasets. Suffers from severe distribution shift and phase misalignment when applied to local, highly regulated domestic retail price targets. |
| **P7** | **Sparse MoE** | Time_MoE, Gated_TabNet | Dynamically routes tokens or variables to sparse expert sub-networks via routing gates. | **Static Token-Level Routing**: Gating routers operate without conditioning on exogenous physical drivers (such as GPR), failing to adapt the routing behavior during structural crises. |

### 1.2 Target Distribution LaTeX Equation
The regulated domestic retail price changes exhibit discrete step transitions combined with high-frequency geopolitical shocks. We model the target distribution $\mathcal{D}_{\text{target}}$ as:

$$\mathcal{D}_{\text{target}} \sim \sum_{k=1}^K C_k \cdot \mathbb{I}(t \in [T_{k-1}, T_k]) + \epsilon_t \cdot \mathbb{I}(GPR_t \ge GPR_{\text{gate}})$$

Where:
* $C_k \in \mathbb{R}$ represents the constant price level set by the regulatory authority during the pricing window $[T_{k-1}, T_k]$.
* $\mathbb{I}(\cdot)$ is the indicator function.
* $T_k$ represent the discrete announcement dates of price adjustments.
* $GPR_t$ is the Geopolitical Risk index at time $t$.
* $GPR_{\text{gate}}$ is the threshold above which geopolitical risk shocks directly affect the domestic pricing distribution.
* $\epsilon_t \sim \mathcal{N}(0, \sigma^2_{\text{shock}})$ represents the high-frequency geopolitical shock term that is added to the retail price change when $GPR_t$ exceeds the threshold.

### 1.3 Morphological Mismatch Analysis: $\mathcal{D}_{\text{pretrain}}$ vs. $\mathcal{D}_{\text{target}}$
Traditional foundation models (P6) are pre-trained on datasets that follow a smooth, continuous distribution:

$$\mathcal{D}_{\text{pretrain}} \sim p_{\text{pretrain}}(\Delta y) = \mathcal{N}(\mu, \sigma^2)$$

This continuous probability density function has well-defined, continuous derivatives everywhere. However, the domestic retail price distribution $\mathcal{D}_{\text{target}}$ is a **mixture of a Dirac delta function** at zero (representing the flat steps where price changes are exactly zero) and a continuous distribution of jump sizes:

$$p_{\text{target}}(\Delta Y_t) = (1 - \pi_t) \delta(0) + \pi_t \cdot \mathcal{N}(\mu_{\text{jump}}, \sigma^2_{\text{jump}})$$

Where:
* $\pi_t \in [0, 1]$ is the probability of a regulatory adjustment occurring at day $t$, which increases as a function of geopolitical intensity: $\pi_t = f(GPR_t)$.
* $\delta(0)$ is the Dirac delta function placing a point mass at zero.

The Kullback-Leibler (KL) divergence between the true target distribution $P$ and the pre-trained distribution $Q$ is:

$$D_{KL}(\mathcal{D}_{\text{target}} \parallel \mathcal{D}_{\text{pretrain}}) = \int_{-\infty}^{\infty} p_{\text{target}}(x) \log\left(\frac{p_{\text{target}}(x)}{p_{\text{pretrain}}(x)}\right) dx$$

Because $p_{\text{target}}(x)$ contains a discrete point mass $(1 - \pi_t)\delta(0)$ where $p_{\text{pretrain}}(0) < 1$, the KL divergence is mathematically unbounded:

$$D_{KL}(\mathcal{D}_{\text{target}} \parallel \mathcal{D}_{\text{pretrain}}) \to \infty$$

This unbounded divergence represents the fundamental impossibility of continuous deep learning architectures to align their prediction distributions with regulated step-like targets, leading to **phantom volatility** (predicting small continuous oscillations in flat regions) and **phase lag** (underestimating price jumps at step boundaries).

### 1.4 Strategic Research Gaps
1. **Uniform Joint Embedding Contamination (GAP 1)**: SOTA models project stationary gasoline and non-stationary diesel series into a single joint representation space, leading to signal cross-contamination and loss of forecasting resolution.
2. **Inability to Absorb Geopolitical Shocks (GAP 2)**: Existing models lack localized mathematical shock-absorbers. Under extreme volatility, attention matrices saturate, failing to isolate high-frequency geopolitical spikes.
3. **Horizon-Blind Routing (GAP 3)**: Router weights in existing MoE networks are static across prediction horizons, failing to adapt when routing from short-term momentum horizons ($H=1$) to long-term trend horizons ($H=60$).
4. **Unsound Validation in Regulated Markets (GAP 4)**: Standard validation splits violate temporal dependencies, leading to look-ahead leakage. Evaluations rely on simple average metrics, ignoring the severe autocorrelation of errors in regulated markets.
5. **Distribution Mismatch under BOG Policy (GAP 5)**: Continuous activation functions in traditional models are structurally incapable of fitting the step-like, discrete price trajectories governed by the BOG policy, inducing phantom volatility and phase lag.

---

## 2. Analysis of `docs/research_os/stage5_hypothesis_design.md`

### 2.1 Four-Layer Experimental Architecture Blueprint (Tầng 1-4)
To address the conceptual gaps, GUM-Net is designed as a four-layer theory-informed architecture:

#### Tầng 1: Chuyên gia cơ sở (Base Experts)
* **GUM-Net-Mamba (SSM selective scan expert)**: Swaps the GRU expert with a Mamba State Space Model block to capture long-term sequential dependencies with linear complexity:
  $$h_t = \mathbf{A}_t h_{t-1} + \mathbf{B}_t x_t, \quad y_t = \mathbf{C}_t h_t + \mathbf{D} x_t$$
  $$\mathbf{A}_t = \exp(\Delta_t \mathbf{A})$$
  Where $\mathbf{A}, \mathbf{B}, \mathbf{C}, \mathbf{D}$ are selective parameters computed dynamically from the input $x_t$, and $\Delta_t$ is the step size.
* **GUM-Net-iTrans (Inverted attention expert)**: Swaps the CNN expert with an inverted transformer block, projecting individual time series independently:
  $$\mathbf{T}_i = \text{Linear}(X_{:,i}) \quad \forall i \in [1, D]$$
  $$\mathbf{E} = \text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V})$$
  Where $\mathbf{Q}, \mathbf{K}, \mathbf{V}$ are computed from channel-independent projections $\mathbf{T}_i$, capturing cross-variable interactions rather than temporal coordinates.
* **GUM-Net-Wavelet (Wavelet KAN expert)**: Employs a localized activation function on KAN edges using Mexican Hat wavelets:
  $$\Phi_{j,k}(x) = \left(1 - \left(\frac{x-\mu_k}{\sigma_j}\right)^2\right)\exp\!\left(-0.5\left(\frac{x-\mu_k}{\sigma_j}\right)^2\right)$$
  Where $\mu_k$ is the translation parameter and $\sigma_j$ is the scale parameter updated via gradient descent.

#### Tầng 2: Bộ lọc (Filtering & Tokenization Layers)
* **GUM-Net-Patch (Semantic Patch-attention)**: Tokenizes the input sequence into patches to preserve local semantic context before projecting to attention layers:
  $$X_p = \text{PatchPartition}(X) \in \mathbb{R}^{P \times (L \cdot D)}$$
  $$\mathbf{H}_p = \text{Attention}(X_p W_Q, X_p W_K, X_p W_V)$$
* **GUM-Net-Fourier (FFT multi-period mixing)**: Applies Fast Fourier Transform to extract multi-periodic frequency components and filter noise:
  $$\mathcal{F}(X) = \text{FFT}(X)$$
  $$X_{\text{freq}} = \text{MLP}(\mathcal{F}(X))$$
  $$X_{\text{filtered}} = \text{IFFT}(X_{\text{freq}})$$

#### Tầng 3: Generative/Causal (Probabilistic & Relational Layers)
* **GUM-Net-Diffusion (DDPM probabilistic)**: Formulates the forecasting head as a conditional Denoising Diffusion Probabilistic Model to capture tail-risk distribution:
  $$p_\theta(y_{t-1}|y_t, x) = \mathcal{N}(y_{t-1}; \mu_\theta(y_t, t, x), \Sigma_\theta(y_t, t, x))$$
* **GUM-Net-Graph (ST-GCN causal graph)**: Models oil price transmission across international benchmarks and domestic retail markets using a Spatio-Temporal Graph Convolutional Network on a causal graph:
  $$G = (V, E), \quad V = \{\text{Brent}, \text{WTI}, \text{Platts}, \text{Retail}\}$$
  $$H^{(l+1)} = \sigma\left(\tilde{D}^{-1/2} \tilde{A} \tilde{D}^{-1/2} H^{(l)} W^{(l)}\right)$$
  Where $\tilde{A} = A + I_N$ is the adjacency matrix of the causal oil chain.
* **GUM-Net-RL (PPO Routing Controller)**: Uses a Proximal Policy Optimization reinforcement learning agent to dynamically adjust the routing gate parameter based on an asymmetric sign loss reward:
  $$\mathcal{R}_t = - \left( |y_t - \hat{y}_t| + \beta \cdot \mathbb{I}(\text{sgn}(y_t - y_{t-1}) \neq \text{sgn}(\hat{y}_t - y_{t-1})) \right)$$

#### Tầng 4: Routing (Ensemble & Fusion Gating Layers)
* **GUM-Net-MoE-Sparse (Top-K Switch Router)**: Routes inputs to a sparse subset of experts (typically $K=1$ or $K=2$) to save compute and prevent parameter interference:
  $$w(x) = \text{Softmax}\left(\text{KeepTopK}\left(H(x), K\right)\right)$$
  $$H(x) = W_r x + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \sigma^2)$$
* **GUM-Net-Fusion (Dynamic GPR-conditioned temperature-scaled gate with residual scaling)**: Fuses all base experts using a dynamic gating router with temperature scaling:
  $$\tau_t = \tau_0 \cdot \exp\left(-\gamma \cdot \left[ |GPR_t| + \beta \cdot |\Delta GPR_t| \right]\right)$$
  $$w_i(x_t) = (1 - \lambda) \cdot \frac{\exp\left(\frac{g_i(x_t)}{\tau_t}\right)}{\sum_{j=1}^3 \exp\left(\frac{g_j(x_t)}{\tau_t}\right)} + \lambda \cdot \frac{1}{3}$$
  Where $\lambda = 0.1$ is the residual scaling shortcut ensuring gradient flow $\ge \frac{\lambda}{3}$ for each expert.

### 2.2 Falsifiable Research Questions & Hypotheses
* **RQ1: Stationarity-Aware Decoupled Modelling**
  * *Research Question*: Does separate modeling of stationary co-products (gasoline/xăng) and non-stationary, trend-dominated co-products (diesel/dầu) prevent cross-contamination and yield statistically superior predictions compared to joint modeling?
  - *Null Hypothesis ($H_0$)*:
    $$\text{MAE}_{\text{decoupled}} \ge \text{MAE}_{\text{joint}} \quad \text{and} \quad R^2_{\text{decoupled}} \le R^2_{\text{joint}}$$
  - *Alternative Hypothesis ($H_1$)*:
    $$\text{MAE}_{\text{decoupled}} < \text{MAE}_{\text{joint}} \quad \text{and} \quad R^2_{\text{decoupled}} > R^2_{\text{joint}}$$
* **RQ2: Wavelet-KAN Shock Absorption & GPR Filtering**
  * *Research Question*: Does the integration of a localized Wavelet-KAN expert with Mexican Hat wavelets and GPR hard-thresholding improve forecasting robustness during geopolitical crises compared to standard MLP or B-spline KAN?
  - *Null Hypothesis ($H_0$)*:
    $$\text{DA}_{\text{Wavelet-KAN}} \le \text{DA}_{\text{MLP/B-Spline}} \quad \text{and} \quad \text{MAPE}_{\text{crisis, Wavelet-KAN}} \ge \text{MAPE}_{\text{crisis, MLP/B-Spline}}$$
  - *Alternative Hypothesis ($H_1$)*:
    $$\text{DA}_{\text{Wavelet-KAN}} > \text{DA}_{\text{MLP/B-Spline}} \quad \text{and} \quad \text{MAPE}_{\text{crisis, Wavelet-KAN}} < \text{MAPE}_{\text{crisis, MLP/B-Spline}}$$
* **RQ3: Horizon-Aware Gating & Temperature Scaling**
  * *Research Question*: Does a GPR-conditioned temperature-scaled dynamic router outperform static routing ensembles or standard softmax routing across different forecast horizons?
  - *Null Hypothesis ($H_0$)*:
    $$\mathcal{L}_{\text{dynamic\_routing}} \ge \mathcal{L}_{\text{static\_ensemble}}$$
  - *Alternative Hypothesis ($H_1$)*:
    $$\mathcal{L}_{\text{dynamic\_routing}} < \mathcal{L}_{\text{static\_ensemble}}$$
* **RQ4: Extrapolation Error Bounding (Residual Scaling)**
  * *Research Question*: Does the Sigmoid-based Residual Scaling mechanism limit extreme extrapolation errors (MAPE) at long horizons ($H = 60$) without degrading short-term accuracy?
  - *Null Hypothesis ($H_0$)*:
    $$\text{MAPE}_{H60, \text{scaling}} \ge \text{MAPE}_{H60, \text{raw}} \quad \text{or} \quad \text{MAE}_{H1, \text{scaling}} > \text{MAE}_{H1, \text{raw}}$$
  - *Alternative Hypothesis ($H_1$)*:
    $$\text{MAPE}_{H60, \text{scaling}} < \text{MAPE}_{H60, \text{raw}} \quad \text{and} \quad \text{MAE}_{H1, \text{scaling}} \approx \text{MAE}_{H1, \text{raw}}$$

---

## 3. Analysis of `docs/research_os/stage7_baseline_taxonomy.md`

### 3.1 Benchmark Selection and Theoretical Contrast Matrix (33 Models)
The 33 models evaluated in the extended benchmark suite are mapped to the 7 paradigms, providing a clear scientific contrast of their theoretical strengths and failure modes:

| Paradigm | Architectural Philosophy | Key Representatives | Extrapolation Handling | Critical Vulnerability under Geopolitical Shocks |
| :--- | :--- | :--- | :--- | :--- |
| **P1: Linear & Decomp** | Direct projection via linear matrices, separating trend and season components. | DLinear, RLinear, LTSF_Linear, NBEATS, NHits | Linear trend extension | Completely fails to capture discrete, asymmetric price steps and non-linear shifts. |
| **P2: Transformer** | Dense attention maps across temporal coordinates. | PatchTST, TFT, Autoformer, FedFormer, Informer, Reformer | Softmax-bound projection | Attention weights saturate under spikes, leading to performance collapse. |
| **P3: Inverted** | Treating variables as tokens and time steps as features to model cross-correlations. | iTransformer, UniTS, TimeXer, Crossformer, CARD | Channel-independent mapping | Smoothes out localized temporal breaks and sudden price adjustments. |
| **P4: Frequency** | Projects time steps to frequency coefficients via FFT. | TimesNet, TimeMixer, TTM, FITS, CoST | Periodic repetition | Gibbs phenomenon smears sharp regulatory price jumps. |
| **P5: State Space (SSM)** | Continuous linear state-space equations with selective gating. | TimeMachine, S_Mamba, MambaFormer, BiMamba | Continuous state transition | Strict linear state transitions saturate during brief, extreme shocks. |
| **P6: Foundation** | Pre-trained zero-shot forecasters on large global datasets. | Chronos, TimesFM, Moirai, Lag_Llama, TEMPO, GPT4TS | Autoregressive generation | High extrapolation hallucination due to distribution shifts in local markets. |
| **P7: Sparse MoE** | Routing individual tokens to subset experts. | Time_MoE, Gated_TabNet | Weighted average combination | Static routing ignores exogenous macroeconomic states (like GPR). |

### 3.2 Scientific Integrity Clause (Requirement R8)
To prevent publication bias and enforce strict scientific integrity, the benchmark framework incorporates the verbatim **Requirement R8 Rule**:

> *"Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu."*

This rule guarantees that if GUM-Net is stochastically outperformed by SOTA baselines (Time_MoE, TimesFM, or S_Mamba) under worst-case scenarios, the metrics are reported transparently and GUM-Net is not artificially inflated.

### 3.3 Python Dispatch Registry Code
To support modular, automated benchmark execution across all 33 baseline models and 11 GUM-Net variants, we propose the following Python dispatch architecture:

```python
"""
src/models/benchmark_registry.py
Benchmark model registry mapping string identifiers to PyTorch modules.
Handles both native deep learning baselines and offline foundation model wrappers.
"""
import torch
import torch.nn as nn
from typing import Dict, Type, Any

class SOTAModelWrapper(nn.Module):
    """
    Offline wrapper for foundation models (Chronos, TimesFM, Moirai, etc.)
    and heavy SOTAs. Falls back to a projection network on Windows if weights are unavailable.
    """
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.horizon = horizon
        self.seq_len = seq_len
        self.proj = nn.Linear(seq_len * input_dim, horizon * output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input shape: [B, seq_len, input_dim]
        B = x.shape[0]
        x_flat = x.contiguous().view(B, -1)
        out = self.proj(x_flat)
        return out.view(B, self.horizon, self.output_dim)

# Registry dictionary
MODEL_REGISTRY: Dict[str, Type[nn.Module]] = {}

def register_model(name: str):
    """Decorator to register models."""
    def decorator(cls: Type[nn.Module]):
        MODEL_REGISTRY[name] = cls
        return cls
    return decorator

# Example of registrations (Implementers will bind the actual classes here)
# P1: Linear
MODEL_REGISTRY["DLinear"] = SOTAModelWrapper
MODEL_REGISTRY["RLinear"] = SOTAModelWrapper
MODEL_REGISTRY["LTSF_Linear"] = SOTAModelWrapper
MODEL_REGISTRY["NBEATS"] = SOTAModelWrapper
MODEL_REGISTRY["NHits"] = SOTAModelWrapper

# P2: Transformer
MODEL_REGISTRY["PatchTST"] = SOTAModelWrapper
MODEL_REGISTRY["TFT"] = SOTAModelWrapper
MODEL_REGISTRY["Autoformer"] = SOTAModelWrapper
MODEL_REGISTRY["FedFormer"] = SOTAModelWrapper
MODEL_REGISTRY["Informer"] = SOTAModelWrapper
MODEL_REGISTRY["Reformer"] = SOTAModelWrapper

# P3: Inverted
MODEL_REGISTRY["iTransformer"] = SOTAModelWrapper
MODEL_REGISTRY["UniTS"] = SOTAModelWrapper
MODEL_REGISTRY["TimeXer"] = SOTAModelWrapper
MODEL_REGISTRY["Crossformer"] = SOTAModelWrapper
MODEL_REGISTRY["CARD"] = SOTAModelWrapper

# P4: Frequency
MODEL_REGISTRY["TimesNet"] = SOTAModelWrapper
MODEL_REGISTRY["TimeMixer"] = SOTAModelWrapper
MODEL_REGISTRY["TTM"] = SOTAModelWrapper
MODEL_REGISTRY["FITS"] = SOTAModelWrapper
MODEL_REGISTRY["CoST"] = SOTAModelWrapper

# P5: State Space (SSM)
MODEL_REGISTRY["TimeMachine"] = SOTAModelWrapper
MODEL_REGISTRY["S_Mamba"] = SOTAModelWrapper
MODEL_REGISTRY["MambaFormer"] = SOTAModelWrapper
MODEL_REGISTRY["BiMamba"] = SOTAModelWrapper

# P6: Foundation
MODEL_REGISTRY["Chronos"] = SOTAModelWrapper
MODEL_REGISTRY["TimesFM"] = SOTAMOMModel = SOTAModelWrapper
MODEL_REGISTRY["Moirai"] = SOTAModelWrapper
MODEL_REGISTRY["Lag_Llama"] = SOTAModelWrapper
MODEL_REGISTRY["TEMPO"] = SOTAModelWrapper
MODEL_REGISTRY["GPT4TS"] = SOTAModelWrapper

# P7: Sparse MoE
MODEL_REGISTRY["Time_MoE"] = SOTAModelWrapper
MODEL_REGISTRY["Gated_TabNet"] = SOTAModelWrapper

# GUM-Net Variants
MODEL_REGISTRY["GUMNet"] = SOTAModelWrapper
MODEL_REGISTRY["GUMNet_Mamba"] = SOTAModelWrapper
MODEL_REGISTRY["GUMNet_iTrans"] = SOTAModelWrapper
MODEL_REGISTRY["GUMNet_Wavelet"] = SOTAModelWrapper
MODEL_REGISTRY["GUMNet_Patch"] = SOTAModelWrapper
MODEL_REGISTRY["GUMNet_Fourier"] = SOTAModelWrapper
MODEL_REGISTRY["GUMNet_Diffusion"] = SOTAModelWrapper
MODEL_REGISTRY["GUMNet_Graph"] = SOTAModelWrapper
MODEL_REGISTRY["GUMNet_RL"] = SOTAModelWrapper
MODEL_REGISTRY["GUMNet_MoE_Sparse"] = SOTAModelWrapper
MODEL_REGISTRY["GUMNet_Fusion"] = SOTAModelWrapper

def get_model_instance(name: str, cfg: Dict[str, Any]) -> nn.Module:
    """Retrieves instance from registry using the unified config."""
    if name not in MODEL_REGISTRY:
        raise KeyError(f"Model '{name}' is not registered in the benchmark suite.")
    
    model_class = MODEL_REGISTRY[name]
    return model_class(
        input_dim=len(cfg["feature_cols"]),
        output_dim=len(cfg["target_cols"]),
        horizon=cfg["horizon"],
        seq_len=cfg["seq_len"]
    )
```

---

## 4. Analysis of `docs/research_os/stage9_failure_diagnostics.md`

### 4.1 Anti-Fabrication Constraints & Post-experimental Estimation
To enforce maximum academic integrity, we define strict **Anti-Fabrication Constraints**:
* **No Hardcoded Statistical Values**: The reports must not contain hardcoded summary statistics (such as mean values, standard deviations, or correlation coefficients) for simulated or real results.
* **The Post-experimental Estimation Protocol**: All statistical tables and diagnostics must be derived programmatically. The diagnostics code must estimate the parameters directly from the raw out-of-sample forecast residuals $e_{t+H} = Y_{t+H} - \hat{Y}_{t+H|t}$.

### 4.2 Systematic Error Group Typology
To isolate architectural failures, prediction errors are classified into four systematic error groups:

1. **Type A: Trend Miss (Shock Saturation)**
   * *Description*: Underestimation of price jumps during extreme geopolitical spikes.
   * *Mathematical Indicator*: 
     $$Y_{t+H} > \hat{Y}_{t+H|t}^{(q=0.90)} \quad \text{under} \quad GPR_t > 200$$
2. **Type B: Regime Delay (Lagged BOG Adjustments)**
   * *Description*: Phase lag during discrete regulatory price updates.
   * *Mathematical Indicator*: 
     $$\text{Corr}(e_t, e_{t-k}) \gg 0 \quad \text{for } k \in [1, 10] \quad \text{in flat regions, followed by a spike at } T_{\text{announce}}$$
3. **Type C: Overshoot (Macro-Noise Pollution)**
   * *Description*: Forecasting phantom volatility in calm, flat price regimes.
   * *Mathematical Indicator*: 
     $$\text{Var}(\hat{Y}_{t+H|t}) \gg \text{Var}(Y_{t+H}) \approx 0 \quad \text{when} \quad GPR_t < GPR_{\text{gate}}$$
4. **Type D: Policy Plateau (Horizon-Dependent Phase Shift)**
   * *Description*: Temporal lag in predicting turning points as the horizon extends.
   * *Mathematical Indicator*: 
     $$\arg\max_{k} \text{CrossCorr}\left(Y_t, \hat{Y}_{t-k|t-H-k}\right) = d > 0 \quad \text{as } H \to 60$$

### 4.3 Two-Phase Evaluation Protocol (US-Iran 2026 Window)
To test model resilience against structural breaks without leakage, we formulate a two-phase temporal protocol:

```
                          2026 US-IRAN TEMPORAL WINDOW
                                 (01/2026 - 05/2026)
                                          |
                     +--------------------+--------------------+
                     |                                         |
                     v                                         v
         Phase 1: 2026-04-30                       Phase 2: 2026-05-31
      Right-Censored Evaluation                  Worst-Case Robustness
    - Brent surges; GPR spikes (350)           - BOG reserves depleted
    - BOG active: domestic price flat          - Domestic retail price jumps 15%
    - Tests: Phantom volatility control        - Tests: Price jump tracking (No Lag)
```

* **Phase 1: 2026-04-30 Right-Censoring (H60 extrapolation)**: The sequence is truncated at `2026-04-30`. During this phase, Brent crude surges and GPR spikes to 350. However, the domestic BOG is active, keeping retail prices flat. The model is evaluated on its ability to maintain flat predictions and avoid Type C errors (phantom volatility) despite the international crude shock.
* **Phase 2: 2026-05-31 Worst-Case sequence**: The sequence is extended to `2026-05-31`, releasing the ground-truth retail price labels for May 2026. Due to prolonged international high prices, the BOG reserves are depleted, triggering a 15% discrete jump in retail gasoline and diesel prices. The model is evaluated on its ability to predict this sharp step transition without lagging (avoiding Type B and Type D errors).

---

## 5. Analysis of `docs/research_os/stage10_econometric_validation.md`

All mathematical validation equations are formalized in standard LaTeX, optimized for journal publication:

### 5.1 Diebold-Mariano Test with Newey-West HAC Variance Correction
The loss differential series $d_t$ between Model 1 (GUM-Net-Fusion) and Model 2 (Baseline) is defined as:

$$d_t = \mathcal{L}\left(e_{1, t+H|t}\right) - \mathcal{L}\left(e_{2, t+H|t}\right)$$

Where $\mathcal{L}(\cdot)$ is the loss metric (typically $\mathcal{L}(e) = |e|$ for MAE). The null hypothesis of equal predictive accuracy is:

$$H_0: \mathbb{E}[d_t] = 0$$

The one-sided alternative hypothesis proving GUM-Net superiority is:

$$H_1: \mathbb{E}[d_t] < 0$$

The DM statistic is computed as:

$$DM = \frac{\bar{d}}{\sqrt{\hat{\sigma}^2_{\bar{d}}}} \ \sim \ \mathcal{N}(0, 1)$$

Where the mean loss differential is $\bar{d} = \frac{1}{T} \sum_{t=1}^T d_t$, and the heteroskedasticity and autocorrelation consistent (HAC) variance estimator is:

$$\hat{\sigma}^2_{\bar{d}} = \frac{1}{T} \left( \hat{\gamma}_0 + 2 \sum_{k=1}^{J} \left(1 - \frac{k}{J+1}\right) \hat{\gamma}_k \right)$$

The sample autocovariance at lag $k$ is:

$$\hat{\gamma}_k = \frac{1}{T} \sum_{t=k+1}^{T} (d_t - \bar{d})(d_{t-k} - \bar{d})$$

And the truncation lag (bandwidth) $J$ is set to correct for overlapping forecasts:

$$J = \min\left(H - 1, \left\lfloor 1.2 \cdot T^{1/3} \right\rfloor\right)$$

### 5.2 Hansen's Model Confidence Set (MCS) Protocol ($\alpha = 0.05$)
Let $\mathcal{M}_0$ be the initial set of 33 candidate models. The MCS iteratively tests the null hypothesis of Equal Predictive Ability (EPA) for a subset $\mathcal{M} \subset \mathcal{M}_0$ at significance level $\alpha = 0.05$:

$$H_{0, \mathcal{M}}: \mathbb{E}[d_{ij, t}] = 0 \quad \forall i, j \in \mathcal{M}$$

The test statistic $T_{\max}$ is defined as:

$$T_{\max} = \max_{i \in \mathcal{M}} t_{i}$$

The studentized loss $t_{i}$ of model $i$ relative to the average of all other active models is:

$$t_{i} = \frac{\bar{d}_{i\cdot}}{\sqrt{\widehat{\text{Var}}(\bar{d}_{i\cdot})}}$$

Where:
* $\bar{d}_{i\cdot} = \frac{1}{|\mathcal{M}|-1} \sum_{j \in \mathcal{M} \setminus \{i\}} \bar{d}_{ij}$ represents the mean loss differential of model $i$.
* $d_{ij, t} = \mathcal{L}(e_{i,t}) - \mathcal{L}(e_{j,t})$ is the loss differential at time $t$.

The variance $\widehat{\text{Var}}(\bar{d}_{i\cdot})$ is estimated via the **Stationary Block Bootstrap** (Politis & Romano, 1994) using $B = 999$ resamples and adaptive block length $b = \lfloor T^{1/4} \rfloor$. If the bootstrap $p$-value for $H_{0, \mathcal{M}}$ falls below $\alpha = 0.05$, the worst-performing model $i^*$ is eliminated:

$$i^* = \arg\max_{i \in \mathcal{M}} \bar{d}_{i\cdot} \quad \text{where} \quad \bar{d}_{i\cdot} = \frac{1}{T} \sum_{t=1}^{T} d_{i\cdot, t}$$

The loop terminates when $H_{0, \mathcal{M}}$ cannot be rejected, outputting the superior set $\widehat{\mathcal{M}}_{0.95}^*$.

### 5.3 Non-Parametric Effect Size Measures
To quantify the error reduction size without assuming residual normality, we compute two statistics on absolute residuals $|e|$:

#### Cliff's Delta ($\delta$)
Cliff's Delta evaluates the probability that a random prediction error from a baseline model ($X_1$) is larger than a random prediction error from GUM-Net ($X_2$):

$$\delta = \frac{1}{N_1 N_2} \sum_{i=1}^{N_1} \sum_{j=1}^{N_2} \text{sgn}\left(|e_{i, \text{baseline}}| - |e_{j, \text{GUM-Net}}|\right)$$

Where $\text{sgn}(x)$ is the sign function:

$$\text{sgn}(x) = \begin{cases} 1, & x > 0 \\ 0, & x = 0 \\ -1, & x < 0 \end{cases}$$

#### Vargha-Delaney $A_{12}$
The Vargha-Delaney $A_{12}$ statistic measures the probability of stochastic superiority of GUM-Net over a baseline:

$$A_{12} = \frac{1}{N_1 N_2} \sum_{i=1}^{N_1} \sum_{j=1}^{N_2} \left[ \mathbb{I}\left(|e_{i, \text{baseline}}| > |e_{j, \text{GUM-Net}}|\right) + 0.5 \cdot \mathbb{I}\left(|e_{i, \text{baseline}}| == |e_{j, \text{GUM-Net}}|\right) \right]$$

An $A_{12} > 0.5$ indicates that the baseline has a stochastic tendency to yield larger errors than GUM-Net, confirming GUM-Net's superiority.

---

## 6. Recommendations for Implementer Agent

1. **Update `docs/research_os/stage2_conceptual_gaps.md`**:
   * Replace the placeholder matrix with the 33-model taxonomy (Table in Section 1.1).
   * Insert the target distribution equation ($\mathcal{D}_{\text{target}}$) and the Morphological Mismatch analysis (KL divergence divergence to infinity).
   * Update the 5 strategic research gaps.
2. **Update `docs/research_os/stage5_hypothesis_design.md`**:
   * Insert the mathematical descriptions and LaTeX formulations for the 4 layers (Tầng 1-4) and the 10 GUM-Net variants (Mamba, iTrans, Wavelet, Patch, Fourier, Diffusion, Graph, RL, MoE-Sparse, Fusion).
   * Ensure that the 4 RQs (RQ1-RQ4) and the $H_0/H_1$ hypotheses match Section 2.2 exactly.
3. **Update `docs/research_os/stage7_baseline_taxonomy.md`**:
   * Embed the theoretical contrast matrix (Table in Section 3.1).
   * Include the verbatim scientific integrity clause (R8 rule).
   * Propose the Python dispatch registry code (Section 3.3).
4. **Update `docs/research_os/stage9_failure_diagnostics.md`**:
   * Detail the anti-fabrication guidelines (zero hardcoding, estimation protocol).
   * Outline the 4 systematic error groups (Types A, B, C, D) and the 2-phase validation protocol (Phase 1: April 30; Phase 2: May 31).
5. **Update `docs/research_os/stage10_econometric_validation.md`**:
   * Check all LaTeX formatting for DM-HAC (Newey-West), MCS ($\alpha = 0.05$), Cliff's Delta, and Vargha-Delaney $A_{12}$ to ensure publication-ready rendering.
