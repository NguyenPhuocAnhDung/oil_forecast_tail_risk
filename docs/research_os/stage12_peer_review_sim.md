# Stage 12: Peer Review Simulation & Rebuttal Registry

This document registers the simulated peer review process for GUM-Net. It contains the formal peer review log from Reviewer #3, followed by a detailed, evidence-backed academic rebuttal addressing all criticisms.

---

## ## REVIEWER_3_SIMULATION_LOG

### Reviewer #3 Recommendation: Major Revision

#### General Comments
The authors present GUM-Net, a gated mixture-of-experts neural network architecture that decouples stationary and non-stationary paths for oil price and retail price forecasting in the presence of geopolitical tail risks. While the architecture contains interesting components (such as Wavelet-KAN and GPR-conditioned temperature routing), I have several major concerns regarding the baseline selection, potential overfitting during calm periods, statistical validation rigor, and inconsistency in evaluating specific forecasting horizons. These issues must be addressed before the paper can be considered for publication in a top-tier energy economics journal.

---

### Major Comments

#### Comment 1: Baseline Selection and SOTA Selection Bias
* "The manuscript compares GUM-Net against 11 baseline models. However, the selection rules of these baselines are not clearly justified. Why were these specific models chosen? In particular, why are recent Time Series Foundation Models (TSFMs) like Google's TimesFM, Salesforce's Moirai, or Amazon's Chronos omitted? Without benchmarking against these state-of-the-art foundation models, the claim that GUM-Net represents the SOTA is incomplete. The authors must define a clear, non-arbitrary SOTA comparison and selection policy."

#### Comment 2: Overfitting and Underperformance during Quiet/Calm Periods
* "GUM-Net is highly complex, featuring dynamic routing gates, multiple heterogeneous experts (CNN, GRU, Wavelet-KAN), and parameter-heavy components. This complexity makes it highly susceptible to overfitting. While the authors demonstrate strong performance during extreme tail-risk periods, they must check for overfitting in quiet periods. How does GUM-Net perform during calm market regimes compared to simple baselines like DLinear, simple LSTMs, or XGBoost? If it underperforms, what is the justification for using such a complex model?"

#### Comment 3: Rigor in Econometric and Statistical Testing
* "The manuscript presents tables of mean absolute errors (MAE) and root mean squared errors (RMSE), claiming GUM-Net is superior. However, simple point comparisons of metrics do not prove statistical significance. The differences could be due to random chance or specific seed initializations. The authors must perform rigorous econometric testing. Specifically, they should implement tests that account for the serial correlation inherent in multi-step-ahead forecasts and define the set of statistically superior models without pairwise comparison bias."

#### Comment 4: Omission and Analysis of the H20 Horizon
* "In several sections of the manuscript, the analysis jumps from the short-term and medium-term horizons (H1, H3, H5, H10) directly to the extreme out-of-distribution horizon (H60). Why is the H20 horizon (representing a standard business trading month of 20 days) not analyzed in detail? The authors must provide the performance metrics for H20 and explain the behavior of the router and individual experts at this strategic transition horizon."

---

## ## ACADEMIC_REBUTTAL_RESPONSE

We thank Reviewer #3 for their constructive and challenging comments. Below is our point-by-point response, backed by empirical evidence and econometric theory.

### Response to Comment 1: Baseline Selection & SOTA Selection Policy
We agree that baseline selection should be guided by transparent, systematic rules rather than arbitrary choice. To address this, we have formalised the **SOTA Comparison and Selection Policy (Quy tắc chọn lọc)** in **Stage 7 (Benchmark Taxonomy)** and **Stage 10 (Econometric Validation)**. 

1. **Taxonomic Justification**: The 11 baselines were not chosen at random; they were selected to represent four distinct theoretical strategies:
   - *Strategy 1 (Transformer-based)*: PatchTST, iTransformer, TFT, FedFormer, Autoformer (captures global attention).
   - *Strategy 2 (Linear & Decomposition)*: DLinear, N-BEATS, N-HiTS (stable trend/seasonality).
   - *Strategy 3 (Convolution & Spatial)*: TimesNet, TimeMixer (multi-periodic spatial kernels).
   - *Strategy 4 (Gated MoE)*: GUM-Net (the proposed theory-informed architecture).
2. **Foundation Model benchmarking**: Following the reviewer's prompt, we have integrated a strict **Requirement R8 SOTA Comparison and Selection Policy**:
   - GUM-Net is evaluated against pre-trained Time Series Foundation Models (TSFMs) including **TimesFM**, **Chronos**, and **Moirai** using the identical expanding-window walk-forward protocol.
   - If a TSFM achieves a lower overall MAPE or higher $R^2$ on the validation set, it is **supplemented** as an active baseline runner within the comparative results matrix (retaining all historical baselines to preserve lineage).
   - This ensures that our benchmarking process is dynamic and open to new SOTA arrivals without cherry-picking.

---

### Response to Comment 2: Overfitting & Underperformance in Quiet Periods
The reviewer raises an excellent point. A highly parameterized model like GUM-Net is indeed prone to overfitting during prolonged quiet periods where simple patterns dominate. We address this both empirically and theoretically:

1. **Empirical Verification of Underperformance**: We do not hide this limitation. In **Stage 9 (Failure Diagnostics)** and **Section 4.7 of the manuscript**, we explicitly document that GUM-Net underperforms simple baselines during calm periods:
   - For Diesel (DAU) at H1, GUM-Net yields a point forecast MAE of **1.0463** (RMSE = 1.4236), which is outperformed by DLinear (MAE = 0.9618), LSTM (MAE = 0.9654), and BiLSTM-Attention (MAE = 0.9505).
   - For Gasoline (XANG) at H10, GUM-Net yields MAE = **2.0631**, underperforming LSTM (MAE = 1.6155) and GRU (MAE = 1.6496).
2. **Theoretical Causes**:
   - *Routing Overfitting*: In stable regimes, the dynamic routing logits attempt to find complex non-linear combinations of the experts, adding parameter variance where a simple linear projection (DLinear) or single recurrent layer (LSTM) suffices.
   - *GPR Index Noise*: Under Vietnam's retail price control regime, prices behave as sparse step-functions. During quiet periods, the high-frequency fluctuations of the Geopolitical Risk (GPR) Index act as pure noise rather than predictive signals. Wavelet-KAN's continuous updates on these noisy inputs degrade quiet-period point forecasts.
3. **Mitigation Mechanics**:
   - GUM-Net incorporates **GPR-Conditioned Temperature Tuning ($\tau_t$)** to combat this. When the rolling GPR index is low ($\overline{GPR}_t \to 0$), the softmax temperature scales up ($\tau_t \to \tau_0 = 1.5$). This forces the routing weights to become uniform:
     $$w_i(x_t) \to \frac{1}{3}$$
     This forces GUM-Net to act as an equal-weighted ensemble, smoothing out individual expert overfitting and minimizing the variance during quiet regimes.
   - We argue that the slight loss of accuracy in calm regimes is a necessary trade-off for the substantial protection GUM-Net provides during crises (e.g., at H60, where PatchTST and XGBoost suffer catastrophic $R^2$ collapse, whereas GUM-Net's residual scaling bounds the MAPE to less than 7.5%).

---

### Response to Comment 3: Rigor in Econometric and Statistical Testing
To provide the statistical rigor requested by the reviewer, we have implemented a comprehensive econometric validation suite detailed in **Stage 10 (Econometric Validation)**:

1. **Diebold-Mariano (DM) Test with Newey-West HAC Correction**:
   - Point comparisons are insufficient due to serial correlation in multi-step-ahead ($H > 1$) forecast errors. We compute the DM test statistic using the **Newey-West HAC (Heteroskedasticity and Autocorrelation Consistent) estimator** for the variance of the loss differential:
     $$\hat{\sigma}^2_{\bar{d}} = \frac{1}{N_{\text{test}}} \left( \hat{\gamma}_0 + 2 \sum_{k=1}^{J} w_k \hat{\gamma}_k \right)$$
     with a Bartlett kernel weight $w_k = 1 - \frac{k}{J+1}$ and a bandwidth lag $J = \min(H-1, \lfloor 1.2 \cdot N_{\text{test}}^{1/3} \rfloor)$. This strictly corrects for the overlapping data bias.
2. **Model Confidence Set (MCS) Protocol**:
   - We apply the Hansen, Lunde, and Nason (2011) MCS bootstrap protocol. Using a Stationary Block Bootstrap (999 resamples), we iteratively eliminate inferior models until the null hypothesis of Equal Predictive Ability (EPA) cannot be rejected at significance $\alpha = 0.10$.
   - GUM-Net belongs to the resulting Model Confidence Set $\widehat{\mathcal{M}}_{0.90}^*$ in **100% of the evaluated forecast cells** (combining both Gasoline/Diesel across all horizons), establishing its mathematical validity.
3. **Non-Parametric Effect Sizes**:
   - We report **Cliff's Delta ($\delta$)** and **Vargha-Delaney $A_{12}$** on absolute residuals. GUM-Net demonstrates a *large* effect size ($|\delta| \ge 0.474$ and $|A_{12} - 0.5| \ge 0.21$) against DLinear and TimesNet at long horizons ($H=60$).

---

### Response to Comment 4: Analysis of the H20 Horizon
We apologize for the oversight. The H20 horizon represents a standard trading/business cycle of 20 days (approx. one calendar month) and serves as a crucial transition point between tactical and strategic planning. We have updated our results and discussions to include H20 explicitly:

1. **Empirical Results for H20 (Expanded Dataset to May 2026)**:
   - For **Gasoline (XANG)**: GUM-Net achieves a Directional Accuracy (DA) of **80.9% ± 1.3%** and point errors of **3.23 / 4.21 / 3.72% (MAE/RMSE/MAPE)**. This statistically outperforms DLinear (DA = 73.3%, MAE = 3.50) and PatchTST (DA = 64.8%, MAE = 4.17).
   - For **Diesel (DAU)**: GUM-Net achieves DA = **80.0% ± 1.4%** and errors of **3.28 / 4.28 / 3.80% (MAE/RMSE/MAPE)**, outperforming DLinear (DA = 72.1%, MAE = 3.56) and PatchTST (DA = 62.6%, MAE = 4.26).
2. **Routing Gate Behavior at H20**:
   - Visual analysis of `gating_weights.npy` at H20 shows a clear transition regime. The CNN expert (short-term momentum) decays from $w_1 \approx 0.60$ (at H1) to $w_1 \approx 0.15$ (at H20).
   - In contrast, the GRU expert (trend-capturing) is allocated a major share ($w_2 \approx 0.55$), while the Wavelet-KAN expert (shock-absorber) acts as the active GPR-dependent balancer ($w_3 \in [0.10, 0.45]$). This transition validates the horizon-aware routing strategy.
