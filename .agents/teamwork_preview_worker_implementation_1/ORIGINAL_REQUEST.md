## 2026-07-17T09:18:22Z

You are teamwork_preview_worker.
Your working directory is: /data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_worker_implementation_1

Your mission is to implement all scientific, mathematical, and tabular edits in the paper draft files inside `docs/` exactly as specified in the proposal file:
`/data/quyhv/oil_forecast_tail_risk/.agents/orchestrator/PROPOSAL.md`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please execute the following:
1. Read `/data/quyhv/oil_forecast_tail_risk/.agents/orchestrator/PROPOSAL.md` for exact instructions.
2. Edit the following files under `docs/`:
   - `Part_2_RelatedWork.md`
   - `Part_3_Methodology.md`
   - `Methodology_Tail_Risk.md`
   - `Evaluation_Scenarios_Draft.md`
3. Run the end-to-end dry run test script `python scripts/e2e_test.py` to verify that the codebase is completely healthy and nothing is broken. Record the command output and result in your handoff.
4. Write a detailed `progress.md` tracking your steps.
5. Write a comprehensive `handoff.md` summarizing the changes made and the dry run verification results.
6. When done, send a message to the Project Orchestrator (Conversation ID: 48a59f00-589b-4d70-b3c9-d4e38195b228) with the path to your handoff report.


## 2026-07-17T13:50:13Z

Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_worker_implementation_1/.
Your task is to implement Milestone 2 (Phase A: Stages 0, 1, 2, and 2.5 of the Research OS) and output four separate Markdown files under `docs/research_os/`:
1. `docs/research_os/stage0_dataset_governance.md`
2. `docs/research_os/stage1_problem_reframing.md`
3. `docs/research_os/stage2_conceptual_gaps.md`
4. `docs/research_os/stage2_5_regime_characterization.md`

Under no circumstances should you edit source code files or run tests yourself without running verification commands. All files should be written cleanly.

For each file:
- **Stage 0 (Dataset Governance)**: Include `## DATASET_GOVERNANCE_REPORT`. Create a detailed Dataset Card for `data/processed/unified_data.csv`. The actual dataset dimensions are 4,471 rows and 20 columns, ranging from `2008-11-03` to `2026-02-27`. You MUST run the stationarity script `scripts/run_advanced_stats.py` or inspect its outputs to include the actual Augmented Dickey-Fuller (ADF) and KPSS unit root test statistics for the retail prices (xăng/dầu: MG95, DO 0.05%) and their log returns. Document the parameters and statistics precisely.
- **Stage 1 (Problem Reframing)**: Include `## PROBLEM_FORMULATION_DIRECTIVE`. Define the research theme "Theory-Informed Robust Forecasting under Sequential Geopolitical Tail Risks". Break down the 5 tail risk windows as sequential structural break windows: (1) 2014 OPEC price war, (2) 2020 COVID shock, (3) 2022 Russia-Ukraine war, (4) 2024 Red Sea shipping crisis, and (5) 2026 US-Iran escalation (extended to May 2026, though note the dataset ends in Feb 2026).
- **Stage 2 (Conceptual Gaps)**: Include `## CORE_RESEARCH_GAP_MATRIX`. Detail the 5 core strategic research gaps. Analyze the mathematical problem of 'Distribution Mismatch' of Foundation Models when predicting Vietnamese retail petroleum prices, which are heavily governed by the BOG (stabilization fund) policy showing step-like behavior (step-functions).
- **Stage 2.5 (Regime Characterization)**: Include `## REGIME_CHARACTERIZATION_PROTOCOL`. Specify the Bai-Perron structural break detection algorithm and CUSUM process. Define the mathematical formulas for Wasserstein distance, Maximum Mean Discrepancy (MMD), and KL Divergence between the normal regime and tail-risk regimes. Run/examine the relevant scripts to back up this protocol with statistics.

MANDATORY INTEGRITY WARNING: DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

When completed, verify that the four files are successfully written to `docs/research_os/`, write your handoff report to `/data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_worker_implementation_1/handoff.md`, and send a message back to parent conversation ID 53d1d6fc-5e29-43fe-b494-a6aaa3afca7b.
