# Stage 13: Technical Manuscript Planner & Blueprint

This document outlines the blueprint for a manuscript targeting a Q1 journal (e.g., *Energy Economics* or *Applied Energy*). It defines the manuscript map, anchors mathematical and empirical assets, and highlights GUM-Net's core scientific contributions.

---

## ## TECHNICAL_MANUSCRIPT_MAP

### Target Journals
* **Energy Economics** (Elsevier, Q1, Impact Factor ~12): Focus on econometric rigor, policy implications, and risk modeling.
* **Applied Energy** (Elsevier, Q1, Impact Factor ~11): Focus on energy system engineering, forecasting applications, and technical novelty.

---

### IMRaD Manuscript Outline

```
+-----------------------------------------------------------------------------+
|                        MANUSCRIPT ANCHOR MAP                                |
+-----------------------------------------------------------------------------+
|                                                                             |
|  1. INTRODUCTION -------------------------- [Contribution 1, 2, 3]          |
|                                                                             |
|  2. LITERATURE REVIEW --------------------- [Taxonomy of Baselines]         |
|                                                                             |
|  3. METHODOLOGY --------------------------- [Eq. 2.1, 2.2, 2.3, 2.4]        |
|                                             [Figure 4.1: Architecture]      |
|                                                                             |
|  4. EXPERIMENTAL SETUP & RESULTS ---------- [Table 4.1: Dataset]            |
|                                             [Table 4.3.1 - 4.3.4: Results]  |
|                                             [Figure 4.2: R² Degradation]    |
|                                             [Figure 4.3: MAPE Bounding]     |
|                                                                             |
|  5. DISCUSSION & ECONOMIC IMPLICATIONS ---- [Figure 4.4: Routing weights]   |
|                                             [Section 4.6 & 4.7: Analysis]   |
|                                                                             |
|  6. CONCLUSION ---------------------------- [Future Backlog]                |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

### Section 1: Introduction
* **Objective**: Introduce the challenge of refined oil product retail price forecasting in emerging markets under geopolitical tail risks. Highlight the limitations of global attention models (Transformers) and simple regression under structural breaks.
* **Anchor: Three Core Scientific Contributions**:
  1. *Decoupled Co-product Modeling Paradigm*: Formulates a strategy that decouples the modeling of co-integrated but distributionally distinct refined petroleum products (stationary gasoline vs. non-stationary, trend-dominated diesel) to prevent signal cross-contamination and capture distinct price-setting policies (BOG step-functions vs. international spot correlations).
  2. *Geopolitical Shock-Absorbing Wavelet-KAN Expert*: Integrates Kolmogorov-Arnold Networks (KAN) with localized Mexican Hat wavelets whose scaling parameter ($\sigma$) is dynamically optimized via backpropagation, coupled with hard-thresholded GPR inputs, allowing the network to absorb sudden geopolitical shocks without global representation collapse.
  3. *Horizon-Aware Dynamic Router with Temperature Scaling*: Deploys a dynamic routing gating mechanism conditioned on both forecasting horizons (via positional embeddings) and geopolitical intensity (via GPR-scaled Softmax temperature $\tau_t$), ensuring optimal routing to specialized experts (CNN for short-term momentum, GRU for long-term trends, Wavelet-KAN for shocks) and preventing expert saturation.

---

### Section 2: Literature Review
* **Objective**: Classify existing modeling paradigms and expose their vulnerabilities.
* **Asset Anchor**: *Benchmark Taxonomy Matrix* (from Stage 7).
* **Content**: Critique Strategy 1 (Transformers - OOD failure), Strategy 2 (Linear models - lack of non-linear shock absorption), and Strategy 3 (CNNs - periodic smearing during crises). Justify the need for Strategy 4 (Theory-Informed Gated MoE).

---

### Section 3: Methodology
* **Objective**: Present the mathematical formulation of GUM-Net.
* **Figure Anchor**: `Figure 4.1: GUM-Net Architectural Flowchart`. Displays the decoupled pathways, the three experts, and the horizon/GPR-conditioned gate.
* **Equation Anchors**:
  * **Equation 1 (Routing head logits)**:
    $$g_j(x_t) = W_g^j x_t + b_g^j$$
    (Defines how input representations, including Positional Embeddings $\text{Pos}_h$ and $GPR_t^{\text{filtered}}$, generate gating logits).
  * **Equation 2 (GPR-Conditioned Softmax Temperature)**:
    $$w_i(x_t) = (1 - \lambda) \cdot \frac{\exp\left(\frac{g_i(x_t)}{\tau_t}\right)}{\sum_{j=1}^3 \exp\left(\frac{g_j(x_t)}{\tau_t}\right)} + \lambda \cdot \frac{1}{3}$$
    $$\tau_t = \tau_0 \cdot \exp\left(-\alpha \cdot \overline{GPR}_t\right)$$
    (Explains how temperature $\tau_t$ sharpens routing weights during crises and averages them during calm regimes).
  * **Equation 3 (Gating Residual Scaling Constraint)**:
    $$\min w_i(x_t) \ge \frac{\lambda}{3} = 0.0333$$
    (Formulates the lower bound that prevents the "dead expert" problem and ensures continuous gradient flow).
  * **Equation 4 (Mexican Hat Wavelet Gradient Update)**:
    $$\frac{\partial \psi}{\partial \sigma} = \frac{C}{\sigma} \exp\left(-\frac{z^2}{2}\right) \left[ -z^4 + 3.5z^2 - 0.5 \right]$$
    (Enables backpropagation to dynamically scale the wavelet's frequency band $\sigma$ to absorb high-frequency price shocks).

---

### Section 4: Experimental Setup & Results
* **Objective**: Present the experimental design, dataset details, and empirical results.
* **Table Anchor: Table 4.1 (Dataset and Window Partition)**:
  * Details the look-back window ($L=30$), training (70%), validation (10%), and testing (20%) splits from 2008 to May 2026 ($N=4,517$ samples).
* **Table Anchors: Empirical Performance Tables**:
  * *Table 4.2 (DA % on Gasoline)*: Anchor for Table 4.3.1 (GUM-Net DA = 79.3% at H60 vs. PatchTST = 54.6%).
  * *Table 4.3 (Point errors on Gasoline)*: Anchor for Table 4.3.2 (GUM-Net MAE/RMSE/MAPE).
  * *Table 4.4 (DA % on Diesel)*: Anchor for Table 4.3.3 (GUM-Net DA = 78.2% at H60 vs. PatchTST = 51.5%).
  * *Table 4.5 (Point errors on Diesel)*: Anchor for Table 4.3.4 (GUM-Net MAE/RMSE/MAPE).
* **Figure Anchors: Visual Analytics**:
  * *Figure 4.2 (R² Degradation Curve)*: Compares $R^2$ decay from H1 to H60, illustrating GUM-Net's stability compared to the steep decline of PatchTST and XGBoost.
  * *Figure 4.3 (MAPE Bounding Chart)*: Illustrates the "emergency brake" effect of Residual Scaling in limiting long-horizon extrapolation errors at H60.

---

### Section 5: Discussion & Econometric Analysis
* **Objective**: Conduct diagnostics, regime analyses, and interpretability evaluations.
* **Figure Anchor: Figure 4.4 (Routing Weights Transition Heatmap)**:
  * Shows the transition of routing weights $w_i$ from $w_1 \approx 0.60$ (CNN dominant at H1) to $w_2 \approx 0.55$ (GRU dominant at H20/H60) and $w_3 \in [0.10, 0.45]$ (Wavelet-KAN active under high GPR).
* **Statistical Validation Anchors**:
  * *Diebold-Mariano Test*: Reports DM statistics with Newey-West HAC variance corrections, showing GUM-Net's error reductions are statistically significant ($p < 0.05$).
  * *Model Confidence Set (MCS)*: Reports that GUM-Net is in the superior set $\widehat{\mathcal{M}}_{0.90}^*$ in 100% of the cases.
  * *Quiet Period Underperformance Analysis*: Discusses why GUM-Net is outperformed by DLinear/LSTM in calm regimes due to routing gate overfitting and GPR noise under BOG step-functions (referencing Diesel H1 and Gasoline H10 data).

---

### Section 6: Conclusion & Policy Implications
* **Objective**: Summarize the paper, formulate policy recommendations for energy planners, and present the future work backlog.
