# Stage 14: Corporate Decision Layer & Publication Strategy

This document outlines the corporate hedging decision layer that translates GUM-Net's forecasting outputs into actionable hedging policies under extreme geopolitical tail risks. It also presents a Novelty Fit analysis for Q1 energy journals.

---

## ## PUBLICATION_STRATEGY_DIRECTIVE

### 1. The Corporate Decision Layer

While forecasting accuracy (MAE, MAPE, R²) is the primary academic metric, corporate risk managers and fuel distributors require concrete decision rules to manage supply chains. Refined petroleum product distributors (e.g., petrol stations, transport logistics companies, airlines) operate on thin margins and are highly vulnerable to supply shocks and retail price caps.

GUM-Net provides a multi-horizon quantile forecast:
* $\hat{y}_{t+H|t}^{q50}$: The predicted median price trend (log-return) at horizon $H$.
* $\hat{y}_{t+H|t}^{q90}$: The 90th percentile upper-bound price forecast (representing the worst-case price inflation tail risk).
* $\overline{GPR}_t$: The normalized rolling Geopolitical Risk Index over a 7-day window.

We translate these outputs into a dynamic **Corporate Hedging Ratio ($H_t \in [0, 1]$)** representing the percentage of fuel volume requirements to lock in via forward contracts, swap options, or pre-purchased inventory at the current spot price.

---

### 2. Mathematical Hedging Decision Rules

The hedging ratio $H_t$ is determined by a GPR-conditioned quantile risk rule:

$$H_t = \min\left(H_{\max}, \max\left(H_{\min}, H_t^{\text{state}} + H_t^{\text{geopolitical}}\right)\right)$$

Where:
* **$H_{\min} = 0.20$**: The minimum strategic inventory buffer to ensure basic operational continuity.
* **$H_{\max} = 0.90$**: The maximum hedging capacity (preventing cash-flow lock-up in illiquid contracts).
* **$H_t^{\text{state}}$**: The baseline trend hedge driven by the median prediction:
  $$H_t^{\text{state}} = H_{\text{base}} + \beta_1 \cdot \text{ReLU}\left(\hat{y}_{t+H|t}^{q50} - \theta_p\right)$$
  * $H_{\text{base}} = 0.40$ is the neutral hedging ratio.
  * $\theta_p = 0.005$ is the log-return threshold (below which no action is taken on point trends).
  * $\beta_1 = 3.5$ is the trend sensitivity parameter.
* **$H_t^{\text{geopolitical}}$**: The tail risk surcharge driven by the predicted upper bound and geopolitical index:
  $$H_t^{\text{geopolitical}} = \beta_2 \cdot \max\left(0, \frac{\overline{GPR}_t - \theta_{\text{gpr}}}{100}\right) + \beta_3 \cdot \text{ReLU}\left(\hat{y}_{t+H|t}^{q90} - \hat{y}_{t+H|t}^{q50}\right)$$
  * $\theta_{\text{gpr}} = 100$ is the threshold above which geopolitical risks are considered active.
  * $\beta_2 = 0.15$ is the GPR sensitivity scaling factor.
  * $\beta_3 = 2.0$ is the tail spread sensitivity factor.

#### Operational Regimes & Hedging Directives:

```
                  +---------------------------------------+
                  |       DETERMINE MARKET REGIME         |
                  +---------------------------------------+
                   /                  |                  \
                  /                   |                   \
                 v                    v                    v
     +-----------------------+ +--------------+ +-----------------------+
     |  1. Calm (GPR < 100)  | | 2. Escalation| | 3. Crisis (GPR > 200) |
     | - Rely on median pred | | - Boost hedge| | - Maximize hedge ratio|
     | - Hedge ratio 20-50%  | | - Ratio 50-70| | - Lock in 80-90%      |
     +-----------------------+ +--------------+ +-----------------------+
```

1. **Quiet/Calm Regime ($\overline{GPR}_t < 100$):**
   * Geopolitical surcharge $H_t^{\text{geopolitical}} \approx 0$.
   * GUM-Net's router allocates high weight to CNN/GRU.
   * The hedge ratio is determined purely by the median trend forecast $\hat{y}_{t+H|t}^{q50}$. If the market is flat, $H_t \approx 0.40$ (neutral). If a downward trend is predicted, the hedge ratio is reduced to $H_{\min} = 0.20$ to exploit future lower spot prices.
2. **Escalation Regime ($100 \le \overline{GPR}_t \le 200$):**
   * The GPR surcharge is activated. 
   * Even if the median forecast $\hat{y}_{t+H|t}^{q50}$ remains flat, the tail spread risk $(\hat{y}_{t+H|t}^{q90} - \hat{y}_{t+H|t}^{q50})$ expands due to increased volatility.
   * The hedge ratio increases to **0.50 – 0.70**, locking in prices ahead of expected step-function adjustments in domestic retail fuel prices.
3. **Extreme Geopolitical Crisis ($\overline{GPR}_t > 200$):**
   * The gating head routes maximum weight to Wavelet-KAN.
   * The soft-max temperature $\tau_t$ drops, causing routing concentration.
   * The geopolitical risk surcharge spikes. The hedging rule triggers the **"Emergency Hedging Directive"**, forcing $H_t \to H_{\max} = 0.90$.
   * This locks in 90% of the required fuel volume, shielding the distributor from extreme supply-side price spikes.

---

### 3. Novelty Fit Analysis for Q1 Journals

To maximize the probability of acceptance, we analyze how GUM-Net's research design aligns with the specific target scopes of Q1 Energy journals.

| Target Journal | Scope & Editor Preferences | GUM-Net Novelty Fit & Alignment Strategy |
|---|---|---|
| **Energy Economics** | * High preference for econometric validity, asymptotic statistical tests, and policy implications. * Rejects "black-box" machine learning papers that lack structural economic theory or statistical testing. | * **Rigorous Validation**: We bypass standard ML train/test splits in favor of Expanding Window Walk-Forward Validation, Newey-West HAC Diebold-Mariano tests, and Hansen's Model Confidence Set. * **Theory-Informed Decoupling**: We justify the decoupling of Gasoline and Diesel based on domestic tax/subsidization policy differences (complying with Vietnam's pricing formula). * **Decision Layer**: We present the mathematical hedging rules, demonstrating the practical economic utility of the machine learning model. |
| **Applied Energy** | * Prefers engineering and system-level applications, computational efficiency, and architectural novelty. * Values physical or system analogies and detailed technological evaluations. | * **Architectural Innovation**: The integration of Wavelet-KAN with backpropagated Mexican Hat wavelet scales represents a significant neural architecture contribution. * **Hybrid Model**: The combination of CNN (spatial/momentum), GRU (temporal/trend), and KAN (shock-absorber) via a horizon-aware router fits the journal's focus on advanced computational systems. * **Physical Analogy**: Stage 15's shock-absorber spring system analogy provides an intuitive, system-level explanation of model dynamics. |
| **Energy** | * Broad journal focusing on energy technology, policy, and resource management. * Values multi-disciplinary approaches bridging energy markets and data science. | * **Policy Modeling**: The model directly incorporates the Geopolitical Risk (GPR) Index and models retail price step-functions (BOG). * This offers energy planners a tool to evaluate the impact of global geopolitical shocks on domestic inflation and price stability, aligning with the journal's policy focus. |
