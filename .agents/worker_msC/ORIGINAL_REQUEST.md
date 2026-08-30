## 2026-07-17T16:22:51Z

You are teamwork_preview_worker.
Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/worker_msC.
Your mission is to implement the academic documentation and report updates for Milestone C based on the synthesized analysis findings.

Your tasks:
Update the 5 Markdown reports in docs/research_os/ using the precise formulations and structures from the synthesis report (at /data/quyhv/oil_forecast_tail_risk/.agents/sub_orch_msC/synthesis.md) and the analysis reports from the Explorers (e.g., at /data/quyhv/oil_forecast_tail_risk/.agents/explorer_msC_1/analysis.md):

1. Update docs/research_os/stage2_conceptual_gaps.md:
   - Update ## CORE_RESEARCH_GAP_MATRIX to include:
     - The 33-model taxonomy table classifying models (11 historical baselines + 22 modern SOTAs) across 7 paradigms with technical gaps.
     - LaTeX equation for target distribution:
       $$\mathcal{D}_{\text{target}} \sim \sum_{k=1}^K C_k \cdot \mathbb{I}(t \in [T_{k-1}, T_k]) + \epsilon_t \cdot \mathbb{I}(GPR_t \ge GPR_{\text{gate}})$$
     - Detailed analysis of Morphological Mismatch (between pre-training distribution and step-like target distribution with Dirac delta function) proving that KL divergence is mathematically unbounded ($D_{KL} \to \infty$).
     - The 5 strategic research gaps detailed in Section 1.4 of the analysis report.

2. Update docs/research_os/stage5_hypothesis_design.md:
   - Update ## EXPERIMENTAL_ARCHITECTURE_BLUEPRINT to include:
     - 4-layer structural blueprint mapping the 10 GUM-Net variants (Mamba, iTrans, Wavelet, Patch, Fourier, Diffusion, Graph, RL, MoE-Sparse, Fusion) with their respective LaTeX equations.
     - 4 Research Questions (RQ1-RQ4) and their null ($H_0$) and alternative ($H_1$) hypotheses.

3. Update docs/research_os/stage7_baseline_taxonomy.md:
   - Update ## BENCHMARK_TAXONOMY_MATRIX to include:
     - Extended taxonomy matrix contrasting the architectural philosophies and vulnerabilities under geopolitical risk for the SOTA paradigms.
     - Include the verbatim R8 rule:
       "Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu."
     - Python dispatch registry code mapping string identifiers to PyTorch modules.

4. Update docs/research_os/stage9_failure_diagnostics.md:
   - Update ## POST_MORTEM_DIAGNOSTICS_REPORT to include:
     - Anti-fabrication constraints: zero hardcoded statistical values, requiring programmatic estimation of all diagnostics directly from out-of-sample residuals.
     - 4 systematic error groups: Type A (Trend Miss), Type B (Regime Delay), Type C (Overshoot), Type D (Policy Plateau) with description and mathematical indicators.
     - 2-phase temporal evaluation protocol for the 2026 US-Iran crisis window (Phase 1: 2026-04-30 right-censoring; Phase 2: 2026-05-31 worst-case).

5. Update docs/research_os/stage10_econometric_validation.md:
   - Update ## STATISTICAL_VALIDATION_VERDICT to include:
     - Journal-ready LaTeX formulas for Diebold-Mariano test with Newey-West HAC variance correction.
     - Hansen's Model Confidence Set (MCS) bootstrap protocol (alpha=0.05) with Stationary Block Bootstrap.
     - Non-parametric effect size measures (Cliff's Delta and Vargha-Delaney A_12).

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Verify your changes:
Ensure all markdown documents render mathematics cleanly and follow proper LaTeX notation. Run any checks to confirm formatting validity.

Write a handoff report at /data/quyhv/oil_forecast_tail_risk/.agents/worker_msC/handoff.md detailing the files updated and verification results.
Notify the parent agent (conversation ID: d4d84ace-29f5-4b18-bce2-c92ab2ee837e) when done by sending a message using the send_message tool.
