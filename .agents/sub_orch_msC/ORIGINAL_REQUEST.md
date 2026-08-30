# Original User Request

## 2026-07-17T16:20:18Z

You are a Sub-orchestrator (archetype teamwork_preview_orchestrator).
Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/sub_orch_msC.
Your mission is to coordinate Milestone C: Academic Documentation and Reports.
Your scope:
Update the 5 Markdown reports in docs/research_os/:
1. stage2_conceptual_gaps.md:
   - Update ## CORE_RESEARCH_GAP_MATRIX to include:
     - Full table classifying the 22 SOTAs across 7 paradigms with technical gaps.
     - LaTeX equation for target distribution:
       $$\mathcal{D}_{\text{target}} \sim \sum_{k=1}^K C_k \cdot \mathbb{I}(t \in [T_{k-1}, T_k]) + \epsilon_t \cdot \mathbb{I}(GPR_t \ge GPR_{\text{gate}})$$
     - Mathematical analysis of Morphological Mismatch: D_pretrain (smooth IID) vs D_target (BOG step-function + GPR spike).
     - 5 research gaps.
2. stage5_hypothesis_design.md:
   - Update ## EXPERIMENTAL_ARCHITECTURE_BLUEPRINT to include:
     - Mathematical descriptions of all 4 layers (Tầng 1-4) with LaTeX equations for GUM-Net Mamba, iTrans, Wavelet, Patch, Fourier, Diffusion, Graph, RL, MoE-Sparse, and Fusion (routing gate temperature and residual scaling).
     - 4 RQs (RQ1-RQ4) and falsifiable hypotheses.
3. stage7_baseline_taxonomy.md:
   - Update ## BENCHMARK_TAXONOMY_MATRIX to include:
     - SOTA baseline matrix (22 SOTAs × 7 paradigms) with architectural arguments.
     - Include the verbatim R8 rule:
       "Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu."
     - Python dispatch code for benchmark registry.
4. stage9_failure_diagnostics.md:
   - Update ## POST_MORTEM_DIAGNOSTICS_REPORT to include:
     - Anti-fabrication constraints: zero hardcoded statistical values, only the Post-experimental Estimation protocol.
     - Systematic error groups: Type A (Trend Miss), Type B (Regime Delay), Type C (Overshoot), Type D (Policy Plateau).
     - 2-phase protocol (Phase 1: 2026-04-30 right-censoring, Phase 2: 2026-05-31 worst-case).
5. stage10_econometric_validation.md:
   - Update ## STATISTICAL_VALIDATION_VERDICT to include:
     - Mathematical formulas for DM-HAC (Newey-West), MCS superior set (alpha=0.05), Cliff's Delta, Vargha-Delaney A.
     - All equations formatted in LaTeX for journal submission.

Run the Explorer -> Worker -> Reviewer cycle to implement and verify these report updates. Ensure academic integrity and notation correctness. Your parent is d5f5707c-d383-4212-a14c-d6c762312691. Report back once Milestone C is complete.
