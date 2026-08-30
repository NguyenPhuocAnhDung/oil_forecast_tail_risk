"""
src/utils.py — Utility functions
=================================
Seed management, logging, và các helper dùng chung.
"""

import os
import sys
import time
import copy
import random
import logging
import numpy as np
import torch


def set_seed(seed: int = 42):
  """Thiết lập seed cho reproducibility hoàn toàn."""
  random.seed(seed)
  np.random.seed(seed)
  torch.manual_seed(seed)
  if torch.cuda.is_available():
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
  os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
  # warn_only=True: log warning cho non-deterministic ops (e.g. TimeMixer upsample)
  # nhưng KHÔNG crash → reproducibility vẫn đảm bảo qua manual seeds + cudnn.deterministic
  torch.use_deterministic_algorithms(True, warn_only=True)



def get_device() -> torch.device:
  """Trả về GPU nếu có, ngược lại CPU."""
  if torch.cuda.is_available():
    device = torch.device('cuda')
    print(f" Using GPU: {torch.cuda.get_device_name(0)}")
  else:
    device = torch.device('cpu')
    print(" Using CPU")
  return device


def setup_logger(name: str, log_dir: str, level=logging.INFO) -> logging.Logger:
  """Tạo logger ghi file + console."""
  os.makedirs(log_dir, exist_ok=True)
  log_file = os.path.join(log_dir, f"{name}_{time.strftime('%Y%m%d_%H%M%S')}.log")

  logger = logging.getLogger(name)
  logger.setLevel(level)
  logger.handlers.clear()

  # File handler
  fh = logging.FileHandler(log_file, encoding='utf-8')
  fh.setLevel(level)
  fh.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S'))
  logger.addHandler(fh)

  # Console handler
  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(level)
  ch.setFormatter(logging.Formatter('%(message)s'))
  logger.addHandler(ch)

  return logger


def calculate_metrics(
  y_true: np.ndarray,
  y_pred: np.ndarray,
  naive_mae: float = None,
) -> dict:
  """
  Tính toán đầy đủ metrics đánh giá dự báo.
  Metrics: MAE, RMSE, MAPE, sMAPE, MASE, WAPE, MdAE, MdAPE,
           MaxAE, Bias, R2, DA, TheilU (+ PICP/PINAW added externally).
  """
  from sklearn.metrics import r2_score

  epsilon = 1e-8
  y_true = np.array(y_true, dtype=np.float64)
  y_pred = np.array(y_pred, dtype=np.float64)

  # Directional Accuracy
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

  mae   = float(np.mean(abs_err))
  mse   = float(np.mean(errors ** 2))
  rmse  = float(np.sqrt(mse))
  mape  = float(np.mean(abs_err / abs_true) * 100)
  smape = float(np.mean(2 * abs_err / (abs_true + np.abs(y_p) + epsilon)) * 100)
  wape  = float(np.sum(abs_err) / (np.sum(abs_true) + epsilon) * 100)
  mdae  = float(np.median(abs_err))
  mdape = float(np.median(abs_err / abs_true) * 100)
  maxae = float(np.max(abs_err))
  bias  = float(np.mean(errors))

  try:
    r2 = float(r2_score(y_t, y_p))
  except ValueError:
    r2 = 0.0

  # MASE
  if naive_mae is not None and naive_mae > epsilon:
    mase = float(mae / naive_mae)
  else:
    naive_denom = float(np.mean(np.abs(np.diff(y_t)))) + epsilon if len(y_t) > 1 else epsilon
    mase = float(mae / naive_denom)

  # Theil's U2
  if len(y_t) > 1:
    mse_naive         = float(np.mean(np.diff(y_t) ** 2)) + epsilon
    mse_model_aligned = float(np.mean(errors[1:] ** 2)) + epsilon
    theil_u = float(np.sqrt(mse_model_aligned / mse_naive))
  else:
    theil_u = 1.0

  return {
    'MAE':    round(mae,   6),
    'RMSE':   round(rmse,  6),
    'MAPE':   round(mape,  4),
    'sMAPE':  round(smape, 4),
    'MASE':   round(mase,  6),
    'WAPE':   round(wape,  4),
    'R2':     round(r2,    6),
    'DA':     round(da,    2),
    'MSE':    round(mse,   6),
    'MdAE':   round(mdae,  6),
    'MdAPE':  round(mdape, 4),
    'MaxAE':  round(maxae, 6),
    'Bias':   round(bias,  6),
    'TheilU': round(theil_u, 6),
  }


