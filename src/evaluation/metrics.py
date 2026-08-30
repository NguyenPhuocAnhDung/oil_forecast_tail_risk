"""
src/evaluation/metrics.py — Evaluation Metrics
=================================================
Comprehensive metrics for time series forecasting evaluation.

Metrics (point forecast):
  MAE    — Mean Absolute Error
  RMSE   — Root Mean Squared Error
  MAPE   — Mean Absolute Percentage Error  (%)
  sMAPE  — Symmetric MAPE, robust near zero  (%)
  MASE   — Mean Absolute Scaled Error (vs naive random walk)
  WAPE   — Weighted APE = sum|e| / sum|y_true|  (%)
  MdAE   — Median Absolute Error
  MdAPE  — Median Absolute Percentage Error  (%)
  MaxAE  — Maximum Absolute Error
  Bias   — Mean Error (signed; positive = overpredicts)
  R2     — Coefficient of Determination
  DA     — Directional Accuracy  (%)
  TheilU — Theil's U2 (< 1 better than naive, 1 = same, > 1 worse)

Quantile metrics (added externally in train_unified.py):
  PICP   — Prediction Interval Coverage Probability at 90%
  PINAW  — Prediction Interval Normalized Average Width
"""

import numpy as np
from sklearn.metrics import r2_score


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    naive_mae: float = None,
) -> dict:
    """
    Tính toán đầy đủ metrics đánh giá dự báo.

    Args:
        y_true    : Giá trị thực (absolute prices), 1D hoặc 2D [N, output_dim]
        y_pred    : Giá trị dự báo (absolute prices), same shape
        naive_mae : MAE của naive forecast (random walk) — dùng cho MASE.
                    Nếu None → tự tính shift-1 naive từ y_true.

    Returns:
        dict: 14 metrics (all float)
    """
    epsilon = 1e-8
    y_true = np.array(y_true, dtype=np.float64)
    y_pred = np.array(y_pred, dtype=np.float64)

    # ── Directional Accuracy & flatten ─────────────────────────
    if y_true.ndim >= 2:
        if y_true.shape[0] > 1:
            true_dir = np.sign(np.diff(y_true, axis=0))
            pred_dir = np.sign(np.diff(y_pred, axis=0))
            da = float(np.mean(true_dir == pred_dir) * 100)
        else:
            da = 0.0
        y_t = y_true.flatten()
        y_p = y_pred.flatten()
    else:
        if len(y_true) > 1:
            true_dir = np.sign(np.diff(y_true))
            pred_dir = np.sign(np.diff(y_pred))
            da = float(np.mean(true_dir == pred_dir) * 100)
        else:
            da = 0.0
        y_t = y_true
        y_p = y_pred

    errors   = y_t - y_p
    abs_err  = np.abs(errors)
    abs_true = np.abs(y_t) + epsilon

    # ── Primary metrics ─────────────────────────────────────────
    mae   = float(np.mean(abs_err))
    mse   = float(np.mean(errors ** 2))
    rmse  = float(np.sqrt(mse))
    mape  = float(np.mean(abs_err / abs_true) * 100)
    smape = float(np.mean(2 * abs_err / (abs_true + np.abs(y_p) + epsilon)) * 100)
    wape  = float(np.sum(abs_err) / (np.sum(abs_true) + epsilon) * 100)
    mdae  = float(np.median(abs_err))
    mdape = float(np.median(abs_err / abs_true) * 100)
    maxae = float(np.max(abs_err))
    bias  = float(np.mean(errors))          # positive → overpredicts

    try:
        r2 = float(r2_score(y_t, y_p))
    except ValueError:
        r2 = 0.0

    # ── MASE ────────────────────────────────────────────────────
    if naive_mae is not None and naive_mae > epsilon:
        mase = float(mae / naive_mae)
    else:
        if len(y_t) > 1:
            naive_denom = float(np.mean(np.abs(np.diff(y_t)))) + epsilon
        else:
            naive_denom = epsilon
        mase = float(mae / naive_denom)

    # ── Theil's U2 ───────────────────────────────────────────────
    if len(y_t) > 1:
        mse_naive         = float(np.mean(np.diff(y_t) ** 2)) + epsilon
        mse_model_aligned = float(np.mean(errors[1:] ** 2)) + epsilon
        theil_u = float(np.sqrt(mse_model_aligned / mse_naive))
    else:
        theil_u = 1.0

    return {
        # Primary (used for ranking & DM test)
        'MAE':    round(mae,   6),
        'RMSE':   round(rmse,  6),
        'MAPE':   round(mape,  4),    # %
        'sMAPE':  round(smape, 4),    # %
        'MASE':   round(mase,  6),
        'WAPE':   round(wape,  4),    # %
        'R2':     round(r2,    6),
        'DA':     round(da,    2),    # %
        # Secondary (diagnostic & reporting)
        'MSE':    round(mse,   6),
        'MdAE':   round(mdae,  6),
        'MdAPE':  round(mdape, 4),    # %
        'MaxAE':  round(maxae, 6),
        'Bias':   round(bias,  6),    # signed
        'TheilU': round(theil_u, 6),  # < 1 = beats naive
    }


def calculate_per_horizon_metrics(
    y_true_2d: np.ndarray,
    y_pred_2d: np.ndarray,
) -> dict:
    """
    Tính metrics cho từng horizon step riêng lẻ.

    Args:
        y_true_2d: [horizon, n_targets]
        y_pred_2d: [horizon, n_targets]

    Returns:
        dict: {'H1': {...}, 'H2': {...}, ..., 'overall': {...}}
    """
    horizon = y_true_2d.shape[0]
    results = {}
    for h in range(horizon):
        results[f'H{h+1}'] = calculate_metrics(y_true_2d[h], y_pred_2d[h])
    results['overall'] = calculate_metrics(y_true_2d, y_pred_2d)
    return results


def calculate_crps(y_true: np.ndarray, q10: np.ndarray, q50: np.ndarray, q90: np.ndarray) -> float:
    """
    Tính toán CRPS (Continuous Ranked Probability Score) từ 3 quantiles [0.1, 0.5, 0.9].
    Công thức xấp xỉ qua pinball loss:
    CRPS = 2 / M * sum_{i=1}^M Pinball_alpha_i(y - q_i)
    """
    y_true = np.array(y_true, dtype=np.float64)
    q10 = np.array(q10, dtype=np.float64)
    q50 = np.array(q50, dtype=np.float64)
    q90 = np.array(q90, dtype=np.float64)
    
    e10 = y_true - q10
    e50 = y_true - q50
    e90 = y_true - q90
    
    p10 = np.maximum(0.1 * e10, -0.9 * e10)
    p50 = np.maximum(0.5 * e50, -0.5 * e50)
    p90 = np.maximum(0.9 * e90, -0.1 * e90)
    
    crps_vals = (2.0 / 3.0) * (p10 + p50 + p90)
    return float(np.mean(crps_vals))
