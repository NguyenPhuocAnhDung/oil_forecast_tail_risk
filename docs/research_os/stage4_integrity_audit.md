## SCIENTIFIC_INTEGRITY_AUDIT_REPORT

# Stage 4: Look-Ahead Bias & Scientific Integrity Audit

This report presents a comprehensive look-ahead bias and scientific integrity audit of the repository's data preprocessing, feature engineering, scaling, splitting, and validation pipelines. It details potential data leakage risks, evaluates current safeguards, and establishes formal containment protocols to guarantee the econometric validity of the research findings.

---

## 1. Look-Ahead Bias Risk Assessment Matrix

We scan the repository's data processing pipeline and identify five major look-ahead bias and data leakage risks.

```
                    +--------------------------------------------+
                    |        RAW DATA INGESTION (Daily)          |
                    +--------------------------------------------+
                                          |
                                          v  [Imputation Audit]
                    +--------------------------------------------+
                    |      CAUSAL IMPUTATION: Forward Fill       |  <-- Prohibit Interpolation
                    +--------------------------------------------+
                                          |
                                          v  [Temporal Splitting]
                    +--------------------------------------------+
                    |        WALK-FORWARD EXPANDING SPLIT        |
                    +--------------------------------------------+
                     /                    |                    \
                    /                     |                     \
                   v                      v                      v
        +--------------+           +--------------+       +--------------+
        |  df_train    |           |    df_val    |       |   df_test    |
        +--------------+           +--------------+       +--------------+
               |                          |                      |
               v [Fit & Transform]        v [Transform Only]     v [Transform Only]
        +--------------+           +--------------+       +--------------+
        | Scaled Train |           |  Scaled Val  |       | Scaled Test  |
        +--------------+           +--------------+       +--------------+
```

| Risk ID | Source of Potential Leakage | Technical Mechanism | Status / Repository Safeguard |
|---|---|---|---|
| **RISK 1** | **Global Feature Scaling** | Computing MinMax or Standard Deviation statistics ($\mu, \sigma$) over the entire dataset before temporal splitting, leading to out-of-sample distribution leakage. | **SAFE**: Checked `src/data/dataset.py` & `scripts/train_unified.py`. A fresh `DataProcessor` is initialized inside each walk-forward iteration, calling `fit_transform` *only* on the training slice `df_train` and `transform` on `df_val` and `df_test`. |
| **RISK 2** | **Future Information in Imputation** | Using linear, cubic spline, or seasonal interpolation to fill missing prices/features on weekends or holidays, which uses future values $Y_{t+k}$ to estimate $Y_t$. | **SAFE**: Verified `src/data/dataset.py`. The pipeline enforces an absolute Forward Fill (`ffill()`) rule. Weekend or holiday gaps are filled using only the most recent historical price $Y_{t-1}$. |
| **RISK 3** | **Global Signal Decomposition** | Applying signal decomposition algorithms (e.g., EEMD, CEEMDAN, VMD) globally to the entire dataset before splitting, which leaks future trends through global spline envelopes. | **SAFE / PROHIBITED**: The repository completely avoids pre-computed global decompositions. The Wavelet-KAN expert processes raw/stationary series directly and applies wavelets locally. |
| **RISK 4** | **Autoregressive / Validation Leakage** | Tuning hyperparameters (such as GPR threshold $\theta$ or gating temperature parameters) on the test set or using test performance for early stopping. | **SAFE**: Early stopping and model selection are conducted strictly on the validation slice `df_val`. The test slice `df_test` is kept completely holdout and used only for final evaluation. |
| **RISK 5** | **Exogenous Feature Lag Mismatch** | Using contemporaneous daily variables $X_t$ that are not yet published at the time of the domestic price adjustment decision, causing temporal leakage. | **SAFE**: Audited in `stage0_dataset_governance.md`. Platt's Singapore prices and GPR indices for day $t$ are published and fully available before the domestic price adjustment on day $t+1$. |

---

## 2. In-Depth Audit of Preprocessing Logic

### 2.1 Feature Scaling Isolation
In `src/data/dataset.py`, the `DataProcessor` class prepares data using the following logic:
```python
if is_train and fit_scaler:
    features_scaled = self.feature_scaler.fit_transform(features_data)
else:
    features_scaled = self.feature_scaler.transform(features_data)
```
This is called in `scripts/train_unified.py` inside the Walk-Forward loop:
```python
# Iteration loop
processor = DataProcessor(seq_len=cfg['seq_len'], horizon=horizon)
X_train, y_train = processor.prepare_data(df_train, ..., is_train=True, fit_scaler=True)
X_val, y_val = processor.prepare_data(df_val, ..., is_train=False, fit_scaler=False)
X_test, _ = processor.prepare_data(df_test, ..., is_train=False, fit_scaler=False)
```
* **Audit Verdict**: **PASS**. There is zero leakage of test set features into the scaling parameters because the scaler is fit strictly on `df_train` during each window. Since the training window expands, the scaler is re-fit from scratch on the updated historical data, preserving the information boundary.

### 2.2 Volatility Feature Stationarity (Audit 2 of `q1_audit.py`)
Historically, rolling volatility features of WTI or Brent were calculated directly on the absolute price levels:
$$\sigma_{t} = \text{std}(P_{t-k:t})$$
Because price levels are non-stationary ($I(1)$), rolling standard deviations calculated on them remain non-stationary and trend-dominated. This introduces spurious regression risks.
* **Audit Verdict**: **PASS**. The audited codebase calculates rolling volatility on the log returns of WTI/Brent:
$$\sigma_{t} = \text{std}(\log(P_{t-k:t} / P_{t-k-1:t-1}))$$
This yields an $I(0)$ stationary volatility feature, verified by ADF tests ($p < 0.05$), eliminating spurious relationship bias.

### 2.3 Directional Accuracy (DA) Product Contamination
When evaluating multiple products (e.g., MG95, MG92, DO 0.05%, DO 0.001%), calculating Directional Accuracy requires comparing the sign of actual changes with predicted changes:
$$\text{DA} = \mathbb{E}[\mathbb{I}(\text{sgn}(\Delta Y_t) == \text{sgn}(\Delta \hat{Y}_t))]$$
* **The Risk**: A common bug is to flatten the 2D arrays of true prices $[N \times M]$ and predicted prices $[N \times M]$ into 1D vectors before applying `np.diff()`. This computes a "difference" between the first observation of product $B$ and the last observation of product $A$, causing cross-product boundary contamination.
* **Audit Verdict**: **PASS**. The codebase applies the diff operator along the temporal axis (`axis=0`) before calculating matches:
```python
diff_true = np.sign(np.diff(y_true, axis=0))
diff_pred = np.sign(np.diff(y_pred, axis=0))
da = np.mean(diff_true == diff_pred) * 100
```
This guarantees that directional predictions are verified purely on temporal trends per product.

---

## 3. Strict Containment Protocols

To maintain scientific integrity across all future developments, the following containment protocols are strictly enforced:

### Protocol 1: Causal Imputation Restriction
* **Rule**: Under no circumstances should `pandas.DataFrame.interpolate()` (linear, spline, cubic) or `pandas.DataFrame.bfill()` be applied to price or exogenous variables.
* **Enforcement**: Only absolute Forward Fill (`ffill()`) and zero-filling for missing returns are allowed:
  ```python
  df = df.ffill().fillna(0)
  ```

### Protocol 2: Window-Level Local Scalers
* **Rule**: Feature scaling parameters must never be saved globally across walk-forward steps.
* **Enforcement**: Scaler objects must be instantiated inside the local iteration block of the walk-forward validation and fitted only on the active training subset `df_train`.

### Protocol 3: Chronological Split Isolation for Quantile Intervals
* **Rule**: Quantile predictions (e.g., Q10, Q50, Q90) and BOG threshold configurations must be tuned strictly using the validation set `df_val` or historical training distributions.
* **Enforcement**: Test slice performance must never back-propagate or influence any hyperparameter adjustments.

### Protocol 4: Out-of-Sample Truncation Bounding
* **Rule**: To prevent leakage from future data extensions, the test set must have an immutable chronological end date.
* **Enforcement**: For `unified_data.csv`, the dataset boundary is strictly capped at `2026-04-30` (or `2026-05-07` for the extended dataset), and no future data points may be used.
