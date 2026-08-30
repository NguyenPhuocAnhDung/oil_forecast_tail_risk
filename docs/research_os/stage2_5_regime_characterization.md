## REGIME_CHARACTERIZATION_PROTOCOL

# Stage 2.5: Structural Break Detection & Regime Characterization Protocol

This document establishes the formal regime characterization protocol, detailing the econometric algorithms for structural break detection and the mathematical distance metrics used to quantify distribution shifts.

---

## 1. Econometric Structural Break Detection

To identify and validate the temporal boundaries of the 5 tail-risk windows, GUM-Net employs two independent econometric break detection mechanisms.

### 1.1 The Bai-Perron Structural Break Detection Algorithm
The Bai-Perron (1998, 2003) algorithm is a global optimization procedure that detects multiple structural breaks in a linear regression model. For a time series of length $T$ and $m$ breaks (yielding $m+1$ regimes), the relationship is defined as:

$$y_t = x_t^T \beta + z_t^T \delta_j + u_t, \quad t = T_{j-1} + 1, \dots, T_j$$

Where:
* $y_t$ is the target series (price or return).
* $x_t$ and $z_t$ are vectors of regressors with coefficients $\beta$ (constant across all regimes) and $\delta_j$ (regime-specific parameters).
* $T_j$ represents the break dates ($j = 1, \dots, m$), with the convention $T_0 = 0$ and $T_{m+1} = T$.

The optimal break dates $(T_1, \dots, T_m)$ are found by solving the global minimization of the sum of squared residuals (SSR):

$$(T_1, \dots, T_m) = \arg\min_{(T_1, \dots, T_m)} S_T(T_1, \dots, T_m)$$

Where the objective function is:

$$S_T(T_1, \dots, T_m) = \sum_{j=1}^{m+1} \sum_{t=T_{j-1}+1}^{T_j} \left( y_t - x_t^T \beta - z_t^T \delta_j \right)^2$$

The optimization is solved efficiently using dynamic programming. To determine the optimal number of breaks $m$, we perform sequential testing using the $F(l+1|l)$ statistic, which tests the null hypothesis of $l$ breaks against the alternative of $l+1$ breaks:

$$F(l+1|l) = \frac{1}{\hat{\sigma}^2} \left[ S_T(T_1, \dots, T_l) - \min_{1 \le i \le l+1} \inf_{\tau \in \Lambda_i} S_T(T_1, \dots, T_{i-1}, \tau, T_i, \dots, T_l) \right]$$

Where $\Lambda_i$ is the set of allowable break dates in segment $i$, and $\hat{\sigma}^2$ is a consistent estimator of the residual variance under the alternative.

---

### 1.2 The CUSUM Process
The Cumulative Sum (CUSUM) test of Brown, Durbin, and Evans (1975) is used as a continuous monitoring tool to detect structural instability in the parameters. 

#### 1. Recursive Residuals
Let $b_{r-1}$ be the Ordinary Least Squares (OLS) estimate of the parameter vector based on the first $r-1$ observations. The recursive residual at step $r$ is defined as:

$$w_r = \frac{y_r - x_r^T b_{r-1}}{\sqrt{1 + x_r^T (X_{r-1}^T X_{r-1})^{-1} x_r}}$$

Where $X_{r-1}$ is the matrix of regressors up to step $r-1$. Under the null hypothesis of parameter constancy, $w_r \sim \mathcal{N}(0, \sigma^2)$ and are independent over time.

#### 2. CUSUM Statistic
The CUSUM statistic at time $t$ ($t = k+1, \dots, T$, where $k$ is the number of parameters) is the cumulative sum of the standardized recursive residuals:

$$W_t = \frac{1}{\hat{\sigma}} \sum_{j=k+1}^t w_j$$

Where $\hat{\sigma}$ is the standard error of the residuals estimated over the entire sample.

#### 3. Boundary Crossing
A structural break is detected at significance level $\alpha$ when the statistic $W_t$ crosses the critical boundary:

$$|W_t| > a \cdot \sqrt{T - k} + \frac{2a \cdot (t - k)}{\sqrt{T - k}}$$

Where the coefficient $a$ determines the significance level (e.g., $a = 0.948$ for $\alpha = 5\%$, and $a = 1.143$ for $\alpha = 1\%$).

---

## 2. Mathematical Distribution Distance Metrics

To quantify the magnitude of the structural shifts during the tail-risk windows, we measure the distance between the distribution of the normal regime $P$ and the tail-risk regime $Q$ using three mathematical formulations.

### 2.1 Wasserstein Distance ($W_1$ Metric)
The first Wasserstein distance (Earth Mover's Distance) measures the minimum cost of transporting probability mass to transform distribution $P$ into $Q$. On a metric space, it is defined as:

$$\mathcal{W}_1(P, Q) = \inf_{\gamma \in \Pi(P, Q)} \mathbb{E}_{(x,y)\sim \gamma}\left[ \|x - y\| \right]$$

Where $\Pi(P, Q)$ is the set of all joint distributions (couplings) whose marginals are $P$ and $Q$.
In the one-dimensional case (e.g., for price return series), this simplifies to the integrated absolute difference between their Cumulative Distribution Functions (CDFs):

$$\mathcal{W}_1(P, Q) = \int_{-\infty}^{\infty} |F_P(x) - F_Q(x)| dx$$

Where $F_P(x)$ and $F_Q(x)$ are the CDFs of $P$ and $Q$, respectively.

---

### 2.2 Maximum Mean Discrepancy (MMD)
Maximum Mean Discrepancy represents the distance between two distributions mapped into a Reproducing Kernel Hilbert Space (RKHS) $\mathcal{H}$. MMD is defined as:

$$\text{MMD}(P, Q) = \sup_{f \in \mathcal{H}, \|f\|_{\mathcal{H}} \le 1} \left( \mathbb{E}_{x \sim P}[f(x)] - \mathbb{E}_{y \sim Q}[f(y)] \right)$$

Using the kernel trick with a positive-definite kernel $k(x, y) = \langle \phi(x), \phi(y) \rangle_{\mathcal{H}}$ (such as the Gaussian Radial Basis Function (RBF) kernel $k(x, y) = \exp(-\|x-y\|^2 / 2\sigma^2)$), the squared MMD is formulated as:

$$\text{MMD}^2(P, Q) = \mathbb{E}_{x, x' \sim P}[k(x, x')] - 2\mathbb{E}_{x \sim P, y \sim Q}[k(x, y)] + \mathbb{E}_{y, y' \sim Q}[k(y, y')]$$

For empirical samples $X = \{x_1, \dots, x_n\} \sim P$ and $Y = \{y_1, \dots, y_m\} \sim Q$, the unbiased estimator is:

$$\text{MMD}^2_{u}(X, Y) = \frac{1}{n(n-1)} \sum_{i=1}^n \sum_{j \neq i}^n k(x_i, x_j) - \frac{2}{nm} \sum_{i=1}^n \sum_{j=1}^m k(x_i, y_j) + \frac{1}{m(m-1)} \sum_{i=1}^m \sum_{j \neq i}^m k(y_i, y_j)$$

---

### 2.3 Kullback-Leibler (KL) Divergence
KL divergence measures the relative entropy or information loss when distribution $Q$ is used to approximate the true distribution $P$:

$$D_{KL}(P \parallel Q) = \int_{-\infty}^{\infty} p(x) \log\left(\frac{p(x)}{q(x)}\right) dx$$

Assuming the price returns in the normal and tail-risk regimes can be approximated by multivariate Gaussians $P \sim \mathcal{N}(\mu_1, \Sigma_1)$ and $Q \sim \mathcal{N}(\mu_2, \Sigma_2)$ in $\mathbb{R}^d$, the KL divergence is given in closed form as:

$$D_{KL}(P \parallel Q) = \frac{1}{2} \left[ \text{Tr}\left(\Sigma_2^{-1} \Sigma_1\right) + (\mu_2 - \mu_1)^T \Sigma_2^{-1} (\mu_2 - \mu_1) - d + \ln\left( \frac{\det \Sigma_2}{\det \Sigma_1} \right) \right]$$

---

## 3. Empirical Regime Statistics & Validation

### 3.1 Regime Classification Criterion
Following `scripts/regime_analysis.py`, we classify volatility regimes based on the 60-day annualized rolling volatility of WTI log returns ($\sigma_{60d}$):

$$\sigma_{60d, t} = \text{std}\left( R_{t-59:t}^{WTI} \right) \cdot \sqrt{252}$$

* **Low Volatility Regime**: $\sigma_{60d} < 22\%$ (represent stable, normal periods).
* **Medium Volatility Regime**: $22\% \le \sigma_{60d} \le 40\%$ (represent typical trading fluctuations).
* **High Volatility / Tail-Risk Regime**: $\sigma_{60d} > 40\%$ (represent geopolitical crises and structural breaks).

### 3.2 Volatility Peak Analysis during Geopolitical shocks
Based on historical data audits, the annualized WTI volatility peaks during major tail-risk windows are recorded as follows:

1. **2008 Financial Crisis (Reference baseline)**: Volatility Peak = **85.4%**
2. **2020 COVID-19 Demand Shock**: Volatility Peak = **90.0%**
3. **2022 Russia-Ukraine War Outbreak**: Volatility Peak = **49.6%**

These periods of high volatility are highly correlated with spikes in the **Geopolitical Risk (GPR) Index**:
* **Normal Regime Baseline GPR**: $60.2 - 80.5$ points.
* **2014 OPEC Price War**: GPR Peak = **138.3** points.
* **2022 Russia-Ukraine War**: GPR Peak = **280.4** points.
* **2024 Red Sea Shipping Crisis**: GPR Peak = **178.6** points.
* **2026 US-Iran Escalation**: GPR Peak = **197.1** points.

### 3.3 Empirical Distance Statistics between Regimes
The empirical distance metrics computed on the daily log return series of domestic retail petroleum prices confirm a severe distribution shift between the normal (low vol) and tail-risk (high vol) regimes:

| Comparison Pair | Wasserstein Distance ($W_1$) | MMD² (RBF Kernel) | KL Divergence ($D_{KL}$) |
|---|---|---|---|
| **Normal ($P$) vs Medium Vol ($Q_1$)** | 0.8524 | 0.0214 | 0.1205 |
| **Normal ($P$) vs Tail-Risk ($Q_2$)** | **3.4215** | **0.1842** | **1.5640** |

*Interpretation*: The Wasserstein distance and MMD² values are **4x to 8x larger** when comparing the normal regime to the tail-risk regime than when comparing it to the medium volatility regime. This confirms that geopolitical tail risks do not represent typical volatility scaling, but rather **fundamental, structural distribution shifts**. This mathematical evidence justifies the integration of specialized gating routers and localized Wavelet-KAN experts to handle these distinct distribution spaces.
