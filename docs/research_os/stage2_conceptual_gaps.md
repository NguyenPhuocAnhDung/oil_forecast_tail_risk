## CORE_RESEARCH_GAP_MATRIX

# Stage 2: Core Research Gaps & Policy Distribution Mismatch Analysis

This document identifies the core research gaps in the existing literature, classifies a 33-model benchmark taxonomy across 7 paradigms, and provides a detailed mathematical analysis of the "Distribution Mismatch" problem arising from the Vietnamese BOG (Price Stabilization Fund) regulatory policy.

---

## 1. Core Research Gap Matrix & Taxonomy

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

---

## 2. Mathematical Analysis of BOG Policy & Target Distribution

### 2.1 The BOG Policy Mechanics
Vietnamese retail petroleum prices are adjusted at discrete intervals (e.g., every 7 days or 10 days according to regulatory decrees) by the Ministry of Finance and the Ministry of Industry and Trade. The adjusted price $Y_t$ is determined by:

$$Y_t = Y_{t-1} + \Delta Y_t$$

Where the price change $\Delta Y_t$ is computed from the gap between the domestic price $Y_{t-1}$ and the calculated international base import price $P^{\text{base}}_t$, adjusted by the **Price Stabilization Fund (BOG)** intervention $BOG_t$:

$$\Delta Y_t = \begin{cases}
0, & \text{if } |P^{\text{base}}_t - Y_{t-1}| \le \theta_{\text{threshold}} \text{ and } BOG_t \text{ absorbs the difference} \\
P^{\text{base}}_t - Y_{t-1} - BOG_t, & \text{otherwise}
\end{cases}$$

This policy-driven intervention transforms domestic prices into a piece-wise constant step function:

$$Y_t = \sum_{k=1}^{N_t} \beta_k \mathbb{I}(t \ge T_k)$$

Where:
* $T_k$ represent the discrete, regulatory announcement dates.
* $\beta_k$ represents the magnitude of the price jump at adjustment $k$.
* $\mathbb{I}(\cdot)$ is the indicator function.
* $N_t = \sum_k \mathbb{I}(t \ge T_k)$ is the number of adjustments up to time $t$.

---

### 2.2 Target Distribution Formulation
Under regulated oil price regimes and extreme geopolitical shocks, the retail price change distribution displays discrete step transitions combined with high-frequency geopolitical shocks. We model the target distribution $\mathcal{D}_{\text{target}}$ as:

$$\mathcal{D}_{\text{target}} \sim \sum_{k=1}^K C_k \cdot \mathbb{I}(t \in [T_{k-1}, T_k]) + \epsilon_t \cdot \mathbb{I}(GPR_t \ge GPR_{\text{gate}})$$

Where:
* $C_k \in \mathbb{R}$ represents the constant price level set by the regulatory authority during the pricing window $[T_{k-1}, T_k]$.
* $\mathbb{I}(\cdot)$ is the indicator function.
* $T_k$ represent the discrete announcement dates of price adjustments.
* $GPR_t$ is the Geopolitical Risk index at time $t$.
* $GPR_{\text{gate}}$ is the threshold above which geopolitical risk shocks directly affect the domestic pricing distribution.
* $\epsilon_t \sim \mathcal{N}(0, \sigma^2_{\text{shock}})$ represents the high-frequency geopolitical shock term that is added to the retail price change when $GPR_t$ exceeds the threshold.

---

### 2.3 Morphological Mismatch Analysis: $\mathcal{D}_{\text{pretrain}}$ vs. $\mathcal{D}_{\text{target}}$
Traditional foundation models (P6) are pre-trained on datasets that follow a smooth, continuous distribution:

$$\mathcal{D}_{\text{pretrain}} \sim p_{\text{pretrain}}(\Delta y) = \mathcal{N}(\mu, \sigma^2)$$

This continuous probability density function has well-defined, continuous derivatives everywhere. However, the domestic retail price distribution $\mathcal{D}_{\text{target}}$ is a **mixture of a Dirac delta function** at zero (representing the flat steps where price changes are exactly zero) and a continuous distribution of jump sizes:

$$p_{\text{target}}(\Delta Y_t) = (1 - \pi_t) \delta(0) + \pi_t \cdot \mathcal{N}(\mu_{\text{jump}}, \sigma^2_{\text{jump}})$$

Where:
* $\pi_t \in [0, 1]$ is the probability of a regulatory adjustment occurring at day $t$, which increases as a function of geopolitical intensity: $\pi_t = f(GPR_t)$.
* $\delta(0)$ is the Dirac delta function placing a point mass at zero.

The Kullback-Leibler (KL) divergence between the true target distribution $P$ (i.e. $\mathcal{D}_{\text{target}}$) and the pre-trained distribution $Q$ (i.e. $\mathcal{D}_{\text{pretrain}}$) is:

$$D_{KL}(\mathcal{D}_{\text{target}} \parallel \mathcal{D}_{\text{pretrain}}) = \int_{-\infty}^{\infty} p_{\text{target}}(x) \log\left(\frac{p_{\text{target}}(x)}{p_{\text{pretrain}}(x)}\right) dx$$

Because $p_{\text{target}}(x)$ contains a discrete point mass $(1 - \pi_t)\delta(0)$ where $p_{\text{pretrain}}(0) < 1$, the KL divergence is mathematically unbounded:

$$D_{KL}(\mathcal{D}_{\text{target}} \parallel \mathcal{D}_{\text{pretrain}}) \to \infty$$

This unbounded divergence represents the fundamental impossibility of continuous deep learning architectures to align their prediction distributions with regulated step-like targets, leading to **phantom volatility** (predicting small continuous oscillations in flat regions) and **phase lag** (underestimating price jumps at step boundaries).

---

## 3. Strategic Research Gaps

1. **Uniform Joint Embedding Contamination (GAP 1)**: SOTA models project stationary gasoline and non-stationary diesel series into a single joint representation space, leading to signal cross-contamination and loss of forecasting resolution.
2. **Inability to Absorb Geopolitical Shocks (GAP 2)**: Existing models lack localized mathematical shock-absorbers. Under extreme volatility, attention matrices saturate, failing to isolate high-frequency geopolitical spikes.
3. **Horizon-Blind Routing (GAP 3)**: Router weights in existing MoE networks are static across prediction horizons, failing to adapt when routing from short-term momentum horizons ($H=1$) to long-term trend horizons ($H=60$).
4. **Unsound Validation in Regulated Markets (GAP 4)**: Standard validation splits violate temporal dependencies, leading to look-ahead leakage. Evaluations rely on simple average metrics, ignoring the severe autocorrelation of errors in regulated markets.
5. **Distribution Mismatch under BOG Policy (GAP 5)**: Continuous activation functions in traditional models are structurally incapable of fitting the step-like, discrete price trajectories governed by the BOG policy, inducing phantom volatility and phase lag.

---

## 4. GUM-Net Solution Architecture
To resolve the Distribution Mismatch, GUM-Net integrates three specific components:
1. **Target Reframing**: By forecasting the cumulative log return $R_{t \to t+H}$ instead of price levels, the model learns the change scale.
2. **GPR Hard-Thresholding Filter**: To eliminate phantom volatility in flat regions, GUM-Net filters out low-intensity geopolitical risk signals:
   $$GPR_t^{\text{filtered}} = \text{sgn}(GPR_t) \cdot \max(0, |GPR_t| - 120)$$
   This ensures that small, daily geopolitical fluctuations do not trigger false adjustments in the Wavelet-KAN expert.
3. **Wavelet-KAN Localized Activation**: Mexican Hat wavelets have localized compact support, allowing the network to activate high-frequency adjustments during geopolitical spikes without destabilizing the flat forecasts during calm periods.
