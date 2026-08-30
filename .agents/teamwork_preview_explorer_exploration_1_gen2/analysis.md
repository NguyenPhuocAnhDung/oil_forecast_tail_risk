# Detailed Repository Exploration Report

This report presents a thorough investigation of the data, documents, and scripts in the `oil_forecast_tail_risk` repository to support the implementation of the 17 stages of Research OS.

---

## 1. Dataset Investigation: `data/processed/unified_data.csv`

### 1.1 Structure and Dimensions
- **File Path**: `data/processed/unified_data.csv`
- **Total Rows (Samples)**: 4,471 rows (excluding header)
- **Total Columns**: 20 columns
- **Data Types**: 1 column is parsing as string/object (`Ngày` / Date), and the other 19 columns are float64.

### 1.2 Columns List
The dataset consists of the following 20 columns:
1. `Ngày` (Date)
2. `MG97` (Gasoline RON97)
3. `MG95` (Gasoline RON95)
4. `MG92` (Gasoline RON92 / E5)
5. `NAPHTHA` (Naphtha price)
6. `KERO` (Kerosene price)
7. `DO 0.001%` (Diesel DO 0.001%S-V)
8. `DO 0.05%` (Diesel DO 0.05%S)
9. `FO 180` (Fuel Oil FO 180)
10. `BRT_DTD` (Brent Dated Price)
11. `BRT_KH` (Brent KH Price)
12. `USD_Index` (US Dollar Index - DXY)
13. `GPR` (Geopolitical Risk Index)
14. `Brent_EU_Daily` (Daily Brent Spot Price)
15. `WTI_Daily` (Daily WTI Spot Price)
16. `Brent_Global_Monthly` (Monthly Brent Price)
17. `WTI_Monthly` (Monthly WTI Price)
18. `DayOfWeek` (Day of the week index: 0=Monday to 4=Friday)
19. `Day_sin` (Sine transform of Day of the Week)
20. `Day_cos` (Cosine transform of Day of the Week)

### 1.3 Date Range
- **Start Date**: `2008-11-03`
- **End Date**: `2026-02-27`
- **Note on Discrepancies**: The papers in the `docs/` folder refer to data extending up to **May 2026** (specifically 01/01/2008 to 31/05/2026 with 4,580 or 4,517 working days). The actual file `unified_data.csv` in the repository ends on **2026-02-27** and contains **4,471 rows**, representing a slight mismatch that must be noted.

### 1.4 First 5 Rows of Data
| Ngày | MG97 | MG95 | MG92 | NAPHTHA | KERO | DO 0.001% | DO 0.05% | FO 180 | BRT_DTD | BRT_KH | USD_Index | GPR | Brent_EU_Daily | WTI_Daily | Brent_Global_Monthly | WTI_Monthly | DayOfWeek | Day_sin | Day_cos |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2008-11-03** | 65.35 | 62.02 | 61.35 | 27.75 | 83.00 | 85.29 | 83.54 | 278.95 | 60.505 | 63.69 | 99.4345 | 68.710 | 60.32 | 63.93 | 52.7135 | 57.44 | 0.0 | 0.0000 | 1.0000 |
| **2008-11-04** | 59.25 | 55.92 | 55.25 | 23.10 | 81.97 | 82.55 | 80.80 | 248.83 | 63.770 | 67.04 | 97.9957 | 60.164 | 62.78 | 70.41 | 52.7135 | 57.44 | 1.0 | 0.9511 | 0.3090 |
| **2008-11-05** | 63.25 | 59.92 | 59.25 | 33.64 | 86.85 | 86.64 | 84.84 | 270.20 | 61.460 | 64.60 | 98.0953 | 88.994 | 61.09 | 65.41 | 52.7135 | 57.44 | 2.0 | 0.5878 | -0.8090 |
| **2008-11-06** | 58.85 | 56.04 | 55.60 | 30.38 | 81.60 | 81.22 | 79.22 | 255.79 | 56.010 | 59.20 | 99.5364 | 96.617 | 56.14 | 60.72 | 52.7135 | 57.44 | 3.0 | -0.5878 | -0.8090 |
| **2008-11-07** | 57.44 | 53.75 | 52.71 | 27.49 | 78.83 | 78.13 | 76.13 | 260.73 | 56.305 | 59.21 | 99.3944 | 99.346 | 56.84 | 61.06 | 52.7135 | 57.44 | 4.0 | -0.9511 | 0.3090 |

### 1.5 Summary Statistics
| Column | Mean | Std | Min | 25% | 50% | 75% | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **MG97** | 89.0869 | 25.1744 | 17.1500 | 72.1200 | 85.1100 | 108.8725 | 163.4400 |
| **MG95** | 87.3110 | 25.0510 | 16.1200 | 70.2050 | 83.4400 | 107.5450 | 160.8600 |
| **MG92** | 84.4755 | 24.6515 | 14.6400 | 67.4500 | 80.9500 | 103.4900 | 155.7200 |
| **NAPHTHA** | 70.9895 | 21.5266 | 13.6000 | 55.5850 | 69.3000 | 85.5550 | 129.0800 |
| **KERO** | 89.5344 | 27.3621 | 13.0600 | 70.4850 | 86.4900 | 115.2400 | 174.0100 |
| **DO 0.001%** | 91.5770 | 28.0173 | 22.9200 | 71.7550 | 87.4200 | 117.5800 | 186.0300 |
| **DO 0.05%** | 90.1147 | 27.5522 | 20.7500 | 70.4100 | 86.4900 | 115.9650 | 177.1700 |
| **FO 180** | 439.6632 | 140.6121 | 105.8900 | 336.4550 | 433.9200 | 520.9350 | 755.9200 |
| **BRT_DTD** | 76.3618 | 23.9089 | 13.2400 | 59.3400 | 73.9950 | 95.0400 | 137.6400 |
| **BRT_KH** | 76.5182 | 23.1579 | 19.1500 | 59.9350 | 74.1200 | 94.4500 | 131.5300 |
| **USD_Index** | 108.1444 | 12.0490 | 85.4692 | 94.2186 | 112.0822 | 117.7550 | 130.0413 |
| **GPR** | 112.6329 | 50.1330 | 9.4916 | 79.2243 | 103.3935 | 136.3009 | 540.8274 |
| **Brent_EU_Daily**| 76.3022 | 23.8819 | 9.1200 | 59.3300 | 74.1300 | 95.0550 | 133.1800 |
| **WTI_Daily** | 70.7989 | 20.5736 | -36.9800 | 53.8650 | 70.6900 | 86.5200 | 123.6400 |
| **Brent_Global_Monthly**| 76.4753 | 23.2887 | 26.8486 | 59.6313 | 74.6783 | 93.9928 | 124.7032 |
| **WTI_Monthly** | 70.8163 | 20.4078 | 16.5500 | 54.6600 | 70.9800 | 86.3300 | 114.8400 |
| **DayOfWeek** | 1.9960 | 1.4104 | 0.0000 | 1.0000 | 2.0000 | 3.0000 | 4.0000 |
| **Day_sin** | 0.0036 | 0.7068 | -0.9511 | -0.5878 | 0.0000 | 0.5878 | 0.9511 |
| **Day_cos** | -0.0029 | 0.7076 | -0.8090 | -0.8090 | 0.3090 | 0.3090 | 1.0000 |

---

## 2. Review of Existing Paper Draft Documents in `docs/`

There are 7 primary documents drafting the GUM-Net paper:

1. **`docs/Evaluation_Scenarios_Draft.md`**
   - **Content**: Outlines the robust forecasting evaluation framework focused on Directional Accuracy (DA) over 6 horizons (H1, H3, H5, H10, H20, H60) under 5 extreme tail-risk windows (2014 OPEC price collapse, 2020 COVID shock, 2022 Russia-Ukraine war, 2024 Red Sea shipping crisis, and a 2026 hypothetical US-Iran escalation). It lists tables showing GUM-Net outperforming 10 SOTA models and baselines in these windows. It also covers the 4 components of GUM-Net's adaptive routing (Softmax Temperature tuning, Mexican Hat $\sigma$-scaling, Directional Penalty sign loss, GPR Noise Gate) and has an Ablation Study.
   - **Status**: Structured draft. Fully revised based on review comments (notations standardized, ablation footnotes added, Diebold-Mariano significance stated).

2. **`docs/Methodology_Tail_Risk.md`**
   - **Content**: Details the mathematical formulation of GUM-Net's gating mechanism, Wavelet-KAN Mexican Hat activation functions, GPR-conditioned temperature routing, and the Joint Quantile/Sign Loss function. Defines the statistical characteristics of the 5 tail-risk windows. Includes a design comparison table comparing GUM-Net vs the 10 SOTA models on 9 key capabilities (e.g. Decoupled modeling, GPR integration, UQ).
   - **Status**: Mathematical draft. Highly structured and complete.

3. **`docs/Part_1_Intro.md`**
   - **Content**: Abstract and Introduction sections. Establishes the macro-importance of retail petroleum forecasting and the structural limits of SOTA models under tail risk. Introduces GUM-Net's design philosophy (MoE, KAN, Decoupled Modeling). Outlines 4 major scientific contributions.
   - **Status**: High-quality draft of Section 1.

4. **`docs/Part_2_RelatedWork.md`**
   - **Content**: Section 2: Related Work. Reviews literature on downstream retail petroleum markets, Mixture of Experts (MoE), and Kolmogorov-Arnold Networks (KAN). Analyzes the structural limitations of 10 SOTA models (e.g., FFT mismatch in TimesNet, low-pass smoothing in N-HiTS, path-dependence in PatchTST, lack of GPR integration in N-BEATS). Outlines 4 major research gaps.
   - **Status**: Complete related work draft.

5. **`docs/Part_3_Methodology.md`**
   - **Content**: Section 3: Methodology. Discusses problem formulation, Stationarity-Aware Decoupled Modeling (xăng vs diesel), the use of Cumulative Log-Return target to prevent error accumulation, and GUM-Net's experts (Dilated CNN, GRU-Attention, Wavelet-KAN) and routing gate.
   - **Status**: Structured methodological draft.

6. **`docs/Part_4_Experiments.md`**
   - **Content**: Section 4: Experimental Setup & Results. Details the dataset, baseline taxonomy, training configuration, and multi-horizon performance analysis (H1, H3, H5, H10, H60). Includes a crucial "Normal-Period Failure Analysis" explaining why GUM-Net is occasionally outperformed by simpler baselines (like DLinear or LSTM) in quiet periods due to routing overfitting and GPR noise contamination. Contains overall benchmark tables.
   - **Status**: Highly complete results draft.

7. **`docs/Part_5_Conclusion_Refs.md`**
   - **Content**: Section 5: Conclusion and References. Summarizes research findings and provides policy implications for regulators (Quỹ BOG management) and distributors (hedging). Lists 30 academic references.
   - **Status**: Complete final section draft.

---

## 3. Inventory of Useful Scripts in `scripts/`

The `scripts/` directory contains tools for training, evaluating, auditing, and checking the GUM-Net paper. The most relevant scripts for implementing the 17 stages of Research OS include:

### 3.1 Stationarity & Breakpoint Identification (ADF/KPSS, Breakpoints, Regimes)
- **`scripts/run_advanced_stats.py`**: Computes standard Augmented Dickey-Fuller (ADF) and KPSS unit root tests on data. Econometrically configures the tests for return series (using `regression='c'`) to justify the Decoupled Modeling strategy.
- **`scripts/q1_audit.py`**: Audits stationarity configurations, checks look-ahead bias, and validates dataset integrity.
- **`scripts/regime_analysis.py`**: Classifies WTI volatility regimes into low, medium, and high-volatility zones using rolling standard deviations. Connects high volatility to historical crises (2008, 2020, 2022) to justify the MoE gating architecture.

### 3.2 Predictive Accuracy & superior Set Tests (DM test, MCS)
- **`scripts/dm_test_da.py`**: Runs the Diebold-Mariano test specifically adapted for Directional Accuracy (DA) error differentials between GUM-Net and DLinear at H60, using Newey-West HAC adjustments.
- **`scripts/model_confidence_set.py`**: Implements the Model Confidence Set (MCS) algorithm (Hansen et al., 2011) using block bootstrap to identify the statistically superior set of models at a given confidence level ($\alpha = 0.10$).
- **`scripts/run_advanced_stats.py`** (referenced above): Also implements standard Diebold-Mariano tests with the Harvey-Leybourne-Newbold (HLN) small-sample correction and the Holm-Bonferroni multiple testing correction.

### 3.3 Explainable AI (XAI) and Diagnostics
- **`scripts/plot_gating.py`**: Visualizes routing gate attributions. Generates stacked bar plots of gating weights across horizons and line plots showing the dynamic shift of experts (e.g. CNN to GRU/KAN) along prediction steps.
- **`scripts/overfitting_diagnostic.py`**: Plots R² degradation curves by horizon and visualizes seed variance (stability check) for reproducibility analysis.

### 3.4 Verification and Pipeline Automation
- **`scripts/verify_math.py`**: Verifies LaTeX mathematical syntax and checks consistency between experimental logs and paper draft formulas.
- **`scripts/verify_csv_against_docx.py`** & **`verify_seed42_against_docx.py`**: Cross-validates experimental outputs stored in results CSVs against docx paper drafts to prevent discrepancies.
- **`scripts/pipeline/`**: Subfolder containing 12 structured scripts executing Research OS stages (e.g. `01_dataset_freeze.py`, `04_ranking.py`, `06_statistics.py`, `10_report_builder.py`).
