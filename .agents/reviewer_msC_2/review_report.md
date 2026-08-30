# Milestone C Review & Adversarial Challenge Report

**Date**: 2026-07-17T23:30:00+07:00
**Reviewer ID**: reviewer_msC_2 (Reviewer 2)
**Workspace**: `oil_forecast_tail_risk`

---

## Part 1: Quality Review

### Review Summary

**Verdict**: **REQUEST_CHANGES**

GUM-Net's updated Milestone C reports in `docs/research_os/` are of exceptional quality, presenting rigorous mathematical formulations, a clear model taxonomy, and an explicit evaluation protocol for tail risk under BOG regulatory interventions. However, a critical omission has been detected: the verbatim R8 selection rule is absent from `docs/research_os/stage10_econometric_validation.md`. 

Approval is deferred until this missing verbatim text is restored.

---

### Findings

#### [Major] Finding 1: Missing Verbatim R8 Rule in Econometric Validation
- **What**: The verbatim R8 selection rule is absent in the Econometric Validation report.
- **Where**: `docs/research_os/stage10_econometric_validation.md` (specifically Section 4: Integration of Requirement R8 SOTA Selection Policy).
- **Why**: The Milestone C instructions explicitly require the verbatim R8 selection rule to be present exactly in both `stage7_baseline_taxonomy.md` and `stage10_econometric_validation.md`. While `stage7` contains the Vietnamese string block verbatim, `stage10` only references it conceptually.
- **Suggestion**: Add the verbatim Vietnamese quote to Section 4 of `stage10_econometric_validation.md`:
  > **"Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu."**

#### [Minor] Finding 2: Singularities in Wavelet-KAN Gradient Updates
- **What**: Potential mathematical division-by-zero or gradient explosion.
- **Where**: `docs/research_os/stage5_hypothesis_design.md` (Equation 150).
- **Why**: The partial derivative of the Mexican Hat wavelet activation function with respect to the scale parameter $\sigma$ is formulated as:
  $$\frac{\partial \psi}{\partial \sigma} = \frac{\psi(z)}{\sigma} \cdot \left[ \frac{-z^4 + 3.5z^2 - 0.5}{1-z^2} \right]$$
  If the normalized input coordinate $z = \pm 1$, the denominator $1-z^2$ becomes $0$, leading to a mathematical singularity.
- **Suggestion**: Document in the text or the code implementation that a tiny stabilization epsilon ($\epsilon = 1\text{e-}6$) is added to the denominator, or that $z$ is clamped away from $\pm 1$ during backward passes.

---

### Verified Claims

1. **R8 Rule in Taxonomy** → verified via `grep_search` and `view_file` → **PASS**
   - *Verbatim text checked*: `> **"Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu."**` is exactly present in `stage7_baseline_taxonomy.md` at line 32.

2. **No Placeholder Tags or Incomplete Text** → verified via `grep_search` → **PASS**
   - A regex-based search for patterns like `TBD`, `TODO`, `FIXME`, `placeholder`, and `[insert` yielded zero matches across all five target files.

3. **LaTeX Math Rendering Quality** → verified via manual math syntax audit → **PASS**
   - Equations across all documents are syntactically correct in LaTeX, using standard environments (e.g. `\begin{cases}`) and spacing conventions suitable for high-impact journal publications.

4. **Python Dispatch Code Syntax Cleanliness** → verified via static analysis → **PASS**
   - The Python code segment in `stage7_baseline_taxonomy.md` is syntactically valid. The `SOTAModelWrapper` correctly implements the `forward` method using PyTorch reshaping, and the `get_model_instance` dispatcher is fully decoupled.

---

### Coverage Gaps

- **Offline Wrappers Execution Flow on Windows Platforms** — risk level: **Medium**
  - *Recommendation*: Since pre-trained weights for global foundation models (TimesFM, Chronos) might be large or require Linux-specific dependencies, the execution path on Windows depends on the fallback behavior of `SOTAModelWrapper`. It is recommended to verify that this fallback is automatically triggered when offline weights are unavailable to prevent unit tests from crashing.

---

### Unverified Items

- **Dynamic Execution of `tests/test_dispatch.py`**
  - *Reason*: The terminal execution via `run_command` timed out waiting for user permission.
  - *Mitigation*: Performed an exhaustive manual code review of both `tests/test_dispatch.py` and `scripts/train_unified.py` and confirmed they align structurally and syntactically.

---

## Part 2: Adversarial Challenge

### Challenge Summary

**Overall risk assessment**: **MEDIUM**

The proposed model architecture uses highly innovative mechanisms (Wavelet-KAN, GPR-conditioned temperature-scaled gates, and Residual Scaling) to solve the BOG policy-induced target distribution mismatch. However, stress-testing these mechanisms reveals three major vulnerability scenarios.

---

### Challenges

#### [High] Challenge 1: Logit Window Delay under Sudden Geopolitical Spikes
- **Assumption Challenged**: Softmax gating weights adapt instantaneously to sudden shocks.
- **Attack Scenario**: GUM-Net computes the rolling GPR average $\overline{GPR}_t$ over a $K=7$ day window. Under a sudden crisis (e.g. GPR spikes from 60 to 380 in 24 hours), the rolling window average takes several days to peak. During these critical first 1-3 days, the temperature $\tau_t$ remains high, meaning the router continues to distribute significant weights to the CNN and GRU experts.
- **Blast Radius**: The model fails to isolate the shock immediately, resulting in substantial Type A (Trend Miss) errors at the onset of a crisis.
- **Mitigation**: Implement an asymmetric rolling filter that reacts instantly to upward spikes (e.g., using $\max(GPR_t, \overline{GPR}_t)$ rather than a simple average) while keeping the smoothing effect for calm periods.

#### [Medium] Challenge 2: Singularity at $z^2 = 1$ in Mexican Hat Gradient Flow
- **Assumption Challenged**: The parameterized scale update for Mexican Hat Wavelets is stable.
- **Attack Scenario**: The gradient of the wavelet function $\psi(z)$ with respect to scale $\sigma$ contains the term $\frac{1}{1-z^2}$. In training, inputs that map to $z = \pm 1$ will cause the gradient to explode to infinity.
- **Blast Radius**: Training instability, resulting in `NaN` weights in the KAN layer and eventual model collapse.
- **Mitigation**: Stabilize the gradient formulation by rewriting it without the division:
  $$\frac{\partial \psi}{\partial \sigma} = \frac{C}{\sigma} \exp\left(-\frac{z^2}{2}\right) \left[ -z^4 + 3.5z^2 - 0.5 \right]$$
  The implementation must directly evaluate this stable form rather than the simplified form containing the $(1-z^2)$ denominator.

#### [Medium] Challenge 3: Stationary Block Bootstrap Length Mismatch
- **Assumption Challenged**: The block length $b = \lfloor T^{1/4} \rfloor$ is adequate to preserve dependencies.
- **Attack Scenario**: For a dataset of $T = 256$ steps, the block length is $b = 4$ days. However, the regulatory BOG price adjustments occur in 7-day or 10-day cycles. A block length of 4 will systematically break the step-function dependency structure of the target series during bootstrapping.
- **Blast Radius**: Underestimated bootstrap standard errors in Hansen's MCS, leading to overconfident inclusion of weak models in the superior set.
- **Mitigation**: Set the bootstrap block length $b$ to match the BOG policy interval (i.e. $b = 7$ or $b = 10$).

---

### Stress Test Predictions

| Scenario (Input Stress) | Expected Behavior | Predicted Behavior | Verdict |
| :--- | :--- | :--- | :--- |
| **GPR spike from 50 to 350 in 1 step** | Immediate activation of Wavelet-KAN ($w_{KAN} > 0.90$) | Delayed activation over 3-4 steps due to $K=7$ rolling average | **FAIL** (Logit Window Delay) |
| **Wavelet input $z = 1.0$** | Smooth backward pass | Gradient explosion / `NaN` values | **FAIL** (Singularity at $z^2=1$) |
| **BOG adjustment cycle of 7 days** | Bootstrap preserves step structure | Bootstrap disrupts price-step jumps due to $b=4$ | **FAIL** (Autocorrelation Loss) |

---

### Unchallenged Areas

- **Causal Graph ST-GCN Structure**: The structure of the causal graph $G = (V, E)$ containing Brent, WTI, Platts, and Retail was not challenged due to the lack of empirical correlation statistics of international crude prices inside the reports.
