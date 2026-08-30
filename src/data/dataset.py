"""
src/data/dataset.py — Data Processing Pipeline
=================================================
Tiền xử lý dữ liệu, tạo dataset cho training.
Hỗ trợ Direct Cumulative Target (leakage-free).

Nguyên lý cốt lõi:
- LUÔN dùng ffill() cho missing values (nhân quả)
- KHÔNG BAO GIỜ dùng bfill() hay interpolate() (rò rỉ tương lai)
- MinMaxScaler [-1, 1] fit PER WINDOW trên train set only
- Direct Cumulative Target: y = log(P_{t+h} / P_t) cho mọi h
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from torch.utils.data import Dataset
import torch


class DataProcessor:
  """
  Xử lý dữ liệu time series cho forecasting.
  
  Pipeline:
  1. Nhận df (log-differenced) và df_raw (giá tuyệt đối)
  2. Scale features bằng MinMaxScaler [-1, 1]
  3. Tạo sliding window X [seq_len] và y [horizon]
  4. Target: Direct Cumulative = log(P_{t+h} / P_t)
  """
  
  def __init__(self, seq_len: int, horizon: int):
    self.seq_len = seq_len
    self.horizon = horizon
    self.feature_scaler = StandardScaler()
    self.target_scaler = StandardScaler()
  
  def prepare_data(self, df: pd.DataFrame, target_cols: list, feature_cols: list,
           df_raw: pd.DataFrame = None, is_train: bool = True,
           fit_scaler: bool = True) -> tuple:
    """
    Chuẩn bị X, y từ DataFrame.
    
    Args:
      df: DataFrame đã log-differenced
      target_cols: Cột target (e.g., ['MG95', 'MG92'])
      feature_cols: Cột features
      df_raw: DataFrame giá tuyệt đối (cho Direct Cumulative)
      is_train: True = fit scaler, False = chỉ transform
      fit_scaler: True = fit_transform, False = transform
    
    Returns:
      X: [n_samples, seq_len, n_features]
      y: [n_samples, n_targets, horizon]
    """
    # Filter available features
    available_features = [c for c in feature_cols if c in df.columns]
    features_data = df[available_features].values
    
    # Scale features
    if is_train and fit_scaler:
      features_scaled = self.feature_scaler.fit_transform(features_data)
    else:
      features_scaled = self.feature_scaler.transform(features_data)
    
    # === DIRECT CUMULATIVE TARGET ===
    # Target = log(P_{t+h} / P_t) — tính trên giá tuyệt đối
    df_target = df_raw if df_raw is not None else df
    absolute_prices = df_target[target_cols].values.copy().astype(np.float64)
    
    # Xử lý giá ≤ 0 (e.g., WTI âm ngày COVID)
    absolute_prices[absolute_prices <= 0] = 1e-9
    
    # Sliding window cho Direct Cumulative
    total_len = len(df)
    valid_range = total_len - self.seq_len - self.horizon + 1
    if valid_range <= 0:
      return np.array([]), np.array([])
    
    # Tạo cumulative log-returns
    p_view = np.lib.stride_tricks.sliding_window_view(
      absolute_prices, window_shape=(self.seq_len + self.horizon), axis=0
    )
    # p_view shape: [n_windows, n_targets, window_length]
    p_view = p_view.transpose(0, 2, 1) # → [n_windows, window_length, n_targets]
    
    p_t = p_view[:, self.seq_len - 1, :]  # Giá tại thời điểm t: [n_windows, n_targets]
    p_future = p_view[:, self.seq_len:, :]  # Giá t+1..t+h: [n_windows, horizon, n_targets]
    
    # R_{t→t+h} = log(P_{t+h} / P_t) cho mỗi h
    log_returns_cumulative = np.log(p_future / p_t[:, np.newaxis, :])
    # Shape: [n_windows, horizon, n_targets]
    
    # Scale targets
    targets_data = log_returns_cumulative # [n_windows, horizon, n_targets]
    n_samples, n_horizon, n_targets = targets_data.shape
    
    if is_train and fit_scaler:
      targets_flat = self.target_scaler.fit_transform(
        targets_data.reshape(-1, n_targets)
      )
    else:
      targets_flat = self.target_scaler.transform(
        targets_data.reshape(-1, n_targets)
      )
    
    targets_scaled = targets_flat.reshape(n_samples, n_horizon, n_targets)
    # Transpose to [n_samples, n_targets, horizon]
    targets_scaled = targets_scaled.transpose(0, 2, 1)
    
    # === SLIDING WINDOW cho X ===
    X_view = np.lib.stride_tricks.sliding_window_view(
      features_scaled, window_shape=self.seq_len, axis=0
    )
    X = X_view[:valid_range].transpose(0, 2, 1) # [n_samples, seq_len, n_features]
    y = targets_scaled[:valid_range]        # [n_samples, n_targets, horizon]
    
    return np.copy(X), np.copy(y)
  
  def inverse_transform_targets(self, y_scaled: np.ndarray) -> np.ndarray:
    """
    Inverse transform scaled targets về log-returns.
    
    Args:
      y_scaled: [horizon, n_targets] hoặc [n_targets, horizon]
    
    Returns:
      log_returns: Cùng shape
    """
    if y_scaled.ndim == 2:
      n_targets = self.target_scaler.n_features_in_
      # Detect orientation: if first dim == n_targets, transpose
      if y_scaled.shape[0] == n_targets and y_scaled.shape[1] != n_targets:
        # [n_targets, horizon] → transpose to [horizon, n_targets]
        y_t = y_scaled.T
        result = self.target_scaler.inverse_transform(y_t)
        return result.T # Back to [n_targets, horizon]
      else:
        return self.target_scaler.inverse_transform(y_scaled)
    return y_scaled


class PetroleumDataset(Dataset):
  """PyTorch Dataset wrapper cho petroleum price data."""
  
  def __init__(self, X: np.ndarray, y: np.ndarray):
    self.X = torch.tensor(X, dtype=torch.float32)
    self.y = torch.tensor(y, dtype=torch.float32)
  
  def __len__(self):
    return len(self.X)
  
  def __getitem__(self, idx):
    return self.X[idx], self.y[idx]
