# BRIEFING — 2026-07-17T23:25:00+07:00

## Mission
Analyze training/inference in train_unified.py, identify reusable elements, and design an implementation plan for 5 scripts under scripts/ for Milestone B.

## 🔒 My Identity
- Archetype: Lead Explorer
- Roles: Lead Explorer
- Working directory: /data/quyhv/oil_forecast_tail_risk/.agents/explorer_msB_1
- Original parent: 9a5de971-c13e-48d8-ab17-8a0d02ea22af
- Milestone: Milestone B

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Code-only network restrictions (no external HTTP calls)
- Follow all teamwork explorer/handoff protocols

## Current Parent
- Conversation ID: 9a5de971-c13e-48d8-ab17-8a0d02ea22af
- Updated: 2026-07-17T23:25:00+07:00

## Investigation State
- **Explored paths**: `scripts/train_unified.py`, `config.py`, `scripts/compile_results.py`, `scripts/compile_fair_results.py`, `scripts/dm_test_da.py`, `scripts/model_confidence_set.py`, `scripts/run_multi_seed.py`, `scripts/run_all.py`, `scripts/plot_paper_figures.py`, `src/evaluation/statistical_tests.py`, `tests/test_dispatch.py`, `docs/research_os/stage10_econometric_validation.md`, `docs/research_os/stage7_baseline_taxonomy.md`, `docs/research_os/stage2_conceptual_gaps.md`.
- **Key findings**:
  - `train_unified.py` saves output files in `results_v4/{protocol}/{model}/{target}_H{horizon}_seed{seed}/` in formats: `results.json` (point/interval metrics with `"datetime"`), `predictions.csv` (true/pred/q10/q90 alternating by product), `errors.npy` (flat residuals), and `gating_weights.npy` (for GUMNet variants).
  - Multi-seed scanning, MASE calculation, and plotting functions can be reused from `compile_results.py`, `compile_fair_results.py`, and `plot_paper_figures.py`.
  - The existing Hansen MCS bootstrap in `model_confidence_set.py` has a centering bug (bootstrap p-values are always ~1.0). Correcting it requires subtracting the sample mean from resampled statistics before computing p-values.
  - Joint MCS bootstrap for 32 models is optimized from $O(B \cdot M^2 \cdot T)$ to $O(M^2 \cdot T + B \cdot M^2)$ by pre-generating index matrices and studentizing with original series HAC standard errors.
  - Cliff's Delta and Vargha-Delaney A can be computed simultaneously in $O(N \log N)$ time using Mann-Whitney U statistic ranks.
  - Orchestration design for `run_all_32models.py` recursively copies `results_v4/` to a timestamped backup, deletes model-specific directories for clean training, and sequentially runs the entire pipeline.
  - Visualization design for `generate_all_outputs.py` produces 8 plots with title running watermarks and 4 LaTeX tables, with full mock data support.
- **Unexplored areas**: None.

## Key Decisions Made
- Formulated the exact implementation designs and statistical validation formulas (DM, MCS, Cliff's Delta, Vargha-Delaney A) for all 5 pipeline scripts.
- Provided an $O(N \log N)$ Mann-Whitney U optimization for effect size calculation.
- Fixed the centering bug in Hansen MCS block bootstrap.

## Artifact Index
- /data/quyhv/oil_forecast_tail_risk/.agents/explorer_msB_1/ORIGINAL_REQUEST.md — Original request record.
- /data/quyhv/oil_forecast_tail_risk/.agents/explorer_msB_1/analysis.md — Main analysis report.
- /data/quyhv/oil_forecast_tail_risk/.agents/explorer_msB_1/handoff.md — Handoff report.
