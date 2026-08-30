## EXPERIMENTAL_ARCHITECTURE_BLUEPRINT

# Stage 5: Falsifiable Design & Hypothesis Specifications

This document outlines the formal experimental architecture blueprint and hypothesis design for GUM-Net. It establishes four core research questions ($RQ_1$ to $RQ_4$), formulates their corresponding null ($H_0$) and alternative ($H_1$) hypotheses, and provides rigorous mathematical specifications in LaTeX.

---

## 1. Four-Layer Experimental Architecture Blueprint (Tầng 1-4)

To address the conceptual and mathematical gaps of existing SOTA paradigms, GUM-Net is designed as a four-layer theory-informed architecture mapping the 10 variants:

### 1.1 Tầng 1: Chuyên gia cơ sở (Base Experts)
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

### 1.2 Tầng 2: Bộ lọc (Filtering & Tokenization Layers)
* **GUM-Net-Patch (Semantic Patch-attention)**: Tokenizes the input sequence into patches to preserve local semantic context before projecting to attention layers:
  $$X_p = \text{PatchPartition}(X) \in \mathbb{R}^{P \times (L \cdot D)}$$
  $$\mathbf{H}_p = \text{Attention}(X_p W_Q, X_p W_K, X_p W_V)$$
* **GUM-Net-Fourier (FFT multi-period mixing)**: Applies Fast Fourier Transform to extract multi-periodic frequency components and filter noise:
  $$\mathcal{F}(X) = \text{FFT}(X)$$
  $$X_{\text{freq}} = \text{MLP}(\mathcal{F}(X))$$
  $$X_{\text{filtered}} = \text{IFFT}(X_{\text{freq}})$$

### 1.3 Tầng 3: Generative/Causal (Probabilistic & Relational Layers)
* **GUM-Net-Diffusion (DDPM probabilistic)**: Formulates the forecasting head as a conditional Denoising Diffusion Probabilistic Model to capture tail-risk distribution:
  $$p_\theta(y_{t-1}|y_t, x) = \mathcal{N}(y_{t-1}; \mu_\theta(y_t, t, x), \Sigma_\theta(y_t, t, x))$$
* **GUM-Net-Graph (ST-GCN causal graph)**: Models oil price transmission across international benchmarks and domestic retail markets using a Spatio-Temporal Graph Convolutional Network on a causal graph:
  $$G = (V, E), \quad V = \{\text{Brent}, \text{WTI}, \text{Platts}, \text{Retail}\}$$
  $$H^{(l+1)} = \sigma\left(\tilde{D}^{-1/2} \tilde{A} \tilde{D}^{-1/2} H^{(l)} W^{(l)}\right)$$
  Where $\tilde{A} = A + I_N$ is the adjacency matrix of the causal oil chain.
* **GUM-Net-RL (PPO Routing Controller)**: Uses a Proximal Policy Optimization reinforcement learning agent to dynamically adjust the routing gate parameter based on an asymmetric sign loss reward:
  $$\mathcal{R}_t = - \left( |y_t - \hat{y}_t| + \beta \cdot \mathbb{I}(\text{sgn}(y_t - y_{t-1}) \neq \text{sgn}(\hat{y}_t - y_{t-1})) \right)$$

### 1.4 Tầng 4: Routing (Ensemble & Fusion Gating Layers)
* **GUM-Net-MoE-Sparse (Top-K Switch Router)**: Routes inputs to a sparse subset of experts (typically $K=1$ or $K=2$) to save compute and prevent parameter interference:
  $$w(x) = \text{Softmax}\left(\text{KeepTopK}\left(H(x), K\right)\right)$$
  $$H(x) = W_r x + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \sigma^2)$$
* **GUM-Net-Fusion (Dynamic GPR-conditioned temperature-scaled gate with residual scaling)**: Fuses all base experts using a dynamic gating router with temperature scaling:
  $$\tau_t = \tau_0 \cdot \exp\left(-\gamma \cdot \left[ |GPR_t| + \beta \cdot |\Delta GPR_t| \right]\right)$$
  $$w_i(x_t) = (1 - \lambda) \cdot \frac{\exp\left(\frac{g_i(x_t)}{\tau_t}\right)}{\sum_{j=1}^3 \exp\left(\frac{g_j(x_t)}{\tau_t}\right)} + \lambda \cdot \frac{1}{3}$$
  Where $\lambda = 0.1$ is the residual scaling shortcut ensuring gradient flow $\ge \frac{\lambda}{3}$ for each expert.

---

## 2. Falsifiable Hypotheses & Research Questions

### RQ1: Stationarity-Aware Decoupled Modelling
* **Research Question**: Does separate modeling of stationary co-products (gasoline/xăng) and non-stationary, trend-dominated co-products (diesel/dầu) prevent cross-contamination and yield statistically superior predictions compared to joint modeling?
* **Null Hypothesis ($H_0$)**:
  $$\text{MAE}_{\text{decoupled}} \ge \text{MAE}_{\text{joint}} \quad \text{and} \quad R^2_{\text{decoupled}} \le R^2_{\text{joint}}$$
  There is no statistically significant improvement in forecasting accuracy or explained variance when separating products into distinct modeling pipelines.
* **Alternative Hypothesis ($H_1$)**:
  $$\text{MAE}_{\text{decoupled}} < \text{MAE}_{\text{joint}} \quad \text{and} \quad R^2_{\text{decoupled}} > R^2_{\text{joint}}$$
  Decoupling gasoline and diesel prevents cross-contamination of trend and mean-reverting signals, yielding lower errors and higher $R^2$, particularly for the trend-dominated diesel products.

### RQ2: Wavelet-KAN Shock Absorption & GPR Filtering
* **Research Question**: Does the integration of a localized Wavelet-KAN expert with Mexican Hat wavelets and GPR hard-thresholding improve forecasting robustness during geopolitical crises compared to standard MLP or B-spline KAN?
* **Null Hypothesis ($H_0$)**:
  $$\text{DA}_{\text{Wavelet-KAN}} \le \text{DA}_{\text{MLP/B-Spline}} \quad \text{and} \quad \text{MAPE}_{\text{crisis, Wavelet-KAN}} \ge \text{MAPE}_{\text{crisis, MLP/B-Spline}}$$
  Incorporating Wavelet-KAN with GPR filtering does not improve Directional Accuracy (DA) or reduce mean absolute percentage errors during high-volatility tail-risk windows.
* **Alternative Hypothesis ($H_1$)**:
  $$\text{DA}_{\text{Wavelet-KAN}} > \text{DA}_{\text{MLP/B-Spline}} \quad \text{and} \quad \text{MAPE}_{\text{crisis, Wavelet-KAN}} < \text{MAPE}_{\text{crisis, MLP/B-Spline}}$$
  The localized compact support of Mexican Hat wavelets, combined with GPR threshold gating, effectively isolates and dampens geopolitical shocks, leading to statistically higher directional accuracy and lower error peaks during crisis windows.

### RQ3: Horizon-Aware Gating & Temperature Scaling
* **Research Question**: Does a GPR-conditioned temperature-scaled dynamic router outperform static routing ensembles or standard softmax routing across different forecast horizons?
* **Null Hypothesis ($H_0$)**:
  $$\mathcal{L}_{\text{dynamic\_routing}} \ge \mathcal{L}_{\text{static\_ensemble}}$$
  Adjusting softmax temperature and gating weights dynamically using GPR intensity yields no statistical improvement over a static average ensemble of the three experts.
* **Alternative Hypothesis ($H_1$)**:
  $$\mathcal{L}_{\text{dynamic\_routing}} < \mathcal{L}_{\text{static\_ensemble}}$$
  Dynamic gating weights adaptively route signals to CNN for short horizons (momentum) and to GRU/KAN for long horizons (trends and shocks), resulting in statistically lower losses across all horizons.

### RQ4: Extrapolation Error Bounding (Residual Scaling)
* **Research Question**: Does the Sigmoid-based Residual Scaling mechanism limit extreme extrapolation errors (MAPE) at long horizons ($H = 60$) without degrading short-term accuracy?
* **Null Hypothesis ($H_0$)**:
  $$\text{MAPE}_{H60, \text{scaling}} \ge \text{MAPE}_{H60, \text{raw}} \quad \text{or} \quad \text{MAE}_{H1, \text{scaling}} > \text{MAE}_{H1, \text{raw}}$$
  Residual scaling fails to bound the maximum MAPE at long horizons, or it introduces a bias that degrades short-term forecasting accuracy.
* **Alternative Hypothesis ($H_1$)**:
  $$\text{MAPE}_{H60, \text{scaling}} < \text{MAPE}_{H60, \text{raw}} \quad \text{and} \quad \text{MAE}_{H1, \text{scaling}} \approx \text{MAE}_{H1, \text{raw}}$$
  Residual scaling acts as a mathematical "emergency brake" that bounds out-of-distribution extrapolation errors at $H=60$ while remaining inactive and harmless during short-term forecasting ($H=1$).

---

## 3. Rigorous Mathematical Specifications

### 3.1 Dynamic Gating Router Formulations
Let $x_t \in \mathbb{R}^d$ be the concatenated representation vector at time $t$:
$$x_t = [f_{\text{cnn}}(X_{t}) \parallel f_{\text{gru}}(X_{t}) \parallel f_{\text{kan}}(X_{t}) \parallel \text{Pos}_h \parallel GPR_t^{\text{filtered}}]$$
Where $\text{Pos}_h$ is the $d_{\text{pos}}$-dimensional Horizon Positional Embedding, and $GPR_t^{\text{filtered}}$ is the hard-thresholded geopolitical risk signal:
$$GPR_t^{\text{filtered}} = \text{sgn}(GPR_t) \cdot \max(0, |GPR_t| - 120)$$
The routing logit $g_j(x_t)$ for expert $j \in \{1, 2, 3\}$ is defined as:
$$g_j(x_t) = W_g^j x_t + b_g^j$$
Where $W_g^j \in \mathbb{R}^{1 \times d}$ and $b_g^j \in \mathbb{R}$ are the learnable gating parameters for expert $j$.

### 3.2 GPR-Conditioned Softmax Temperature Tuning $\tau_t$
The dynamic gating weight $w_i(x_t)$ is computed using the temperature-scaled Softmax:
$$w_i(x_t) = (1 - \lambda) \cdot \frac{\exp\left(\frac{g_i(x_t)}{\tau_t}\right)}{\sum_{j=1}^3 \exp\left(\frac{g_j(x_t)}{\tau_t}\right)} + \lambda \cdot \frac{1}{3}$$
The softmax temperature parameter $\tau_t$ varies dynamically based on the rolling geopolitical risk intensity $\overline{GPR}_t$:
$$\tau_t = \tau_0 \cdot \exp\left(-\alpha \cdot \overline{GPR}_t\right)$$
Where:
* $\tau_0 = 1.5$ is the baseline temperature (calm regime).
* $\alpha = 0.05$ is the sensitivity scaling factor.
* $\overline{GPR}_t$ is the normalized rolling GPR average over a $K = 7$ day window:
  $$\overline{GPR}_t = \frac{1}{K} \sum_{s=0}^{K-1} \frac{GPR_{t-s}}{100}$$

#### Limiting Behaviors of Gating:
1. **Calm Regime ($\overline{GPR}_t \to 0$):**
   $$\tau_t \to \tau_0 \implies \frac{g_i(x_t)}{\tau_t} \to \text{small values} \implies w_i(x_t) \to \frac{1}{3}$$
   The gating distribution becomes uniform, functioning as an equal-weighted ensemble which minimizes overfitting.
2. **Crisis Regime ($\overline{GPR}_t \gg 0$):**
   $$\tau_t \to 0 \implies \frac{g_i(x_t)}{\tau_t} \to \infty \text{ or } -\infty \implies w_i(x_t) \to \begin{cases} 1 - \frac{2}{3}\lambda, & i = \arg\max(g) \\ \frac{\lambda}{3}, & \text{otherwise} \end{cases}$$
   The gating distribution sharpens, routing almost all weight to the primary active expert (Wavelet-KAN) to handle the shock.

### 3.3 Residual Routing Parameter $\lambda$
The gating shortcut uses a fixed hyperparameter $\lambda = 0.1$. The final output of the gated unified network $f_{\text{final}}(x_t)$ is:
$$f_{\text{final}}(x_t) = w_1(x_t) \cdot f_{\text{cnn}}(X_t) + w_2(x_t) \cdot f_{\text{gru}}(X_t) + w_3(x_t) \cdot f_{\text{kan}}(X_t)$$
By adding the residual term $\frac{\lambda}{3}$ to each weight, we establish a lower bound on the routing weights:
$$\min w_i(x_t) \ge \frac{\lambda}{3} = 0.0333$$
This ensures that all experts receive at least 3.33% of the gradient flow during backpropagation, preventing the "dead expert" problem (gating saturation) and allowing continuous cooperative learning.

### 3.4 Mexican Hat Wavelet Parameter Scaling & Updating
The Mexican Hat Wavelet activation function on the edges of the KAN layers is parameterized by:
$$\psi(z) = C \cdot (1 - z^2) \exp\left(-\frac{z^2}{2}\right)$$
Where:
$$z = \frac{x - \mu}{\sigma}, \quad C = \frac{2}{\sqrt{3\sigma}\pi^{1/4}}$$
To dynamically adjust the frequency response and temporal localization of the wavelet, the scale parameter $\sigma > 0$ is updated via gradient descent.
The partial derivative of $\psi$ with respect to the scale parameter $\sigma$ is derived as follows:
$$\frac{\partial \psi}{\partial \sigma} = \frac{\partial \psi}{\partial z} \frac{\partial z}{\partial \sigma} + \frac{\partial \psi}{\partial C} \frac{\partial C}{\partial \sigma}$$
1. Scale change of input coordinate: $\frac{\partial z}{\partial \sigma} = -\frac{x - \mu}{\sigma^2} = -\frac{z}{\sigma}$
2. Normalization coefficient derivative: $\frac{\partial C}{\partial \sigma} = -\frac{1}{2\sigma} C$
3. Wavelet shape derivative: $\frac{\partial \psi}{\partial z} = C \exp\left(-\frac{z^2}{2}\right) \cdot \left[ -2z - z(1-z^2) \right] = C(z^3 - 3z)\exp\left(-\frac{z^2}{2}\right)$

Substituting these back into the partial derivative:
$$\frac{\partial \psi}{\partial \sigma} = C(z^3 - 3z)\exp\left(-\frac{z^2}{2}\right) \left(-\frac{z}{\sigma}\right) - \frac{C}{2\sigma}(1-z^2)\exp\left(-\frac{z^2}{2}\right)$$
$$\frac{\partial \psi}{\partial \sigma} = \frac{C}{\sigma} \exp\left(-\frac{z^2}{2}\right) \left[ -z^4 + 3z^2 - 0.5(1-z^2) \right]$$
$$\frac{\partial \psi}{\partial \sigma} = \frac{C}{\sigma} \exp\left(-\frac{z^2}{2}\right) \left[ -z^4 + 3.5z^2 - 0.5 \right]$$
Expressing this in terms of the original function $\psi(z)$ for $z^2 \neq 1$:
$$\frac{\partial \psi}{\partial \sigma} = \frac{\psi(z)}{\sigma} \cdot \left[ \frac{-z^4 + 3.5z^2 - 0.5}{1-z^2} \right]$$
This derivative allows the optimizer to backpropagate directly to the scale parameter $\sigma$. If high-frequency shocks are present, $\sigma$ contracts ($\sigma \to \text{small}$), increasing the wavelet's frequency band to capture rapid price adjustments. If the market is calm, $\sigma$ dilates ($\sigma \to \text{large}$), smoothing the response.
