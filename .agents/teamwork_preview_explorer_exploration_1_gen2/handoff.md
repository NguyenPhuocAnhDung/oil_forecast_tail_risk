# Soft Handoff Report: Repository Exploration for GUM-Net

This handoff summarizes the findings of the repository exploration to prepare for implementing the 17 stages of Research OS.

---

## 1. Observation

- **Dataset**: `data/processed/unified_data.csv` contains 4,471 rows (excluding header) and 20 columns.
  - Verbatim header:
    ```
    Ngày,MG97,MG95,MG92,NAPHTHA,KERO,DO 0.001%,DO 0.05%,FO 180,BRT_DTD,BRT_KH,USD_Index,GPR,Brent_EU_Daily,WTI_Daily,Brent_Global_Monthly,WTI_Monthly,DayOfWeek,Day_sin,Day_cos
    ```
  - Verbatim first row (line 2):
    ```
    2008-11-03,65.35,62.02,61.35,27.75,83.0,85.29,83.54,278.95,60.505,63.69,99.4345,68.71046447753906,60.32,63.93,52.7135,57.44,0.0,0.0,1.0
    ```
  - Verbatim last row (line 4472):
    ```
    2026-02-27,82.85,82.09,79.63,68.89,93.57,92.88,92.26,430.7,70.94,72.39,117.8223,197.1114654541016,71.32,66.96,69.4095,64.51,4.0,-0.9510565162951536,0.3090169943749472
    ```
- **Discrepancies**:
  - `docs/Evaluation_Scenarios_Draft.md` (line 33) states:
    ```
    Việc đánh giá được thực hiện trên tập dữ liệu mở rộng kéo dài từ ngày 01/01/2008 đến 31/05/2026 (tổng cộng 4.580 ngày làm việc).
    ```
  - `docs/Part_1_Intro.md` (line 20) states:
    ```
    đối với tập dữ liệu thực tế khổng lồ gồm 4.517 ngày làm việc kéo dài đến tháng 5/2026
    ```
  - The actual data spans `2008-11-03` to `2026-02-27` with `4,471` rows.
- **Documents in `docs/`**: Found 7 files:
  1. `Evaluation_Scenarios_Draft.md` (evaluation framework, tail-risk windows, ablation study, model comparisons)
  2. `Methodology_Tail_Risk.md` (gating mechanism math, 5 tail risk windows, SOTA comparison table)
  3. `Part_1_Intro.md` (abstract & section 1)
  4. `Part_2_RelatedWork.md` (section 2 related work, SOTA limitations, 4 research gaps)
  5. `Part_3_Methodology.md` (section 3 methodology, decoupled modeling, target return, GUM-Net experts)
  6. `Part_4_Experiments.md` (section 4 experiments setup, H1-H60 results, normal-period failure analysis, May 2026 data extension, xăng & dầu tables)
  7. `Part_5_Conclusion_Refs.md` (conclusion, policy implications, 30 references)
- **Scripts in `scripts/`**: Found 64 files. Key scripts:
  - `scripts/run_advanced_stats.py` (ADF & KPSS tests, standard DM test with HAC/HLN/Holm-Bonferroni correction)
  - `scripts/model_confidence_set.py` (Model Confidence Set test using Hansen et al. (2011) block bootstrap)
  - `scripts/dm_test_da.py` (Diebold-Mariano test specifically for Directional Accuracy (DA))
  - `scripts/plot_gating.py` (Visualizes routing gate attributions)
  - `scripts/regime_analysis.py` (WTI volatility regime-conditional analysis)
  - `scripts/overfitting_diagnostic.py` (R² degradation and seed variance stability checking)
  - `scripts/q1_audit.py` (Audits stationarity configuration and look-ahead bias)
  - `scripts/pipeline/` (12 automation scripts for Research OS steps)

---

## 2. Logic Chain

1. **Check actual dataset parameters**: Running a Python pandas script on `data/processed/unified_data.csv` confirmed that the dataset contains exactly 4,471 rows and 20 columns, with a date range of `2008-11-03` to `2026-02-27`.
2. **Scan paper drafts**: Reading the documents in `docs/` revealed that they describe GUM-Net's structure and performance, but contain internal inconsistencies regarding data volume (4,580 vs 4,517 days) and target dates (May 2026 vs Feb 2026).
3. **Identify script capabilities**: Ripgrep and line inspection showed that the `scripts/` directory is well-equipped with diagnostic and statistical validation tools (ADF/KPSS, DM test, MCS, XAI routing weight visualizations, and regime volatility classifiers).
4. **Conclusion formulation**: These inputs are sufficient to map out and implement the 17 stages of Research OS. The identified date range mismatch is a key data quality finding that needs resolution during Stage 0 and Stage 4.

---

## 3. Caveats

- We assumed that `data/processed/unified_data.csv` is the primary and only dataset of interest, and did not examine raw data sources.
- No model training or evaluation was executed. All analysis of GUM-Net's performance was based on the text within the paper drafts and the pre-computed results in the results folder.

---

## 4. Conclusion

The repository contains a complete set of draft documents, statistical scripts, and a processed unified dataset. However, there are discrepancies between the dates/row counts described in the drafts (May 2026, 4,580/4,517 rows) and the actual data file (2026-02-27, 4,471 rows). The available scripts cover all required econometric checks (ADF/KPSS, DM test, MCS) and explainability plots (gating weights, R² degradation, regimes) needed to complete the Research OS pipeline.

---

## 5. Verification Method

- To verify the dataset size and date range, run:
  ```powershell
  python -c "import pandas as pd; df = pd.read_csv('data/processed/unified_data.csv'); print(len(df), df.iloc[0, 0], df.iloc[-1, 0])"
  ```
- To verify the existence of the detailed report:
  - Inspect `/data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_explorer_exploration_1_gen2/analysis.md`.

---

## 6. Remaining Work

1. Implement Stage 0 (Dataset Governance) and update the Dataset Card using the exact actual dimensions (4,471 rows, `2008-11-03` to `2026-02-27`).
2. Resolve date range discrepancies in `docs/Part_1_Intro.md`, `docs/Evaluation_Scenarios_Draft.md`, and `docs/Part_4_Experiments.md` to match the actual dataset.
3. Set up and execute the Research OS stage scripts (Stage 0 to Stage 16) inside `docs/research_os/` using the scripts in `scripts/pipeline/` and general statistical utilities.
