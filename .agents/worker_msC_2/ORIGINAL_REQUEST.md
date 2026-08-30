## 2026-07-17T16:29:31Z
You are teamwork_preview_worker.
Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/worker_msC_2.
Your mission is to fix the missing verbatim R8 rule in docs/research_os/stage10_econometric_validation.md.

Your tasks:
1. Open docs/research_os/stage10_econometric_validation.md and look at section "## 4. Integration of Requirement R8 SOTA Selection Policy".
2. Under "## 4. Integration of Requirement R8 SOTA Selection Policy" (for example, as a new sub-section "### 4.1.1 Verbatim Scientific Integrity Clause (R8 Rule)" or directly under "### 4.1 Comparison Rules"), insert the verbatim R8 selection rule:
   "Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu."
   Ensure it is formatted cleanly (e.g. as a blockquote or bold text) and matches the exact wording.
3. Do NOT modify any other files or make any other changes.
4. Run the project tests using "python -m unittest tests/test_dispatch.py" to verify everything is functional.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write a handoff report at /data/quyhv/oil_forecast_tail_risk/.agents/worker_msC_2/handoff.md detailing the files updated and verification results.
Notify the parent agent (conversation ID: d4d84ace-29f5-4b18-bce2-c92ab2ee837e) when done by sending a message using the send_message tool.
