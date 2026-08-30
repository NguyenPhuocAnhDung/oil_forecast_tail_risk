# Plan - Research OS Implementation

This plan outlines the 17-stage implementation of the Research OS for GUM-Net under geopolitical tail risk. All report files will be generated in `docs/research_os/` as separate Markdown files.

## Milestones

### Milestone 1: Initialization & Exploration (Stages 0-2.5 Planning)
- Create the metadata files (`plan.md`, `progress.md`, `BRIEFING.md`).
- Spawn `teamwork_preview_explorer` to inspect `data/processed/unified_data.csv`, standard research models, existing draft papers in `docs/`, and any relevant python scripts.

### Milestone 2: Implementation Phase A - Data Governance, Reframing, Gaps & Break Analysis (Stages 0, 1, 2, 2.5)
- **Stage 0 (Dataset Governance)**: 특写 `unified_data.csv` card + ADF & KPSS.
- **Stage 1 (Problem Reframing)**: Structural break analysis framework for 5 tail risks.
- **Stage 2 (Conceptual Gaps)**: Distribution Mismatch math, 5 gaps vs 10 SOTA.
- **Stage 2.5 (Regime Characterization)**: Bai-Perron/CUSUM mathematical design, Wasserstein/MMD/KL divergences.
- Spawn a Worker to perform/implement these stages and generate the Markdown files in `docs/research_os/`.

### Milestone 3: Implementation Phase B - Evidence, Bias, Hypothesis, Pipeline & Baselines (Stages 3, 4, 5, 6, 7)
- **Stage 3 (Evidence Hierarchy)**: Literature classification (Level A, B, C) and negative results.
- **Stage 4 (Look-Ahead Bias Audit)**: Search data pipeline and pre-processing for future leaks.
- **Stage 5 (Falsifiable Design)**: RQ1-RQ4, hypotheses, temperature tuning $\tau_t$ and residual parameter $\lambda$ equations.
- **Stage 6 (Data Pipeline)**: Walk-forward validation with H20 & interpolated MIDAS GPR, historical percentile noise gate.
- **Stage 7 (Taxonomic Baseline)**: 11 baselines categorized, architectural philosophy contrast, integrate R8 (TimesFM, Chronos, Moirai selection rules).
- Spawn a Worker to implement these stages and generate the Markdown files in `docs/research_os/`.

### Milestone 4: Implementation Phase C - Experiment Execution, Failures, Econometrics & XAI (Stages 8, 9, 10, 11)
- **Stage 8 (Experiment Execution)**: 10 seeds freezing, output checkpoint schema.
- **Stage 9 (Failure Case Analysis)**: Type A, B, C, D error taxonomy, temporal dynamics analysis (April vs May 2026).
- **Stage 10 (Econometric Validation)**: Diebold-Mariano with Newey-West HAC, MCS, Vargha-Delaney A / Cliff's Delta, integrate R8 rules.
- **Stage 11 (XAI Attributions)**: Routing weight dynamics $[w_1, w_2, w_3]$, counterfactual test $GPR_t \to 0$.
- Spawn a Worker to implement these stages and generate the Markdown files in `docs/research_os/`.

### Milestone 5: Implementation Phase D - Peer Review, Manuscript, Publication, Pedagogy & Audit (Stages 12, 13, 14, 15, 16)
- **Stage 12 (Peer Review Sim)**: Rebuttal for Reviewer #3.
- **Stage 13 (Technical Manuscript Planner)**: IMRaD roadmap for Q1 journal.
- **Stage 14 (Decision Layer)**: Decision policy for corporate hedging, novelty fit.
- **Stage 15 (Scientific Pedagogy)**: Adaptive shock absorber spring metaphor.
- **Stage 16 (Workflow Audit)**: Knowledge graph nodes/edges and Sprint Backlog.
- Spawn a Worker to implement these stages and generate the Markdown files in `docs/research_os/`.

### Milestone 6: Global Consistency Check & Validation
- Scan paper drafts in `docs/` and verify they align with the results in `docs/research_os/`.
- Run Challenger to verify correctness of data tables and logic.
- Run Forensic Auditor to audit the entire project workspace for integrity.
