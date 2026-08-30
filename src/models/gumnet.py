"""
src/models/gumnet.py — GUMNet-WF v2
======================================
Gated Unified Mixture Network with Walk-Forward validation.

Cải tiến so với v1:
1. Horizon-Grouped Prediction Heads (short/medium/long)
2. Residual Connection to Naive Forecast
3. Multi-Resolution CNN (Inception-style: k=3,7,15)
4. Expanded Gate bottleneck (128 thay vì 64)
5. Expert capacity scaling option

Kiến trúc:
- 3 Experts: Multi-Scale CNN + GRU+Attention + Wavelet-KAN
- Dynamic Horizon-Aware Gating (Positional Embedding per step h)
- Output: [B, H, C, Q] với Q quantiles
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F


class WaveletKANBlock(nn.Module):
  """
  Wavelet-enhanced Kolmogorov-Arnold Network block.
  
  ψ(x) = (1 - x²) · exp(-0.5x²)  (Mexican Hat Wavelet)
  output = SiLU(W₁·x) + W₂·ψ((x - t)/s)
  """
  
  def __init__(self, in_dim: int, out_dim: int):
    super().__init__()
    self.scale = nn.Parameter(torch.ones(1, 1, in_dim))
    self.translation = nn.Parameter(torch.zeros(1, 1, in_dim))
    self.weight_base = nn.Linear(in_dim, out_dim)
    self.weight_wavelet = nn.Linear(in_dim, out_dim)
  
  def forward(self, x: torch.Tensor) -> torch.Tensor:
    # Learnable scale (positive)
    scale_safe = F.softplus(self.scale) + 1e-5
    x_norm = (x - self.translation) / scale_safe
    x_norm = torch.clamp(x_norm, min=-10.0, max=10.0)
    
    # Mexican Hat wavelet
    wavelet = (1 - x_norm ** 2) * torch.exp(-0.5 * x_norm ** 2)
    
    # KAN combination: base activation + wavelet transformation
    base = F.silu(self.weight_base(x))
    wav = self.weight_wavelet(wavelet)
    return base + wav


class BSplineKANBlock(nn.Module):
  """
  Simplified B-spline KAN Block for ablation study.
  Uses a polynomial expansion as a proxy for B-splines.
  """
  def __init__(self, in_dim: int, out_dim: int):
    super().__init__()
    self.weight_base = nn.Linear(in_dim, out_dim)
    self.weight_p2 = nn.Linear(in_dim, out_dim)
    self.weight_p3 = nn.Linear(in_dim, out_dim)
  
  def forward(self, x: torch.Tensor) -> torch.Tensor:
    base = F.silu(self.weight_base(x))
    p2 = self.weight_p2(x ** 2)
    p3 = self.weight_p3(x ** 3)
    return base + p2 + p3


class TemporalAttention(nn.Module):
  """
  Temporal Attention: weighted aggregation thay thế mean pooling.
  Cho phép mô hình tập trung vào các timestep quan trọng.
  """
  
  def __init__(self, input_dim: int):
    super().__init__()
    self.attention_net = nn.Sequential(
      nn.Linear(input_dim, input_dim // 2),
      nn.Tanh(),
      nn.Linear(input_dim // 2, 1),
    )
  
  def forward(self, x: torch.Tensor) -> torch.Tensor:
    """x: [B, L, D] → [B, D]"""
    scores = self.attention_net(x)      # [B, L, 1]
    weights = F.softmax(scores, dim=1)    # [B, L, 1]
    context = torch.sum(weights * x, dim=1) # [B, D]
    return context


class MultiScaleCNN(nn.Module):
  """
  Inception-style Multi-Scale CNN.
  
  3 parallel convolutions (kernel 3, 7, 15) capture:
  - k=3: Biến động tần số cao (daily shocks)
  - k=7: Biến động trung tần (weekly patterns)
  - k=15: Xu hướng (multi-week trends)
  """
  
  def __init__(self, input_dim: int, d_feat: int):
    super().__init__()
    d_per_scale = d_feat // 3
    d_remainder = d_feat - 2 * d_per_scale # Handle non-divisible
    
    self.conv_k3 = nn.Conv1d(input_dim, d_per_scale, kernel_size=3, padding=1)
    self.conv_k7 = nn.Conv1d(input_dim, d_per_scale, kernel_size=7, padding=3)
    self.conv_k15 = nn.Conv1d(input_dim, d_remainder, kernel_size=15, padding=7)
    
    self.norm = nn.LayerNorm(d_feat)
  
  def forward(self, x: torch.Tensor) -> torch.Tensor:
    """x: [B, L, D] → [B, L, d_feat]"""
    x_t = x.transpose(1, 2) # [B, D, L]
    
    out_k3 = F.relu(self.conv_k3(x_t))   # [B, d/3, L]
    out_k7 = F.relu(self.conv_k7(x_t))   # [B, d/3, L]
    out_k15 = F.relu(self.conv_k15(x_t))  # [B, d/3, L]
    
    out = torch.cat([out_k3, out_k7, out_k15], dim=1) # [B, d_feat, L]
    out = out.transpose(1, 2) # [B, L, d_feat]
    return self.norm(out)


class GUMNet(nn.Module):
  """
  Gated Unified Mixture Network — v2
  
  Architecture:
    Input [B, L, D]
     Expert 1: Multi-Scale CNN → TemporalAttention → f_cnn [B, d]
     Expert 2: GRU + MultiheadAttention → TemporalAttention → f_gru [B, d]
     Expert 3: Wavelet-KAN → TemporalAttention → f_kan [B, d]
    
    For each horizon step h:
      pos_h = Embedding(h)      [B, d]
      gate_input = [f_cnn; f_gru; f_kan; pos_h] [B, 4d]
      weights_h = Softmax(MLP(gate_input))    [B, 3]
      f_fused_h = Σ weights_h[i] × f_expert_i  [B, d]
      pred_h = HeadGroup(f_fused_h) + residual  [B, C×Q]
  
  Args:
    seq_len: Lookback window length
    input_dim: Number of input features
    output_dim: Number of target variables
    horizon: Forecast horizon
    d_feat: Hidden dimension
    num_quantiles: Number of quantile outputs
  """
  
  def __init__(self, seq_len: int = 30, input_dim: int = 11, output_dim: int = 2,
         horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3):
    super().__init__()
    self.seq_len = seq_len
    self.horizon = horizon
    self.output_dim = output_dim
    self.num_quantiles = num_quantiles
    self.d_feat = d_feat
    self.ablation = os.environ.get('GUMNET_ABLATION', 'none')
    
    # Horizon group for architecture decisions
    # H1-H5: short, H10: medium, H60: long
    self._horizon_group = 'short' if horizon <= 5 else ('medium' if horizon <= 15 else 'long')
    
    # === EXPERTS ===
    # Expert 1: Multi-Scale CNN (captures multi-resolution temporal patterns)
    self.cnn = MultiScaleCNN(input_dim, d_feat)
    self.cnn_attention = TemporalAttention(d_feat)
    
    # Expert 2: GRU + Self-Attention
    # 2 layers for all horizons — 3 layers caused convergence failure for H10/H60
    self.gru = nn.GRU(input_dim, d_feat, num_layers=2, batch_first=True, dropout=0.1)
    self.self_attention = nn.MultiheadAttention(embed_dim=d_feat, num_heads=4, batch_first=True)
    self.gru_attention = TemporalAttention(d_feat)
    
    # Expert 3: Wavelet-KAN (captures non-linear wavelet features)
    if self.ablation == 'bspline_kan':
      self.kan = BSplineKANBlock(input_dim, d_feat)
    else:
      self.kan = WaveletKANBlock(input_dim, d_feat)
    self.kan_attention = TemporalAttention(d_feat)
    
    # === HORIZON-AWARE GATING ===
    self.horizon_pos_embedding = nn.Embedding(horizon, d_feat)
    
    # Gate network (expanded bottleneck: 128 instead of 64)
    self.gate = nn.Sequential(
      nn.Linear(d_feat * 4, 128), # 3 experts + 1 position
      nn.ReLU(),
      nn.Dropout(0.1),
      nn.Linear(128, 3),
      nn.Softmax(dim=-1),
    )
    
    # === HORIZON-GROUPED PREDICTION HEADS ===
    # Short-term (H1-H10): Simple linear
    self.short_head = nn.Linear(d_feat, output_dim * num_quantiles)
    
    # Medium-term (H11-H20): 2-layer MLP
    self.medium_head = nn.Sequential(
      nn.Linear(d_feat, d_feat),
      nn.GELU(),
      nn.Dropout(0.1),
      nn.Linear(d_feat, output_dim * num_quantiles),
    )
    
    # Long-term (H21+): Deeper MLP with more capacity
    self.long_head = nn.Sequential(
      nn.Linear(d_feat, d_feat * 2),
      nn.GELU(),
      nn.Dropout(0.2),
      nn.Linear(d_feat * 2, d_feat),
      nn.GELU(),
      nn.Linear(d_feat, output_dim * num_quantiles),
    )
    
    # === RESIDUAL SCALING ===
    # Per-step learnable residual scale vector.
    # H1 model (1 step): learns to be close to 1.0 → strong naive-like residual
    # H60 model (60 steps): early steps learn ~0.8, late steps learn ~0.2
    # This allows the model to automatically calibrate confidence per step
    self.residual_scale = nn.Parameter(torch.ones(horizon) * 0.5)
  
  def _get_head(self, step_idx: int) -> nn.Module:
    """Chọn prediction head dựa trên horizon group (không phải step index).
    
    Trước đây: head chọn theo step index (0-9 luôn = short_head)
    → H10 model luôn dùng linear head → underfit
    
    Bây giờ: head chọn theo configured horizon
    → H10 dùng medium_head, H60 dùng long_head
    """
    if self._horizon_group == 'short':   # H1-H5
      return self.short_head
    elif self._horizon_group == 'medium': # H10
      return self.medium_head
    else:                                # H60
      # Within H60: early steps use medium, late steps use long
      if step_idx < 10:
        return self.medium_head
      else:
        return self.long_head
  
  def forward(self, x: torch.Tensor) -> tuple:
    """
    Forward pass.
    
    Args:
      x: [B, L, D] input time series
    
    Returns:
      predictions: [B, H, C, Q] quantile predictions
      gating_weights: [B, H, 3] expert weights per step
    """
    B, L, D = x.shape
    
    # === Extract expert features ===
    # Expert 1: Multi-Scale CNN
    cnn_out = self.cnn(x)           # [B, L, d_feat]
    f_cnn = self.cnn_attention(cnn_out)     # [B, d_feat]
    
    # Expert 2: GRU + Self-Attention
    gru_out, _ = self.gru(x)          # [B, L, d_feat]
    attn_out, _ = self.self_attention(gru_out, gru_out, gru_out) # [B, L, d_feat]
    f_gru = self.gru_attention(attn_out)    # [B, d_feat]
    
    # Expert 3: Wavelet-KAN
    kan_out = self.kan(x)            # [B, L, d_feat]
    f_kan = self.kan_attention(kan_out)     # [B, d_feat]
    
    # === Dynamic Gating per Horizon Step ===
    all_preds = []
    all_weights = []
    horizon_indices = torch.arange(self.horizon, device=x.device)
    
    for h in range(self.horizon):
      # Positional embedding for step h
      pos_h = self.horizon_pos_embedding(horizon_indices[h])
      pos_h = pos_h.unsqueeze(0).expand(B, -1) # [B, d_feat]
      
      gate_input = torch.cat([f_cnn, f_gru, f_kan, pos_h], dim=-1) # [B, 4*d_feat]
      
      if self.ablation == 'equal_gating':
        weights_h = torch.ones(B, 3, device=x.device) / 3.0
      else:
        weights_h = self.gate(gate_input) # [B, 3]
      
      # Fused representation
      f_fused = (weights_h[:, 0:1] * f_cnn +
            weights_h[:, 1:2] * f_gru +
            weights_h[:, 2:3] * f_kan) # [B, d_feat]
      
      # Horizon-grouped prediction with residual
      head = self._get_head(h)
      raw_pred = head(f_fused) # [B, C*Q]
      
      # Residual connection: default = zero return (naive forecast)
      # Model only learns the delta from naive
      if self.ablation == 'no_residual':
        pred_h = raw_pred
      else:
        # Per-step residual scale: sigmoid maps to (0,1)
        scale_h = torch.sigmoid(self.residual_scale[h])
        pred_h = scale_h * raw_pred
      
      all_preds.append(pred_h)
      all_weights.append(weights_h)
    
    # Stack predictions: [B, H, C*Q] → [B, H, C, Q]
    predictions = torch.stack(all_preds, dim=1)
    predictions = predictions.view(B, self.horizon, self.output_dim, self.num_quantiles)
    
    gating_weights = torch.stack(all_weights, dim=1) # [B, H, 3]
    
    return predictions, gating_weights
