# CHALLENGE REPORT — 2026-07-17T23:31:00+07:00

## Challenge Summary

**Overall risk assessment**: MEDIUM

While the dispatch registry works flawlessly and the unit tests pass cleanly, there are several discrepancies between the mathematical formulations in the documentation (`docs/research_os/*.md`) and the actual implementation in the codebase, as well as minor internal math inconsistencies in the reports. These issues do not prevent execution but represent gaps in mathematical correctness and scientific alignment.

---

## Challenges

### [Medium] Challenge 1: Code-to-Document Discrepancies (Dynamic GPR-Conditioned Temperature)
- **Assumption challenged**: The reports claim that the champion model `GUM-Net-Fusion` uses a "GPR-conditioned temperature-scaled dynamic router" where the temperature parameter $\tau_t$ is dynamically computed from geopolitical shock metrics.
- **Attack scenario**: If a reviewer inspects the codebase (`src/models/gumnet_family.py`) to replicate this dynamic behavior, they will find that `GUMNetFusion` implements a static temperature hyperparameter (`self.temp`, default 0.5) that is passed to the constructor. The code computes:
  ```python
  logits = self.gate_logits(gate_input) / self.temp
  ```
  No dynamic adjustment of $\tau_t$ using GPR is implemented.
- **Blast radius**: Low-to-Medium. The model runs and trains, but it lacks the dynamic routing behavior described in the manuscript. This represents a clear gap between the scientific claims and the physical implementation.
- **Mitigation**: Update `GUMNetFusion` in `src/models/gumnet_family.py` to implement the dynamic temperature calculation using the GPR columns from the input, or update the documentation to state that a constant temperature is used as a baseline and the dynamic formulation is a theoretical extension.

### [Medium] Challenge 2: GPR Hard-Thresholding Filter Not Implemented
- **Assumption challenged**: The documents (`stage2_conceptual_gaps.md` Section 4 and `stage5_hypothesis_design.md` Section 3.1) state that GUM-Net utilizes a GPR hard-thresholding filter to prevent phantom volatility:
  $$GPR_t^{\text{filtered}} = \text{sgn}(GPR_t) \cdot \max(0, |GPR_t| - 120)$$
- **Attack scenario**: Inspecting `src/preprocess.py` and the data loading/routing pipelines reveals no such filter. The models receive raw GPR features.
- **Blast radius**: Low-to-Medium. Phantom volatility might not be suppressed in flat regions as effectively as the paper claims.
- **Mitigation**: Implement the $GPR_t^{\text{filtered}}$ transformation in `config.py` or the dataset preprocessing pipeline.

### [Low] Challenge 3: Internal Inconsistency of Temperature Formulas
- **Assumption challenged**: The dynamic temperature parameter $\tau_t$ should be defined consistently.
- **Attack scenario**: In `stage5_hypothesis_design.md` Section 1.4 and `stage9_failure_diagnostics.md` Section 3.1, the temperature is defined as:
  $$\tau_t = \tau_0 \cdot \exp\left(-\gamma \cdot \left[ |GPR_t| + \beta \cdot |\Delta GPR_t| \right]\right)$$
  However, in `stage5_hypothesis_design.md` Section 3.2, it is defined as:
  $$\tau_t = \tau_0 \cdot \exp\left(-\alpha \cdot \overline{GPR}_t\right)$$
  where $\overline{GPR}_t$ is a 7-day rolling average.
- **Blast radius**: Low. Confuses the reader about which GPR metrics drive the temperature scaling.
- **Mitigation**: Standardize on a single formulation of $\tau_t$ in the manuscript files.

### [Low] Challenge 4: Numerically Unstable Mexican Hat Wavelet Gradient
- **Assumption challenged**: The analytical gradient derived for the scale parameter $\sigma$ of the Mexican Hat wavelet.
- **Attack scenario**: In `stage5_hypothesis_design.md` Section 3.4, the final derivative is written as:
  $$\frac{\partial \psi}{\partial \sigma} = \frac{\psi(z)}{\sigma} \cdot \left[ \frac{-z^4 + 3.5z^2 - 0.5}{1-z^2} \right]$$
  If a developer attempts to implement this formula directly, they will encounter a division-by-zero error (producing NaN) when $z^2 = 1$. The original un-simplified formulation:
  $$\frac{\partial \psi}{\partial \sigma} = \frac{C}{\sigma} \exp\left(-\frac{z^2}{2}\right) \left[ -z^4 + 3.5z^2 - 0.5 \right]$$
  is numerically stable at $z^2=1$.
- **Blast radius**: Low. PyTorch's autograd handles the gradient computation automatically, so this does not break the codebase, but the documented equation is numerically unstable.
- **Mitigation**: Document the stable form instead of the version divided by $1-z^2$.

### [Low] Challenge 5: Diebold-Mariano Bandwidth Discrepancy
- **Assumption challenged**: Consistent truncation lag (bandwidth) $J$ in the HAC variance estimator.
- **Attack scenario**: `stage10_econometric_validation.md` defines the truncation lag as $J = \min\left(H - 1, \left\lfloor 1.2 \cdot T^{1/3} \right\rfloor\right)$. However, in `scripts/build_manuscript_final.py` line 69, `dm_test_da` computes the bandwidth using $H$ (i.e. `h`) instead of $H-1$, whereas `dm_test_mse` uses $H-1$.
- **Blast radius**: Negligible. Results in very small differences in the calculated $p$-values.
- **Mitigation**: Update `dm_test_da` in `scripts/build_manuscript_final.py` to use `h - 1` for consistency.

---

## Stress Test Results

- **Run unit tests on dispatch registry** (`python -m unittest tests/test_dispatch.py`) → Ensure all GUM-Net variants and SOTA baselines instantiate and run forward passes → **PASS** (2 tests, OK).
- **Check files existence and first-line headers** → Confirm top-level header tags are intact → **PASS** (all 5 files have exact headers).
- **Verify verbatim R8 rule in docs** → Search for R8 clause → **PASS** (present in `stage7_baseline_taxonomy.md` line 32).

---

## Unchallenged Areas

- **Full Model Training Performance**: The downstream impact of not implementing GPR filtering and dynamic temperature on the actual model metrics (e.g. MAPE, $R^2$) was not measured because training takes too long and is outside the review-only scope.
- **Other 13 Stage Documents**: The remaining 13 Markdown documents in `docs/research_os/` were not reviewed in detail, as only the 5 modified stage files were requested.
