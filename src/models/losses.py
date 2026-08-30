"""
src/models/losses.py — Loss Functions
========================================
Quantile Pinball Loss cho GUMNet probabilistic output.
Huber Loss cho robust regression (fat tails).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


def quantile_pinball_loss(predictions: torch.Tensor, targets: torch.Tensor,
             quantiles: list = None) -> torch.Tensor:
  """
  Quantile (Pinball) Loss cho multi-quantile prediction.
  
  L_q(y, ŷ) = max(q × (y - ŷ), (q-1) × (y - ŷ))
  
  Args:
    predictions: [B, H, Q] — Q quantile predictions
    targets: [B, H] — actual values
    quantiles: list of quantile levels (default [0.1, 0.5, 0.9])
  
  Returns:
    Scalar loss (mean over all quantiles, horizons, samples)
  """
  if quantiles is None:
    quantiles = [0.1, 0.5, 0.9]
  
  device = predictions.device
  quantiles_tensor = torch.tensor(quantiles, device=device, dtype=torch.float32)
  
  # targets: [B, H] → [B, H, 1] for broadcasting
  targets = targets.unsqueeze(-1)
  
  # errors: [B, H, Q]
  errors = targets - predictions
  
  # Pinball loss per quantile
  loss = torch.max(quantiles_tensor * errors, (quantiles_tensor - 1) * errors)
  
  return loss.mean()


class HuberQuantileLoss(nn.Module):
  """
  Huber-Quantile Loss — robust version of quantile loss.
  Reduces sensitivity to outliers (fat-tailed distributions).
  
  Combines Huber loss with quantile weighting:
  L(y, ŷ) = Σ_q ρ_q(y - ŷ) where ρ_q uses Huber instead of linear penalty
  """
  
  def __init__(self, quantiles: list = None, delta: float = 1.0):
    super().__init__()
    self.quantiles = quantiles or [0.1, 0.5, 0.9]
    self.delta = delta
  
  def forward(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    """
    Args:
      predictions: [B, H, Q]
      targets: [B, H]
    """
    targets = targets.unsqueeze(-1)
    errors = targets - predictions
    
    quantiles = torch.tensor(self.quantiles, device=predictions.device)
    
    # Huber-ized errors
    abs_errors = torch.abs(errors)
    quadratic = torch.clamp(abs_errors, max=self.delta)
    linear = abs_errors - quadratic
    huber = 0.5 * quadratic ** 2 + self.delta * linear
    
    # Apply quantile weighting
    weights = torch.where(errors >= 0, quantiles, 1 - quantiles)
    loss = weights * huber
    
    return loss.mean()


class MSELossFlat(nn.Module):
  """MSE Loss that handles [B, H, C] shape for baselines."""
  
  def __init__(self):
    super().__init__()
    self.mse = nn.MSELoss()
  
  def forward(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    return self.mse(predictions, targets)
