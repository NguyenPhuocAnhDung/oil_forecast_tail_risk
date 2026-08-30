"""
src/models/baselines.py — Baseline Models
============================================
6 baseline architectures cho fair comparison:
1. LSTM
2. GRU
3. BiLSTM-Attention
4. XGBoost (non-neural)
5. PatchTST (Transformer-based)
6. DLinear (Linear decomposition)

Tất cả models nhận input [B, seq_len, input_dim] và output [B, horizon, output_dim].
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from src.models.sota_baselines import TimesNet, iTransformer, TimeMixer, SimplifiedTFT, SimplifiedNHits


# ============================================================
# 1. LSTM Baseline
# ============================================================
class BaselineLSTM(nn.Module):
  def __init__(self, input_dim: int, output_dim: int, horizon: int,
         hidden_dim: int = 64, num_layers: int = 2):
    super().__init__()
    self.horizon = horizon
    self.output_dim = output_dim
    self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers,
              batch_first=True, dropout=0.1)
    self.fc = nn.Linear(hidden_dim, horizon * output_dim)
  
  def forward(self, x):
    lstm_out, _ = self.lstm(x)
    out = self.fc(lstm_out[:, -1, :])
    return out.view(-1, self.horizon, self.output_dim)


# ============================================================
# 2. GRU Baseline
# ============================================================
class BaselineGRU(nn.Module):
  def __init__(self, input_dim: int, output_dim: int, horizon: int,
         hidden_dim: int = 64, num_layers: int = 2):
    super().__init__()
    self.horizon = horizon
    self.output_dim = output_dim
    self.gru = nn.GRU(input_dim, hidden_dim, num_layers=num_layers,
             batch_first=True, dropout=0.1)
    self.fc = nn.Linear(hidden_dim, horizon * output_dim)
  
  def forward(self, x):
    gru_out, _ = self.gru(x)
    out = self.fc(gru_out[:, -1, :])
    return out.view(-1, self.horizon, self.output_dim)


# ============================================================
# 3. BiLSTM-Attention Baseline
# ============================================================
class BaselineBiLSTMAttention(nn.Module):
  def __init__(self, input_dim: int, output_dim: int, horizon: int,
         hidden_dim: int = 64, num_layers: int = 2):
    super().__init__()
    self.horizon = horizon
    self.output_dim = output_dim
    self.bilstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers,
               batch_first=True, dropout=0.1, bidirectional=True)
    self.attention = nn.Sequential(
      nn.Linear(hidden_dim * 2, hidden_dim), nn.Tanh(),
      nn.Linear(hidden_dim, 1),
    )
    self.fc = nn.Linear(hidden_dim * 2, horizon * output_dim)
  
  def forward(self, x):
    bilstm_out, _ = self.bilstm(x) # [B, L, 2*hidden]
    attn_scores = self.attention(bilstm_out) # [B, L, 1]
    attn_weights = F.softmax(attn_scores, dim=1)
    context = torch.sum(attn_weights * bilstm_out, dim=1) # [B, 2*hidden]
    out = self.fc(context)
    return out.view(-1, self.horizon, self.output_dim)


# ============================================================
# 4. PatchTST Baseline (Simplified)
# ============================================================
class BaselinePatchTST(nn.Module):
  def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int = None,
         d_model: int = 32, nhead: int = 4, num_layers: int = 2,
         patch_len: int = 16, stride: int = 8):
    super().__init__()
    self.horizon = horizon
    self.output_dim = output_dim
    self.input_dim = input_dim
    
    if seq_len is None:
      seq_len = {1: 15, 3: 20, 5: 30, 10: 45, 60: 90}.get(horizon, 30)
    
    self.patch_len = min(patch_len, seq_len)
    self.stride = min(stride, self.patch_len)
    self.num_patches = max(1, (seq_len - self.patch_len) // self.stride + 1)
    
    self.patch_proj = nn.Linear(self.patch_len, d_model)
    encoder_layer = nn.TransformerEncoderLayer(
      d_model=d_model, nhead=nhead, dim_feedforward=d_model * 2,
      batch_first=True, dropout=0.1
    )
    self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
    self.head = nn.Linear(self.num_patches * d_model, horizon)
    self.projection = nn.Linear(input_dim, output_dim)
  
  def forward(self, x):
    B, L, D = x.shape
    # Channel-independence
    x_ci = x.transpose(1, 2).reshape(B * D, L)
    
    # Patching
    patches = []
    for i in range(self.num_patches):
      start = i * self.stride
      end = min(start + self.patch_len, L)
      patch = x_ci[:, start:end]
      if patch.shape[1] < self.patch_len:
        patch = F.pad(patch, (0, self.patch_len - patch.shape[1]))
      patches.append(patch.unsqueeze(1))
    x_patch = torch.cat(patches, dim=1) # [B*D, num_patches, patch_len]
    
    x_embed = self.patch_proj(x_patch)
    x_trans = self.transformer(x_embed)
    x_flat = x_trans.reshape(B * D, -1)
    out = self.head(x_flat) # [B*D, horizon]
    out = out.view(B, D, self.horizon).transpose(1, 2) # [B, H, D]
    return self.projection(out) # [B, H, output_dim]


# ============================================================
# 5. DLinear Baseline
# ============================================================
class MovingAvg(nn.Module):
  def __init__(self, kernel_size: int):
    super().__init__()
    self.kernel_size = kernel_size
    self.avg = nn.AvgPool1d(kernel_size=kernel_size, stride=1, padding=0)
  
  def forward(self, x):
    # x: [B, L, D]
    front = x[:, :1, :].repeat(1, (self.kernel_size - 1) // 2, 1)
    back = x[:, -1:, :].repeat(1, self.kernel_size // 2, 1)
    x = torch.cat([front, x, back], dim=1)
    x = x.transpose(1, 2)
    x = self.avg(x)
    return x.transpose(1, 2)


class BaselineDLinear(nn.Module):
  def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int = None):
    super().__init__()
    self.horizon = horizon
    self.output_dim = output_dim
    
    if seq_len is None:
      seq_len = {1: 15, 3: 20, 5: 30, 10: 45, 60: 90}.get(horizon, 30)
    
    kernel_size = min(25, seq_len // 2 * 2 + 1)
    if kernel_size % 2 == 0:
      kernel_size = max(1, kernel_size - 1)
    
    self.moving_avg = MovingAvg(kernel_size)
    self.linear_trend = nn.Linear(seq_len, horizon)
    self.linear_seasonal = nn.Linear(seq_len, horizon)
    self.projection = nn.Linear(input_dim, output_dim)
  
  def forward(self, x):
    trend = self.moving_avg(x) # [B, L, D]
    seasonal = x - trend
    
    trend_out = self.linear_trend(trend.transpose(1, 2)) # [B, D, H]
    seasonal_out = self.linear_seasonal(seasonal.transpose(1, 2))
    
    out = (trend_out + seasonal_out).transpose(1, 2) # [B, H, D]
    return self.projection(out) # [B, H, output_dim]


# ============================================================
# 6. XGBoost Baseline (wrapper)
# ============================================================
class BaselineXGBoost:
  """
  XGBoost baseline — non-neural, direct multi-output.
  Wraps sklearn/xgboost MultiOutputRegressor.
  """
  
  def __init__(self, output_dim: int, horizon: int):
    from xgboost import XGBRegressor
    from sklearn.multioutput import MultiOutputRegressor
    
    self.horizon = horizon
    self.output_dim = output_dim
    self.n_outputs = horizon * output_dim
    
    base = XGBRegressor(
      n_estimators=200, max_depth=6, learning_rate=0.05,
      subsample=0.8, colsample_bytree=0.8,
      random_state=42, verbosity=0,
      n_jobs=2,
    )
    self.model = MultiOutputRegressor(base, n_jobs=8)
    self.fitted = False
  
  def fit(self, X: np.ndarray, y: np.ndarray):
    """X: [N, seq_len, features] → flatten to [N, seq_len*features]"""
    X_flat = X.reshape(X.shape[0], -1)
    y_flat = y.reshape(y.shape[0], -1)
    self.model.fit(X_flat, y_flat)
    self.fitted = True
  
  def predict(self, X: np.ndarray) -> np.ndarray:
    """Returns [N, horizon, output_dim]"""
    X_flat = X.reshape(X.shape[0], -1)
    y_flat = self.model.predict(X_flat)
    return y_flat.reshape(-1, self.horizon, self.output_dim)


# ============================================================
# Model Registry
# ============================================================
BASELINE_REGISTRY = {
  'LSTM': BaselineLSTM,
  'GRU': BaselineGRU,
  'BiLSTM_Attention': BaselineBiLSTMAttention,
  'PatchTST': BaselinePatchTST,
  'DLinear': BaselineDLinear,
  'TimesNet': TimesNet,
  'iTransformer': iTransformer,
  'TimeMixer': TimeMixer,
  'TFT': SimplifiedTFT,
  'NHits': SimplifiedNHits,
  # XGBoost handled separately (non-PyTorch)
}

def get_baseline_model(name: str, input_dim: int, output_dim: int, horizon: int, seq_len: int = None):
  """Factory function to create baseline model."""
  if name == 'XGBoost':
    return BaselineXGBoost(output_dim=output_dim, horizon=horizon)
  
  if name not in BASELINE_REGISTRY:
    raise ValueError(f"Unknown baseline: {name}. Available: {list(BASELINE_REGISTRY.keys()) + ['XGBoost']}")
  
  if seq_len is None:
    from config import get_unified_config
    seq_len = get_unified_config('BOTH', horizon)['seq_len']
  
  model_class = BASELINE_REGISTRY[name]
  if name in ['PatchTST', 'DLinear', 'TimesNet', 'iTransformer', 'TimeMixer', 'TFT', 'NHits']:
    return model_class(input_dim=input_dim, output_dim=output_dim, horizon=horizon, seq_len=seq_len)
  else:
    return model_class(input_dim=input_dim, output_dim=output_dim, horizon=horizon)
