## STATISTICAL_VALIDATION_VERDICT

# Stage 10: Econometric Validation & Superior Set Selection

This document establishes the formal econometric validation framework for GUM-Net. It specifies the Diebold-Mariano test with Newey-West HAC variance corrections, details the Hansen et al. (2011) Model Confidence Set bootstrap protocol ($\alpha = 0.05$), defines the non-parametric effect size metrics, and integrates the **Requirement R8: SOTA Comparison and Selection Policy**.

---

## 1. Diebold-Mariano Test with Newey-West HAC Variance Correction

The Diebold-Mariano (DM) test is used to evaluate the statistical significance of GUM-Net's forecasting superiority over the baseline models.

### 1.1 Loss Differential & Hypothesis Formulation
Let $e_{1,t+H|t}$ and $e_{2,t+H|t}$ be the $H$-step forecast errors of Model 1 (GUM-Net-Fusion) and Model 2 (Baseline) at time $t$. The loss differential $d_t$ is defined as:

$$d_t = \mathcal{L}\left(e_{1, t+H|t}\right) - \mathcal{L}\left(e_{2, t+H|t}\right)$$

Where $\mathcal{L}(\cdot)$ is the loss metric (typically $\mathcal{L}(e) = |e|$ for MAE). The null hypothesis of equal predictive accuracy is:

$$H_0: \mathbb{E}[d_t] = 0$$

The one-sided alternative hypothesis proving GUM-Net superiority is:

$$H_1: \mathbb{E}[d_t] < 0$$

The DM statistic is computed as:

$$DM = \frac{\bar{d}}{\sqrt{\hat{\sigma}^2_{\bar{d}}}} \ \sim \ \mathcal{N}(0, 1)$$

Where the mean loss differential is:

$$\bar{d} = \frac{1}{T} \sum_{t=1}^T d_t$$

### 1.2 Newey-West HAC Correction
Because $H$-step ahead forecasts contain overlapping information, the forecast errors are autocorrelated up to order $H-1$. To handle this serial correlation and potential heteroskedasticity, we compute the variance estimator $\hat{\sigma}^2_{\bar{d}}$ using the **Newey-West HAC estimator**:

$$\hat{\sigma}^2_{\bar{d}} = \frac{1}{T} \left( \hat{\gamma}_0 + 2 \sum_{k=1}^{J} \left(1 - \frac{k}{J+1}\right) \hat{\gamma}_k \right)$$

The sample autocovariance at lag $k$ is:

$$\hat{\gamma}_k = \frac{1}{T} \sum_{t=k+1}^{T} (d_t - \bar{d})(d_{t-k} - \bar{d})$$

And the truncation lag (bandwidth) $J$ is set to correct for overlapping forecasts:

$$J = \min\left(H - 1, \left\lfloor 1.2 \cdot T^{1/3} \right\rfloor\right)$$

(with $J$ enforced to be at least $1$ to correct for first-order autocorrelation).

A $p$-value $< 0.05$ rejects $H_0$, indicating that GUM-Net's error reduction is statistically significant.

---

## 2. Hansen's Model Confidence Set (MCS) Protocol ($\alpha = 0.05$)

To isolate the superior set of models without pairwise comparison bias, we implement the **Model Confidence Set (MCS)** procedure (Hansen, Lunde, and Nason, 2011; *Econometrica*) at the significance level $\alpha = 0.05$.

```
          +------------------------------------------------------------+
          |               INITIAL MODEL SET: M_0                       |
          |  {GUM-Net, PatchTST, DLinear, TFT, TimesNet, LSTM, ...}    |
          +------------------------------------------------------------+
                                        |
                                        v
          +------------------------------------------------------------+
          |           Test Equal Predictive Ability (EPA)              |
          |         H_0: E[d_ij,t] = 0 for all i,j in M_t              |
          +------------------------------------------------------------+
                                    /       \
                         Rejected  /         \  Accepted
                                  v           v
          +----------------------------+  +----------------------------+
          | Eliminate worst model:     |  | Stop. M_t is the Model     |
          | i* = argmax_i d_i.         |  | Confidence Set (M_alpha*)  |
          | M_t+1 = M_t \ {i*}         |  +----------------------------+
          +----------------------------+
```

### 2.1 EPA Test Statistic
Let $\mathcal{M}_0$ be the initial set of 33 candidate models. The MCS dynamically tests the null hypothesis of Equal Predictive Ability (EPA) for a subset $\mathcal{M} \subset \mathcal{M}_0$ at significance level $\alpha = 0.05$:

$$H_{0, \mathcal{M}}: \mathbb{E}[d_{ij, t}] = 0 \quad \forall i, j \in \mathcal{M}$$

The test statistic $T_{\max}$ is defined as:

$$T_{\max} = \max_{i \in \mathcal{M}} t_{i}$$

The studentized loss $t_{i}$ of model $i$ relative to the average of all other active models is:

$$t_{i} = \frac{\bar{d}_{i\cdot}}{\sqrt{\widehat{\text{Var}}(\bar{d}_{i\cdot})}}$$

Where:
* $\bar{d}_{i\cdot} = \frac{1}{|\mathcal{M}|-1} \sum_{j \in \mathcal{M} \setminus \{i\}} \bar{d}_{ij}$ represents the mean loss differential of model $i$.
* $d_{ij, t} = \mathcal{L}(e_{i,t}) - \mathcal{L}(e_{j,t})$ is the loss differential at time $t$.

### 2.2 Stationary Block Bootstrap
Because the loss differentials exhibit temporal dependence, the distribution of $T_{\max}$ and the variance $\widehat{\text{Var}}(\bar{d}_{i\cdot})$ are estimated using a **Stationary Block Bootstrap** (Politis & Romano, 1994) using $B = 999$ resamples and adaptive block length $b = \lfloor T^{1/4} \rfloor$.

If the bootstrap $p$-value for $H_{0, \mathcal{M}}$ falls below $\alpha = 0.05$, the worst-performing model $i^*$ is eliminated:

$$i^* = \arg\max_{i \in \mathcal{M}} \bar{d}_{i\cdot} \quad \text{where} \quad \bar{d}_{i\cdot} = \frac{1}{T} \sum_{t=1}^{T} d_{i\cdot, t}$$

The loop terminates when the EPA null hypothesis cannot be rejected at $\alpha = 0.05$. The remaining models constitute the superior set $\widehat{\mathcal{M}}_{0.95}^*$.

---

## 3. Non-Parametric Effect Size Measures

To quantify the magnitude of GUM-Net's performance gains over the baseline models without relying on normal distribution assumptions, we compute Cliff's Delta and Vargha-Delaney $A_{12}$ metrics on the absolute prediction residuals.

### 3.1 Cliff's Delta ($\delta$)
Cliff's Delta evaluates the probability that a random prediction error from a baseline model ($X_1$) is larger than a random prediction error from GUM-Net ($X_2$):

$$\delta = \frac{1}{N_1 N_2} \sum_{i=1}^{N_1} \sum_{j=1}^{N_2} \text{sgn}\left(|e_{i, \text{baseline}}| - |e_{j, \text{GUM-Net}}|\right)$$

Where $\text{sgn}(x)$ is the sign function:

$$\text{sgn}(x) = \begin{cases} 1, & x > 0 \\ 0, & x = 0 \\ -1, & x < 0 \end{cases}$$

### 3.2 Vargha-Delaney $A_{12}$
The Vargha-Delaney $A_{12}$ statistic measures the probability of stochastic superiority of GUM-Net over a baseline:

$$A_{12} = \frac{1}{N_1 N_2} \sum_{i=1}^{N_1} \sum_{j=1}^{N_2} \left[ \mathbb{I}\left(|e_{i, \text{baseline}}| > |e_{j, \text{GUM-Net}}|\right) + 0.5 \cdot \mathbb{I}\left(|e_{i, \text{baseline}}| == |e_{j, \text{GUM-Net}}|\right) \right]$$

An $A_{12} > 0.5$ indicates that the baseline has a stochastic tendency to yield larger errors than GUM-Net, confirming GUM-Net's superiority.

---

## 4. Integration of Requirement R8 SOTA Selection Policy

To ensure GUM-Net is continually benchmarked against the strongest industry standards, we implement a strict **SOTA Comparison and Selection Policy**.

```
                           +------------------------+
                           |   Evaluate TSFM model  |
                           | (TimesFM, Chronos,...) |
                           +------------------------+
                                       |
                                       v
                    +--------------------------------------+
                    | Is global MAPE_TSFM < MAPE_GUM-Net?  |
                    +--------------------------------------+
                                   /        \
                            Yes   /          \   No
                                 v            v
                  +----------------------+  +----------------------+
                  | Supplement TSFM into |  | Keep current SOTA    |
                  | active baselines     |  | benchmarks           |
                  +----------------------+  +----------------------+
                              |
                              v
                  +----------------------+
                  | Trigger Automated    |
                  | Loss Audit Loop      |
                  +----------------------+
```

### 4.1 Comparison Rules
1. **Foundation Model Inclusion**: GUM-Net must be evaluated against the latest pre-trained Time Series Foundation Models (TSFMs) including **TimesFM**, **Chronos**, and **Moirai** using the same data splits and walk-forward protocol.
2. **The Supplementation Trigger**: If a TSFM achieves a lower overall validation MAPE or higher $R^2$ than GUM-Net, GUM-Net is **not** replaced. Instead, the outperforming TSFM is added to the active comparative baseline matrix. All historical baselines must remain active.

### 4.1.1 Verbatim Scientific Integrity Clause (R8 Rule)
> **Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu.**

### 4.2 Automated Loss Audit Loop
Upon supplementing a TSFM, the pipeline triggers an automated diagnostic loop:
$$\text{Loss Diff}(t) = \mathcal{L}_{\text{GUM-Net}}(t) - \mathcal{L}_{\text{TSFM}}(t)$$
* **Regime Analysis**:
  1. **Quiet Regime Superiority**: If the TSFM's advantage is concentrated during normal periods, the routing temperature $\tau_t$ is regularized or the expert parameters are constrained to prevent overfitting of the gate.
  2. **Crisis Regime Superiority**: If the TSFM outperforms during crises, the Wavelet-KAN scale parameters ($\sigma$) and the GPR noise gate thresholds are audited and adjusted to enhance local shock absorption.
