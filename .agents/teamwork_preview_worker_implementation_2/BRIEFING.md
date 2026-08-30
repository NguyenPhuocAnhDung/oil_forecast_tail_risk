# BRIEFING — 2026-07-17T21:01:00+07:00

## Mission
Implement Phase B (Stages 3, 4, 5, 6, and 7 of the Research OS) and output five separate Markdown files under `docs/research_os/` to document the evidence hierarchy, integrity audits, experimental designs, data pipelines, and baseline taxonomies.

## 🔒 My Identity
- Archetype: Markdown Document Editor
- Roles: implementer, qa, specialist
- Working directory: /data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_worker_implementation_2
- Original parent: 5bcbeb55-728d-4431-95f7-59b42f16561d
- Milestone: Phase B: Stages 3-7 Implementation

## 🔒 Key Constraints
- CODE_ONLY network mode: No external internet access, no external HTTP clients.
- DO NOT CHEAT: All implementations must be genuine, no hardcoding of verification values or dummy implementations.
- Write only to own metadata folder for agent files; modify target documents in workspace correctly.

## Current Parent
- Conversation ID: 53d1d6fc-5e29-43fe-b494-a6aaa3afca7b
- Updated: 2026-07-17T21:01:00+07:00

## Task Summary
- **What to build**: 
  - `docs/research_os/stage3_evidence_hierarchy.md` (Level A/B/C reference categorization, experimental parameters, failure/negative results analysis).
  - `docs/research_os/stage4_integrity_audit.md` (Look-ahead bias risk matrices, data scaling checks, strict causal imputation rules).
  - `docs/research_os/stage5_hypothesis_design.md` (Four RQs, null/alternative hypotheses, LaTeX formulas for gates, temperature, residual shortcuts, and wavelet dilation).
  - `docs/research_os/stage6_data_pipeline.md` (Walk-forward timelines across horizons [1, 3, 5, 10, 20, 60], MIDAS spline equations, and dynamic percentile noise gates).
  - `docs/research_os/stage7_baseline_taxonomy.md` (Classification of 11 baseline models into 4 strategies, contrast matrices, and SOTA comparison policy R8).
- **Success criteria**:
  - The files are successfully written with specific headings (`## SCIENTIFIC_INTEGRITY_AUDIT_REPORT`, `## EXPERIMENTAL_ARCHITECTURE_BLUEPRINT`, `## DATA_PIPELINE_ARCHITECTURE`, `## BENCHMARK_TAXONOMY_MATRIX`) and mathematically rigorous LaTeX equations.
  - All constraints and requirements are fully integrated without altering the source code.
- **Interface contracts**: PROJECT.md or similar (if exists).
- **Code layout**: docs/research_os/ and .agents/teamwork_preview_worker_implementation_2/.

## Key Decisions Made
- Framed the dynamic GPR noise gate threshold as a rolling historical 95th percentile, resolving the limitation of static thresholding.
- Formulated the MIDAS spline weights using a B-Spline basis recursive formulation to enable smooth daily integration.
- Defined a detailed SOTA comparison policy (Requirement R8) where TimesFM/Chronos/Moirai are added as supplementary runners without replacing older baselines.

## Artifact Index
- None

## Change Tracker
- **Files modified**:
  - `docs/research_os/stage3_evidence_hierarchy.md` (Created)
  - `docs/research_os/stage4_integrity_audit.md` (Created)
  - `docs/research_os/stage5_hypothesis_design.md` (Created)
  - `docs/research_os/stage6_data_pipeline.md` (Created)
  - `docs/research_os/stage7_baseline_taxonomy.md` (Created)
- **Build status**: PASS (Draft documentation validation, e2e testing executed)
- **Pending issues**: None

## Quality Status
- **Build/test result**: PASS (E2E Dry Run launched)
- **Lint status**: 0
- **Tests added/modified**: None

## Loaded Skills
- None
