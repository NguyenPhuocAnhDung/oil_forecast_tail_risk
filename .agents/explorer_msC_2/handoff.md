# Handoff Report: Milestone C Reports Analysis

This handoff report is prepared by teamwork_preview_explorer (Explorer 2) to summarize the academic analysis of the five reports in `docs/research_os/` to prepare for Milestone C updates.

---

## 1. Observation
We observed and extracted the following technical specifications from the files in `docs/research_os/` and the project configurations:
1. **File paths and structure**:
   - `docs/research_os/stage2_conceptual_gaps.md` lines 21-105: Defined Vietnamese BOG pricing dynamics and the mathematical formulation of the distribution mismatch problem (KL divergence $\to \infty$).
   - `docs/research_os/stage5_hypothesis_design.md` lines 70-126: Formulated routing logits, GPR temperature tuning $\tau_t = \tau_0 \exp(-\alpha \overline{GPR}_t)$, and Mexican Hat wavelets parameter updates.
   - `docs/research_os/stage7_baseline_taxonomy.md` lines 33-53: Classified 11 baselines across 4 theoretical strategies.
   - `docs/research_os/stage9_failure_diagnostics.md` lines 11-100: Formulated four-tier error groups and analyzed the 2026 US-Iran crisis window dynamics.
   - `docs/research_os/stage10_econometric_validation.md` lines 9-117: Outlined the DM test with HAC correction, MCS stationary block bootstrap, and non-parametric effect sizes.
2. **Configuration Constants**:
   - From `.agents/ORIGINAL_REQUEST.md` lines 249-285: Defined `SOTA_TAXONOMY_REGISTRY` with 33 models, `GUM_NET_VARIANTS` with 11 models, and `HORIZON_TEMPORAL_CONFIG`.
3. **Target Equations**:
   - Verbatim formula from the request:
     $$\mathcal{D}_{\text{target}} \sim \sum_{k=1}^K C_k \cdot \mathbb{I}(t \in [T_{k-1}, T_k]) + \epsilon_t \cdot \mathbb{I}(GPR_t \ge GPR_{\text{gate}})$$
   - Verbatim R8 rule:
     "Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu."

---

## 2. Logic Chain
Our synthesis and reasoning from the observations proceeds as follows:
1. **Observation 1.1 & 1.2** show that existing SOTA deep learning models are continuous in nature and fail to represent step-like price functions (BOG adjustments) or sudden structural breaks (GPR shocks). This leads to Gibbs oscillations (phantom volatility) and extrapolation hallucinations.
2. Hence, a **Decoupled Modelling Strategy** (ADF tests) separating xăng (stationary) and dầu (non-stationary) is required (as formulated in **Gap 1**).
3. To locally absorb GPR shocks without destabilizing calm periods, the **Wavelet-KAN Expert** with localized Mexican Hat activation functions is designed (**Gap 2**).
4. The transition between short-term momentum (CNN) and long-term trend/shock (GRU/Wavelet-KAN) forecasting across horizons $H \in \{1, 3, 5, 7, 10, 20, 60\}$ requires a **GPR-Conditioned Temperature-Scaled Dynamic Router** (**Gap 3** and **Tầng 4 Routing**).
5. The validation of these hypotheses requires a robust **Expanding Window Walk-Forward** setup using DM tests with Newey-West HAC variance corrections (truncation lag $J = \min(H-1, \lfloor 1.2 N^{1/3} \rfloor)$) and Model Confidence Set (MCS) bootstrap to prevent multi-testing biases (**Gap 4** and **Stage 10**).
6. To verify failure conditions, we establish a **4-Tier Error Taxonomy** (Type A, B, C, D) and a **2-Phase Evaluation Protocol** (Phase 1: right-censoring at 2026-04-30; Phase 2: worst-case at 2026-05-31) to stress-test the model's robustness under simulated US-Iran crisis scenarios.

---

## 3. Caveats
- **Empirical Execution**: This analysis is read-only and does not execute the actual model training or results generation.
- **Data Availability**: It is assumed that `unified_data.csv` has been extended up to `2026-04-30` as documented in `stage1_problem_reframing.md`.
- **Systematic Errors**: In Type A and B errors, the exact announcement schedules ($T_k$) are assumed to be known or inferred from base import prices ($P^{base}_t$), though in real-world settings adjustments are political and may suffer from unexpected delays.

---

## 4. Conclusion
We have successfully performed a detailed academic analysis of the five reports in `docs/research_os/` and written the comprehensive analysis to `.agents/explorer_msC_2/analysis.md` in standard journal LaTeX format. The analysis provides:
1. A taxonomy of 33 SOTA models across 7 paradigms with technical gaps.
2. Detailed morphological mismatch analysis showing how step-functions cause spectral leakage and Gibbs oscillations.
3. Rigorous mathematical descriptions of the 4-layer GUM-Net architecture variants and routing gates.
4. An econometric validation framework combining DM-HAC, MCS block bootstrap, Cliff's Delta, and Vargha-Delaney A metrics.
5. Falsifiable hypotheses (RQ1-RQ4) and systematic failure case protocols.

---

## 5. Verification Method
To independently verify the analysis:
1. **File Inspection**: Verify that the analysis report exists at `/data/quyhv/oil_forecast_tail_risk/.agents/explorer_msC_2/analysis.md` and contains the verbatim R8 rule and LaTeX equations.
2. **Compile Check**: Verify that all equations in `analysis.md` render correctly as LaTeX.
3. **Execution Plan**: The implementer agent can run the code pipeline (`scripts/run_all_32models.py`) and verify that the models match the names in the taxonomy registry and dispatch code.
