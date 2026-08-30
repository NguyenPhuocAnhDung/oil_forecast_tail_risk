## 2026-07-17T14:02:46Z
Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_worker_implementation_3/.
Your task is to implement Milestone 4 (Phase C: Stages 8, 9, 10, and 11 of the Research OS) and output four separate Markdown files under `docs/research_os/`:
1. `docs/research_os/stage8_experiment_execution.md`
2. `docs/research_os/stage9_failure_diagnostics.md`
3. `docs/research_os/stage10_econometric_validation.md`
4. `docs/research_os/stage11_explainable_ai.md`

Under no circumstances should you edit source code files or run tests yourself without running verification commands. All files should be written cleanly.

For each stage:
- **Stage 8 (Experiment Execution)**: Include `## EXPERIMENT_PIPELINE_LOG`. Detail the random-seed freezing protocol for 10 independent runs (seeds 42, 101, 2023, 777, 999, 123, 456, 888, 1111, 2026). Specify the exact checkpoint directory structures (`results_v4/checkpoints/` and logs). Document the training hyperparameters (learning rate, optimizer, early stopping, batch size, etc.).
- **Stage 9 (Failure Case Analysis)**: Include `## POST_MORTEM_DIAGNOSTICS_REPORT`. Construct the 4-tier error taxonomy for forecasting residuals: Type A (underestimation of sudden price jumps), Type B (lagged adjustment to step-function BOG decisions), Type C (macro-noise pollution in quiet regions), Type D (horizon-dependent phase shift). Perform a temporal dynamics audit for the 2026 US-Iran crisis window, contrasting the short-medium term phase (cross-sectional slice at the end of April 2026) vs the long-term phase (full sequence at the end of May 2026).
- **Stage 10 (Econometric Validation)**: Include `## STATISTICAL_VALIDATION_VERDICT`. Detail the Diebold-Mariano (DM) test using the Newey-West Heteroskedasticity and Autocorrelation Consistent (HAC) variance estimator to handle serial correlation in multi-step forecast errors. Specify the Model Confidence Set (MCS) bootstrap protocol (Hansen et al., 2011) to isolate the superior set of models. Define effect size metrics Cliff's Delta and Vargha-Delaney A to quantify the magnitude of GUM-Net's performance gains. Ensure the SOTA comparison and selection rules from Requirement R8 are fully integrated here.
- **Stage 11 (XAI Attributions)**: Include `## EXPLAINABLE_AI_VERDICT`. Mathematically detail the gating routing attributions. Trace how the routing weights $[w_1, w_2, w_3]$ dynamically shift between the CNN expert (local features), GRU-Attention (long-term trends), and Wavelet-KAN (nonlinear shock absorption) as GPR changes. Describe the counterfactual evaluation protocol: artificially setting $GPR_t \to 0$ during the peak of the 2022 Russia-Ukraine war to measure the routing gate's sensitivity and the resulting performance degradation (proving the necessity of geopolitical risk features).

MANDATORY INTEGRITY WARNING: DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

When completed, verify that the four files are successfully written to `docs/research_os/`, write your handoff report to `/data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_worker_implementation_3/handoff.md`, and send a message back to parent conversation ID 53d1d6fc-5e29-43fe-b494-a6aaa3afca7b.
