## DATA_PIPELINE_ARCHITECTURE

# Stage 6: Data Pipeline & Walk-Forward Validation Architecture

This document describes the formal data pipeline and walk-forward validation architecture for the research project. It details the causal data ingestion pipeline, specifies the expanding-window walk-forward validation protocol across the six prediction horizons, and provides the mathematical formulation of the MIDAS spline interpolation and the dynamic percentile-based Noise Gate.

---

## 1. End-to-End Data Pipeline Flow

The diagram below illustrates the end-to-end flow of raw data ingestion, causal preprocessing, temporal partition, local scaling, and multi-horizon target formulation.

```
 +-----------------------------------------------------------------------+
 | Raw Ingestion:                                                        |
 | Platt's Daily Spot, WTI/Brent Futures, USD Index (Daily), GPR (Daily) |
 +-----------------------------------------------------------------------+
                                     |
                                     v [Protocol: Causal Forward Fill]
 +-----------------------------------------------------------------------+
 | Missing Value Imputation: y_t = y_{t-1} if t is Weekend/Holiday       |
 +-----------------------------------------------------------------------+
                                     |
                                     v [Stationarity Check: ADF / KPSS]
 +-----------------------------------------------------------------------+
 | Stationary Decoupling:                                                |
 | - Gasoline (xăng): Log-returns (I(0))                                 |
 | - Diesel (dầu): Price levels (I(1))                                   |
 +-----------------------------------------------------------------------+
                                     |
                                     v [MIDAS & Noise Gate Integration]
 +-----------------------------------------------------------------------+
 | Feature Engineering: MIDAS Spline GPR + Percentile Noise Gate         |
 +-----------------------------------------------------------------------+
                                     |
                                     v [Expanding Window Splits]
 +-----------------------------------------------------------------------+
 | Walk-Forward Validation:                                              |
 | Split into Local Train [1:T], Local Val [T:V], Local Test [V:V+H]     |
 +-----------------------------------------------------------------------+
                                     |
                                     v [Local Scaling Only]
 +-----------------------------------------------------------------------+
 | Scaling: StandardScaler fit on Local Train, transform Val & Test      |
 +-----------------------------------------------------------------------+
                                     |
                                     v [Direct Target Construction]
 +-----------------------------------------------------------------------+
 | Target: R_{t->t+H} = log(P_{t+H} / P_t) for H in [1, 3, 5, 10, 20, 60]|
 +-----------------------------------------------------------------------+
```

---

## 2. Multi-Horizon Walk-Forward Validation

To guarantee leak-free out-of-sample evaluation, we implement the **Expanding Window Walk-Forward Validation** protocol. The dataset spans $N = 4,517$ trading days.

### 2.1 The Splitting Mechanism
At step $i$ of the walk-forward validation:
1. **Active Boundary**: The training data boundary is defined up to $T_i = N - N_{\text{test}} + i \cdot S_H$.
2. **Local Training Partition**: $D_{\text{train}, i} = \{X_t, Y_t\}_{t=1}^{0.85 \times T_i}$
3. **Local Validation Partition**: $D_{\text{val}, i} = \{X_t, Y_t\}_{t=0.85 \times T_i - L}^{T_i}$
4. **Local Test Slice**: $D_{\text{test}, i} = \{X_t, Y_t\}_{t=T_i - L}^{T_i + H}$
   * *Note*: The test slice is strictly of length $L + H$, where $L = 30$ is the look-back window, and $H$ is the prediction horizon. Only the final prediction at index $T_i + H$ is recorded for evaluation.

### 2.2 Prediction Horizons and Step Sizes
We evaluate the models across six prediction horizons. The step size $S_H$ is optimized to balance the number of evaluation windows and test error autocorrelation:

| Horizon ($H$) | Economic Interpretation | Walk-Forward Step Size ($S_H$) | Total Test Iterations ($N_{\text{test}} / S_H$) |
|---|---|---|---|
| **H1** | Daily momentum | $1$ day | $200$ |
| **H3** | Near-term market lag | $3$ days | $66$ |
| **H5** | Weekly operating cycle | $5$ days | $40$ |
| **H10** | Domestic policy window | $5$ days | $40$ (overlapping) |
| **H20** | Mid-term planning horizon | $10$ days | $20$ |
| **H60** | Long-term strategic forecast | $20$ days | $10$ |

*Note on H10 Overlapping*: To ensure stable statistical estimates of $R^2$ at $H=10$, we use $S_{10} = 5$ days. The resulting overlap in test errors is corrected in the Diebold-Mariano test using a Heteroskedasticity and Autocorrelation Consistent (HAC) covariance estimator with a Bartlett kernel.

---

## 3. Mixed Data Sampling (MIDAS) Spline Interpolation

The Geopolitical Risk (GPR) Index and international oil futures are daily variables, whereas domestic retail price adjustments occur at discrete weekly or bi-weekly intervals. To feed daily exogenous variables into the step-function prediction pipeline without losing high-frequency volatility, we implement a **MIDAS Spline Interpolation** model.

Let $t$ represent the low-frequency index (announcement dates) and $\tau$ represent the high-frequency daily index. The low-frequency target return is predicted using a weighted lag of the daily GPR index:
$$X^{\text{MIDAS}}_{t} = \sum_{j=0}^{K} w_j(\theta) GPR_{t - j/m}^{(d)}$$
Where:
* $m$ is the number of daily trading days within the low-frequency step.
* $w_j(\theta)$ is the weighting function.
* $GPR_{t - j/m}^{(d)}$ is the daily GPR value at lag $j/m$.

To parameterize $w_j(\theta)$ smoothly and prevent parameter explosion, we use a **B-Spline Basis Formulation**:
$$w_j(\theta) = \sum_{p=1}^{P} \alpha_p B_p(j)$$
Where:
* $B_p(j)$ are the spline basis functions of degree $d_s$ (typically cubic, $d_s = 3$) evaluated at lag $j$.
* $\alpha_p$ are the learnable spline coefficients.
* $P$ is the number of spline knots (e.g., $P = 4$).

The cubic spline basis function $B_p(j)$ is defined recursively. For a knot sequence $t_0, t_1, \dots, t_{M}$:
$$B_{p, 0}(j) = \begin{cases} 1, & \text{if } t_p \le j < t_{p+1} \\ 0, & \text{otherwise} \end{cases}$$
$$B_{p, k}(j) = \frac{j - t_p}{t_{p+k} - t_p} B_{p, k-1}(j) + \frac{t_{p+k+1} - j}{t_{p+k+1} - t_{p+1}} B_{p+1, k-1}(j)$$
This spline-based formulation allows GUM-Net to learn a smooth, continuous lag weight structure that automatically scales GPR features, capturing decay effects over long horizons.

---

## 4. Historical Percentile-Based Dynamic Noise Gate

Vietnamese retail prices are highly regulated and constant over multiple days. Continuous fluctuations in daily GPR index values act as noise, causing the Wavelet-KAN expert to predict "phantom volatility" in flat regions. To filter this, we implement a **Percentile-Based Dynamic Noise Gate**.

Rather than setting a static threshold, the activation threshold $\theta_t$ is computed dynamically using the $95\text{th}$ percentile of the historical GPR index over a rolling one-year window:
$$\theta_t = \text{Percentile}\left( \{ GPR_s \}_{s=t-N_{\text{hist}}}^{t-1}, 95 \right)$$
Where $N_{\text{hist}} = 252$ trading days (representing one trading year).

The filtered GPR index is then defined as:
$$GPR_t^{\text{filtered}} = \text{sgn}(GPR_t) \cdot \max\left( 0, |GPR_t| - \theta_t \right)$$

### Properties of the Dynamic Noise Gate:
1. **Adaptive Scaling**: If the previous year was geopolitically stable, $\theta_t$ remains low, allowing smaller shocks to activate the Wavelet-KAN. If the previous year was highly volatile, $\theta_t$ scales upward, raising the bar for what constitutes a significant geopolitical shock.
2. **Zero-Mapping for Calm Regimes**: When $GPR_t < \theta_t$, $GPR_t^{\text{filtered}}$ is mapped exactly to $0$. This shuts off the input to the Wavelet-KAN expert, preventing the network from predicting price changes during calm periods and preserving the flat step-like output.
