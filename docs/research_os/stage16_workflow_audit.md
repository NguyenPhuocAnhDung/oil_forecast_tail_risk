# Stage 16: Retrospective Process Audit & Sprint Backlog

This document presents the retrospective workflow audit for GUM-Net, mapping the project's internal knowledge structure as a formal graph and formulating an Agile Sprint Backlog for future research.

---

## ## WORKFLOW_AUDIT_REPORT

### 1. Retrospective Process Audit

The GUM-Net development lifecycle has transitioned from basic dataset governance to statistical validation. A review of our experimental execution exposes a key trade-off: GUM-Net achieves robustness under extreme tail risks (geopolitical crises and long horizons) by accepting a minor loss of point-forecasting accuracy during quiet/calm periods (where simple linear baselines dominate). 

To ensure continuous improvement, we map the project's internal knowledge structure to identify key vulnerabilities and dependencies.

---

### 2. Project Knowledge Graph

Below is the formal representation of GUM-Net's internal knowledge structure.

```
       +------------------------------------+
       |                BOG                 |
       |     (Domestic Price Policy)        |
       +------------------------------------+
                         |
                         | imposes step-function sparsity
                         v
       +------------------------------------+
       |           Refined Prices           | <=================+
       |     (Gasoline vs. Diesel)          |                   ||
       +------------------------------------+                   ||
                         ^                                      ||
                         | decoupled paths                      ||
                         |                                      ||
       +------------------------------------+                   ||
       |            Routing Gate            |                   ||
       |     (Horizon-Aware Control)        |                   ||
       +------------------------------------+                   ||
           /             |              \                       ||
          /              |               \                      ||
         v               v                v                     ||
  +-------------+  +-------------+  +-------------+             ||
  | CNN Expert  |  | GRU Expert  |  | Wavelet-KAN |             ||
  |  (Momentum) |  |   (Trend)   |  |   (Shock)   |             ||
  +-------------+  +-------------+  +-------------+             ||
                                          ^                     ||
                                          | hard-thresholded    ||
                                          | GPR input           ||
                                    +-------------+             ||
                                    |     GPR     | ------------++
                                    | (Geopoltics)| conditions softmax
                                    +-------------+ temp (tau_t)
```

#### Graph Node Definitions:
1. **`BOG` (Vietnamese Stabilization Fund / Domestic Policy)**:
   - *Type*: Institutional Policy Layer.
   - *Description*: Imposes step-function sparsity on retail fuel prices, preventing rapid transmission of international oil shocks but inducing sharp, discrete jumps during prolonged crises.
2. **`GPR` (Geopolitical Risk Index)**:
   - *Type*: Exogenous Feature.
   - *Description*: Measures global geopolitical tensions. Acts as the primary risk indicator.
3. **`Wavelet-KAN` (Kolmogorov-Arnold Network Expert)**:
   - *Type*: Architecture Expert.
   - *Description*: Absorbs localized high-frequency shocks using Mexican Hat wavelets with backpropagated scale parameters ($\sigma$).
4. **`CNN Expert`**:
   - *Type*: Architecture Expert.
   - *Description*: Captures short-term local momentum and spatial correlations.
5. **`GRU Expert`**:
   - *Type*: Architecture Expert.
   - *Description*: Captures long-term temporal trends.
6. **`Routing Gate`**:
   - *Type*: Control Layer.
   - *Description*: Horizon-aware dynamic gating head. Uses a GPR-conditioned temperature-scaled Softmax to distribute weights $w_i(x_t)$ among the three experts.
7. **`Residual Scaling`**:
   - *Type*: Bounding Layer.
   - *Description*: Acts as an algorithmic emergency brake at long horizons ($H=60$), clamping out-of-distribution MAPE to $< 7.5\%$.
8. **`Refined Prices` (RON95, RON92, Diesel)**:
   - *Type*: Forecast Target.
   - *Description*: Highly regulated retail oil price log-returns.

#### Graph Edge Properties:
* **`GPR` $\xrightarrow{\text{conditions softmax temp}}$ `Routing Gate`**:
  * *Property*: Inverse exponential relationship: $\tau_t = \tau_0 \cdot \exp(-\alpha \cdot \overline{GPR}_t)$. Lowers temperature to focus on the shock expert when GPR is high.
* **`GPR` $\xrightarrow{\text{hard-thresholded input}}$ `Wavelet-KAN`**:
  * *Property*: Subtraction thresholding $GPR_t^{\text{filtered}} = \text{sgn}(GPR_t) \cdot \max(0, |GPR_t| - \theta)$, filtering out normal-period market noise.
* **`BOG` $\xrightarrow{\text{imposes step-function sparsity}}$ `Refined Prices`**:
  * *Property*: Induces price rigidity in calm regimes, leading to temporary model underperformance (overfitting on flat steps).
* **`Routing Gate` $\xrightarrow{\text{controls weights}}$ `CNN`, `GRU`, `Wavelet-KAN`**:
  * *Property*: Allocates $w_i(x_t)$ with a residual lower bound constraint: $\min w_i(x_t) \ge \frac{\lambda}{3} = 0.0333$ to prevent gradient saturation.
* **`Residual Scaling` $\xrightarrow{\text{bounds error}}$ `Refined Prices`**:
  * *Property*: Binds extrapolation errors to prevent run-away predictions at $H=60$.

---

### 3. Future Researcher Agile Sprint Backlog

To guide future investigators in scaling and optimizing GUM-Net, we establish a concrete 2-week Sprint Backlog:

#### Sprint Goal: "Optimize Calm-Regime Generalization and Integrate SOTA Foundation Models"

| US ID | Title | User Story | Priority | Estimate (SP) | Acceptance Criteria |
|---|---|---|---|:---:|---|
| **US-01** | **Integrate Google TimesFM and Chronos Baselines** | *As a researcher,* I want to run TimesFM and Chronos on `unified_data.csv` *so that* GUM-Net can be evaluated against pre-trained SOTA time-series foundation models. | High | 5 | * TSFM predictions generated via walk-forward validation.<br>* Results added to comparative results tables. |
| **US-02** | **Implement SOTA Comparison and Selection Policy Loop** | *As an engineer,* I want to implement the automated loss audit loop *so that* if a TSFM outperforms GUM-Net, it is automatically supplemented and triggers an architecture diagnostic. | High | 3 | * Script automatically compares validation MAPE.<br>* Logs warning and inputs detailed `Loss Diff(t)` breakdown if TSFM outperforms GUM-Net. |
| **US-03** | **Optimize GPR Noise Gating Threshold ($\theta$)** | *As a data scientist,* I want to grid-search the GPR hard-thresholding parameter $\theta$ *so that* we can filter out quiet-regime GPR noise and improve MAE. | Medium | 3 | * MAE on Gasoline (H10) in calm regimes is reduced by at least 5%.<br>* Geopolitical shock absorption at H60 remains unaffected. |
| **US-04** | **Wavelet-KAN Numeric Guardrails** | *As an engineer,* I want to add boundary constraints to the backpropagated scale parameter $\sigma$ *so that* the network does not suffer division-by-zero during steep shocks. | High | 2 | * Custom autograd function limits $\sigma \ge 0.01$.<br>* Model training runs to completion without generating NaNs under simulated spot price shocks. |
| **US-05** | **Hedging Advisor Streamlit App** | *As a corporate user,* I want a Streamlit interface displaying GUM-Net's multi-horizon forecasts alongside the dynamic hedging ratio $H_t$ *so that* I can execute fuel purchases. | Medium | 5 | * Web interface loads predictions daily.<br>* Renders interactive plots of $\hat{y}^{q50}, \hat{y}^{q90}$, and outputs explicit Hedging Directives (Hedge Ratio %). |
