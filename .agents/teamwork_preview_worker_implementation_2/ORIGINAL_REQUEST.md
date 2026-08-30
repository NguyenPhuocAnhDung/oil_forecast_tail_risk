## 2026-07-17T13:58:22Z
Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_worker_implementation_2/.
Your task is to implement Milestone 3 (Phase B: Stages 3, 4, 5, 6, and 7 of the Research OS) and output five separate Markdown files under `docs/research_os/`:
1. `docs/research_os/stage3_evidence_hierarchy.md`
2. `docs/research_os/stage4_integrity_audit.md`
3. `docs/research_os/stage5_hypothesis_design.md`
4. `docs/research_os/stage6_data_pipeline.md`
5. `docs/research_os/stage7_baseline_taxonomy.md`

Under no circumstances should you edit source code files or run tests yourself without running verification commands. All files should be written cleanly.

For each stage:
- **Stage 3 (Evidence Hierarchy)**: Categorize academic reference documents (from `Refs/` or general list) into Levels A, B, C based on their methodological rigor and relevance. Detail the exact experimental parameters and negative results (what failed) extracted from these references.
- **Stage 4 (Look-Ahead Bias Audit)**: Include `## SCIENTIFIC_INTEGRITY_AUDIT_REPORT`. Scan the repository's data preprocessing, scaling, and splitting logic. Identify any potential look-ahead bias risks (e.g. using global min/max instead of rolling train statistics, interpolating missing values using future information, leaking validation metrics). Propose strict containment protocols.
- **Stage 5 (Falsifiable Design)**: Include `## EXPERIMENTAL_ARCHITECTURE_BLUEPRINT`. Define four research questions ($RQ_1$ to $RQ_4$) and formulate corresponding null ($H_0$) and alternative ($H_1$) hypotheses. Provide rigorous LaTeX mathematical specifications for:
  1. The dynamic routing gate gating weights $g_j(x_t)$ and their dependency on geopolitical risk $GPR_t$.
  2. The dynamic routing temperature parameter $\tau_t$ (scaling it using GPR signals to make it sharper during crises and smoother during calm periods).
  3. The residual routing parameter $\lambda$ weighting the Wavelet-KAN vs other experts.
  4. The Mexican Hat Wavelet activation function parameter $\sigma$ scaling.
- **Stage 6 (Data Pipeline)**: Include `## DATA_PIPELINE_ARCHITECTURE`. Formulate the Walk-Forward validation procedure. Incorporate the six prediction horizons: `[1, 3, 5, 10, 20, 60]` days (make sure to include the newly added H20 horizon). Specify the mathematical details of MIDAS (mixed data sampling) spline interpolation used for high-frequency/daily GPR integration, and detail the historical percentile-based dynamic Noise Gate (e.g., using the 95th percentile of historical GPR as an activation threshold).
- **Stage 7 (Taxonomic Baseline)**: Include `## BENCHMARK_TAXONOMY_MATRIX`. Classify the 11 baseline models (iTransformer, TimesNet, TimeMixer, TFT, N-HiTS, PatchTST, DLinear, N-BEATS, FedFormer, Autoformer, and GUM-Net) into 4 distinct theoretical strategies. Contrast their architectural philosophies (e.g., transformer-based vs linear-based vs wavelet-based KAN). Crucially, integrate Requirement R8 (Chiến lược so sánh SOTA và Quy tắc chọn lọc) which defines the selection policy: compare GUM-Net with the strongest Time Series Foundation Models (TimesFM, Chronos, Moirai, etc.) on the dataset, and if any foundation model outperforms GUM-Net, adopt/supplement it as a baseline runner without removing old baselines.

MANDATORY INTEGRITY WARNING: DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

When completed, verify that the five files are successfully written to `docs/research_os/`, write your handoff report to `/data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_worker_implementation_2/handoff.md`, and send a message back to parent conversation ID 53d1d6fc-5e29-43fe-b494-a6aaa3afca7b.
