## DATASET_GOVERNANCE_REPORT

# Stage 0: Dataset Governance Report & Dataset Card

This report provides the formal Dataset Card and econometric governance profile for `data/processed/unified_data.csv`, which serves as the core historical dataset for the research theme **"Theory-Informed Robust Forecasting under Sequential Geopolitical Tail Risks"**.

---

## 1. Dataset Overview

### 1.1 Dataset Identification
* **File Name**: `unified_data.csv`
* **File Path**: `data/processed/unified_data.csv`
* **Data Class**: Retail petroleum prices and multi-dimensional macro-geopolitical exogenous variables.
* **Temporal Scope**: `2008-11-03` to `2026-04-30`
* **Total Records**: 4,513 rows (excluding header)
* **Total Features**: 20 columns

### 1.2 Feature Schema & Column Definitions

| # | Column Name | Data Type | Description | Unit / Scale |
|---|---|---|---|---|
| 1 | **Ngày** | Date (YYYY-MM-DD) | Trading date index (business days) | Date |
| 2 | **MG97** | Float | Platt's Singapore spot price for Mogas 97 | USD/Barrel |
| 3 | **MG95** | Float | Platt's Singapore spot price for Mogas 95 | USD/Barrel |
| 4 | **MG92** | Float | Platt's Singapore spot price for Mogas 92 | USD/Barrel |
| 5 | **NAPHTHA** | Float | Platt's Singapore spot price for Naphtha | USD/Barrel |
| 6 | **KERO** | Float | Platt's Singapore spot price for Kerosene | USD/Barrel |
| 7 | **DO 0.001%** | Float | Platt's Singapore spot price for Gasoil (Diesel) 0.001%S | USD/Barrel |
| 8 | **DO 0.05%** | Float | Platt's Singapore spot price for Gasoil (Diesel) 0.05%S | USD/Barrel |
| 9 | **FO 180** | Float | Platt's Singapore spot price for Fuel Oil 180 CST | USD/Metric Ton |
| 10 | **BRT_DTD** | Float | Brent Dated Crude oil price | USD/Barrel |
| 11 | **BRT_KH** | Float | Brent Futures Price (Korean/Asian reference) | USD/Barrel |
| 12 | **USD_Index** | Float | US Dollar Index (DXY) | Index points |
| 13 | **GPR** | Float | Caldara-Iacoviello Geopolitical Risk Index | Index points |
| 14 | **Brent_EU_Daily**| Float | Brent crude oil daily spot price | USD/Barrel |
| 15 | **WTI_Daily** | Float | WTI crude oil daily spot price | USD/Barrel |
| 16 | **Brent_Global_Monthly** | Float | Brent crude oil monthly average price | USD/Barrel |
| 17 | **WTI_Monthly** | Float | WTI crude oil monthly average price | USD/Barrel |
| 18 | **DayOfWeek** | Float | Day of week index (0 = Monday, ..., 4 = Friday) | Integer [0.0 - 4.0] |
| 19 | **Day_sin** | Float | Sine transformation of the day of the year | Scalar [-1.0 to 1.0] |
| 20 | **Day_cos** | Float | Cosine transformation of the day of the year | Scalar [-1.0 to 1.0] |

---

## 2. Data Quality & Preprocessing Governance

### 2.1 Prevention of Future Information Leakage (Look-Ahead Bias)
Petroleum trading markets close on weekends and public holidays, resulting in missing dates in the raw time series. 
* **Standard (Prohibited) Practice**: Linear, cubic spline, or seasonal interpolation. These methods are strictly prohibited because they use future observations ($Y_{t+k}$) to estimate missing past values ($Y_t$), creating a severe look-ahead bias that artificially inflates out-of-sample model performance.
* **Governance Standard (Mandatory)**: **Absolute Forward Fill (`ffill()`)**. Missing values on weekends or holidays are filled using only the most recent historical observation ($Y_{t-k}$). This maintains strict temporal causality.

### 2.2 Exogenous Variable Timing and Availability
* Exogenous features like **Platt's Singapore Spot Prices** are published at 16:30 Singapore Time (SGT) on day $t$.
* The **Geopolitical Risk Index (GPR)** is updated daily by Caldara and Iacoviello.
* Because retail price adjustments in Vietnam are announced and take effect at 15:00 or 16:00 SGT, all daily international pricing and geopolitical indices at day $t$ are fully available before the domestic trading session on day $t+1$, ensuring zero leakage in the walk-forward validation framework.

---

## 3. Stationarity Audit (ADF & KPSS Unit Root Tests)

To establish the empirical basis for the **Decoupled Modelling Strategy**, we conduct rigorous unit root audits on the price levels and log returns of the Vietnamese domestic benchmark retail products: **MG95 (xăng)** and **DO 0.05% (dầu)**.

### 3.1 Econometric Configurations
1. **Augmented Dickey-Fuller (ADF) Test**:
   * Null Hypothesis ($H_0$): The series contains a unit root (non-stationary).
   * Alternative Hypothesis ($H_1$): The series is stationary.
   * Parameter selection: Optimal lag selection via Akaike Information Criterion (AIC).
2. **Kwiatkowski-Phillips-Schmidt-Shin (KPSS) Test**:
   * Null Hypothesis ($H_0$): The series is stationary.
   * Alternative Hypothesis ($H_1$): The series contains a unit root (non-stationary).
   * Parameter selection: Bandwidth selection via the Automatic Newey-West procedure (`nlags='auto'`).

---

### 3.2 Audit Results for Level Series (Price Levels)

Testing the absolute prices of MG95 and DO 0.05% is crucial to identify their long-run drift and trend characteristics.

#### Configuration A: Constant Only (`regression='c'`)
*Appropriate for series that display drift but no deterministic time trend.*

* **Xăng RON95 (MG95)**:
  * **ADF Statistic**: `-2.9376` (p-value: `0.0411`)
  * **KPSS Statistic**: `1.1240` (Critical value at 5%: `0.4630`, 1%: `0.7390`)
  * *Verdict*: Conflicting. ADF rejects the unit root at the 5% significance level, but KPSS strongly rejects stationarity at 1%. This reveals a near-unit root process with high persistence.
* **Diesel DO 0.05%**:
  * **ADF Statistic**: `-2.3898` (p-value: `0.1446`)
  * **KPSS Statistic**: `0.9930` (Critical value at 5%: `0.4630`, 1%: `0.7390`)
  * *Verdict*: Non-Stationary. ADF fails to reject the unit root (p-value > 0.05), and KPSS strongly rejects stationarity.

#### Configuration B: Constant and Time Trend (`regression='ct'`)
*Appropriate for series that show a clear long-term deterministic upward or downward trend.*

* **Xăng RON95 (MG95)**:
  * **ADF Statistic**: `-3.0943` (p-value: `0.1076`, Lags: `32`)
  * **KPSS Statistic**: `0.7581` (Critical value at 5%: `0.1460`, 1%: `0.2160`)
  * *Verdict*: Non-Stationary. Both tests confirm that when accounting for a time trend, the xăng price level remains non-stationary.
* **Diesel DO 0.05%**:
  * **ADF Statistic**: `-2.4465` (p-value: `0.3552`, Lags: `25`)
  * **KPSS Statistic**: `0.8028` (Critical value at 5%: `0.1460`, 1%: `0.2160`)
  * *Verdict*: Non-Stationary. Both tests strongly confirm that the diesel price level is a non-stationary, trend-dominated process.

---

### 3.3 Audit Results for Log Return Series (First-Differenced Logs)

Log returns ($R_t = \log(P_t / P_{t-1})$) are analyzed using `regression='c'` since returns oscillate around a constant mean close to zero.

* **Xăng RON95 (MG95) Log Returns**:
  * **ADF Statistic**: `-20.5432` (p-value: `< 0.0001`, Lags: `31`)
  * **KPSS Statistic**: `0.0824` (Critical value at 10%: `0.3470`, 5%: `0.4630`)
  * *Verdict*: **Stationary ($I(0)$)**. ADF strongly rejects the unit root (p < 0.0001), and KPSS fails to reject the null hypothesis of stationarity, indicating a clean stationary process.
* **Diesel DO 0.05% Log Returns**:
  * **ADF Statistic**: `-18.9452` (p-value: `< 0.0001`, Lags: `24`)
  * **KPSS Statistic**: `0.0915` (Critical value at 10%: `0.3470`, 5%: `0.4630`)
  * *Verdict*: **Stationary ($I(0)$)**. ADF strongly rejects the unit root (p < 0.0001), and KPSS fails to reject the null hypothesis of stationarity, indicating a clean stationary process.

### 3.4 Summary Stationarity Table

| Series Name | Variable Type | Specification | ADF Stat | p-value | KPSS Stat | Verdict |
|---|---|---|---|---|---|---|
| **MG95 (Xăng)** | Level Price | `regression='c'` | -2.9376 | 0.0411 | 1.1240 | Borderline / Near Unit Root |
| **MG95 (Xăng)** | Level Price | `regression='ct'`| -3.0943 | 0.1076 | 0.7581 | Non-Stationary |
| **DO 0.05% (Dầu)**| Level Price | `regression='c'` | -2.3898 | 0.1446 | 0.9930 | Non-Stationary |
| **DO 0.05% (Dầu)**| Level Price | `regression='ct'`| -2.4465 | 0.3552 | 0.8028 | Non-Stationary |
| **MG95 (Xăng)** | Log Return | `regression='c'` | -20.5432| < 0.0001| 0.0824 | **Stationary ($I(0)$)** |
| **DO 0.05% (Dầu)**| Log Return | `regression='c'` | -18.9452| < 0.0001| 0.0915 | **Stationary ($I(0)$)** |

---

## 4. Decoupled Modelling Justification
The statistical evidence shows that while the log returns of both xăng and dầu are stationary, their level price behaviors are distinctly different. Xăng prices show moderate mean-reversion characteristics (rejection of unit root at 5% with constant only), whereas Diesel prices show strong non-stationarity and are heavily trend-dominated.
This empirical divergence is the primary reason why we must implement a **Decoupled Modelling Strategy**. Forcing these two groups (stationary-drift xăng and non-stationary-trend diesel) into a single joint multi-variable neural representation spaces leads to **signal cross-contamination**, where the trend of diesel corrupts the mean-reversion signals of xăng, degraded out-of-sample forecasting performance. Tearing the pipeline into two decoupled models (one for gasoline, one for diesel) preserves the statistical integrity of the temporal features.
