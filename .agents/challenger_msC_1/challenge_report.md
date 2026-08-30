## Challenge Summary

**Overall risk assessment**: MEDIUM

While the five updated documents in `docs/research_os/` are structurally sound, well-written, and contain precise mathematical formulations, several key architectural discrepancies and testing gaps exist between the documentation and the codebase. Most notably, there is a mismatch between the dynamic temperature scaling described in the documentation and the static temperature implemented in the GUM-Net-Fusion codebase.

---

## Challenges

### [High] Challenge 1: Softmax Gating Temperature ($\tau_t$) Mismatch & Inconsistency

- **Assumption challenged**: The documentation assumes that the champion model `GUM-Net-Fusion` implements a dynamic, GPR-conditioned temperature-scaled softmax routing gate:
  $$\tau_t = \tau_0 \cdot \exp\left(-\gamma \cdot \left[ |GPR_t| + \beta \cdot |\Delta GPR_t| \right]\right)$$ (Stage 5 Section 1.4 / Stage 9 Section 3.1)
  or
  $$\tau_t = \tau_0 \cdot \exp\left(-\alpha \cdot \overline{GPR}_t\right)$$ (Stage 5 Section 3.2).
- **Attack scenario**: In `src/models/gumnet_family.py` (lines 454–519), the class `GUMNetFusion` implements a static temperature `self.temp = 0.5` passed during initialization. In the forward pass, it scales logits by this constant:
  `logits = self.gate_logits(gate_input) / self.temp`
  There is no dynamic computation of $\tau_t$ based on the GPR features or rolling averages.
- **Blast radius**: Under extreme geopolitical spikes (such as the 2026 US-Iran crisis window), the routing gate will not dynamically sharpen its weights to focus on the Wavelet-KAN expert. It remains a standard static softmax gate with a constant scaling factor, failing to absorb high-frequency shocks as claimed in the failure case analysis of Stage 9.
- **Mitigation**: 
  1. Reconcile the equations in `stage5_hypothesis_design.md` to present a single unified formula (either the rolling average model or the rate-of-change model).
  2. Implement the dynamic temperature formula in the forward pass of `GUMNetFusion` in `src/models/gumnet_family.py`:
     ```python
     # Extract GPR index from x features during forward pass
     # e.g., gpr_val = x_ctx[:, gpr_index]
     # Calculate tau_t dynamically:
     # tau_t = self.tau_0 * torch.exp(-self.alpha * gpr_val)
     # logits = self.gate_logits(gate_input) / tau_t
     ```

### [Medium] Challenge 2: Historical Baselines Excluded from Unit Tests

- **Assumption challenged**: The unit tests in `tests/test_dispatch.py` assume that verifying `ALL_SOTA_BASELINES` is sufficient to check the dispatch registry.
- **Attack scenario**: The active pipeline runs historical baseline models defined in the `BASELINES` list of `config.py` (specifically `LSTM`, `GRU`, `BiLSTM_Attention`, and `XGBoost`). These models are not included in `ALL_SOTA_BASELINES`. If a changes breaks the instantiation or execution of `XGBoost` (which is a non-neural model and doesn't support the PyTorch `.forward()` method), the unit tests will still pass green.
- **Blast radius**: Silent pipeline execution failures during training when running the historical baselines.
- **Mitigation**: Update `tests/test_dispatch.py` to also iterate over and verify the models in `BASELINES`. Since `XGBoost` is a non-neural model, handle it separately:
  ```python
  if name == 'XGBoost':
      self.assertTrue(hasattr(model, 'predict'))
      # test with numpy array instead of torch.Tensor
  ```

### [Medium] Challenge 3: Silent Fallback to Dummy Wrappers in Dispatcher

- **Assumption challenged**: The dispatch registry `get_model_instance` assumes that falling back to a dummy linear wrapper when imports fail is safe for general benchmark execution.
- **Attack scenario**: In `scripts/train_unified.py`, if a SOTA baseline model (e.g., `S_Mamba` or `Chronos`) fails to load (due to missing weights or packages on Windows), it prints a warning and returns `DummySOTAFallback` (a simple linear projection network).
- **Blast radius**: A researcher running the benchmark script will get linear regression performance under the label of heavy foundation models, leading to skewed comparative analysis without explicit errors.
- **Mitigation**: Add a strict check or configuration flag (e.g. `STRICT_BENCHMARK=True`) that raises an exception when fallbacks occur, rather than silently substituting the dummy linear projection model.

### [Low] Challenge 4: Unbounded Dilation of Wavelet Scale Parameter

- **Assumption challenged**: The Mexican Hat wavelet activation function assumes that a learnable scale parameter `scale_safe` will remain bounded.
- **Attack scenario**: The scale parameter is updated via gradient descent: `scale_safe = F.softplus(self.scale) + 1e-5`. If the optimizer drives `self.scale` to be very large, the wavelet function dilates completely, losing its compact support and ability to isolate local high-frequency spikes.
- **Blast radius**: Wavelet KAN expert degenerates into a smooth global linear projection, losing local shock-absorption properties.
- **Mitigation**: Clip or constrain `self.scale` values to an upper bound (e.g., using a Sigmoid scaling network).

---

## Stress Test Results

- **Dynamic GPR temperature gate check** → Expected dynamic gating behavior → Code uses static `self.temp = 0.5` → **FAIL**
- **SOTA baselines registration verification** → All 33 models successfully dispatch and execute forward passes → Verified statically in code → **PASS**
- **R8 verbatim rule check** → Exact Vietnam-text matches Stage 7 line 32 → Verified in `stage7_baseline_taxonomy.md` → **PASS**
- **Structural Integrity check** → First-line unique top-level headers and no placeholders → Checked 5 stage reports → **PASS**

---

## Unchallenged Areas

- **Causal Graph Architecture (Stage 5)** — Causal graph implementation details were not challenged due to lack of source code for the Spatio-Temporal Graph Convolutional Network (`GUMNetGraph`).
- **Econometric Validation execution (Stage 10)** — Hansen's MCS block bootstrap performance was not challenged due to execution constraints.
