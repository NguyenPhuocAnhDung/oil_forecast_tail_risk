"""
gumnet_het.py  –  GUMNet with Heterogeneous Expert Routing (v3 architecture)
=============================================================================
Key innovation over v2:
  Each expert receives a DIFFERENT subset of input features:
  - CNN Expert  ← raw price series (price levels + crude benchmarks)
  - GRU Expert  ← macro/external indicators (USD, GPR, monthly)
  - KAN Expert  ← derived ratio/momentum features (ratios, vol, cyclical)

This mirrors the Mixture-of-Experts (MoE) principle: each expert is a
specialist, not a generalist. Theoretical justification from:
  Jacobs et al. (1991) "Adaptive mixtures of local experts"
  Fedus et al. (2022) "Switch Transformers" (Switch-MoE routing)

Feature partitioning:
  CNN_FEAT_KEYS = price products + crude benchmarks
  GRU_FEAT_KEYS = USD_Index, GPR (+ MA30 variants for H60)
  KAN_FEAT_KEYS = Ratio_*, Trend_WTI, Vol_WTI_*, Day_sin, Day_cos

Enabled via: GUMNET_HET=1 environment variable
"""
import os
import torch
import torch.nn as nn
import numpy as np
from typing import Optional

# Feature type identifiers (must match config.py feature_cols)
CNN_FEAT_KEYS = ['MG97', 'MG95', 'MG92', 'NAPHTHA', 'KERO',
                 'DO 0.001%', 'DO 0.05%', 'FO 180',
                 'WTI_Daily', 'Brent_EU_Daily', 'BRT_DTD', 'BRT_KH']
GRU_FEAT_KEYS = ['USD_Index', 'GPR', 'GPR_MA30', 'USD_Index_MA30',
                 'WTI_Monthly', 'Brent_Global_Monthly']
KAN_FEAT_KEYS = ['Ratio_95_WTI', 'Ratio_92_WTI',
                 'Ratio_DO001_WTI', 'Ratio_DO05_WTI', 'Ratio_DO_Spread',
                 'Trend_WTI', 'Vol_WTI_10d', 'Vol_WTI_30d',
                 'Day_sin', 'Day_cos']

def get_feature_indices(feature_cols, keys):
    """Get column indices for given feature keys."""
    indices = [i for i, f in enumerate(feature_cols) if f in keys]
    return indices if indices else list(range(len(feature_cols)))  # fallback to all


class TemporalAttention(nn.Module):
    """Scaled dot-product attention over temporal dimension."""
    def __init__(self, d: int, n_heads: int = 4):
        super().__init__()
        self.attn = nn.MultiheadAttention(d, n_heads, batch_first=True, dropout=0.05)
        self.norm = nn.LayerNorm(d)

    def forward(self, x):  # [B, T, d]
        out, _ = self.attn(x, x, x)
        out = self.norm(out + x)
        return out[:, -1]  # take last time step as summary


class MultiScaleCNN(nn.Module):
    """Multi-scale temporal CNN with kernels at 3, 7, 15 days."""
    def __init__(self, in_channels: int, d: int):
        super().__init__()
        self.d_per = d // 3
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels, self.d_per, kernel_size=k, padding=k // 2)
            for k in [3, 7, 15]
        ])
        concat_dim = self.d_per * 3
        self.proj = nn.Linear(concat_dim, d)
        self.norm = nn.LayerNorm(d)

    def forward(self, x):  # [B, T, C] → [B, d]
        x = x.transpose(1, 2)  # [B, C, T]
        outs = []
        for conv in self.convs:
            y = torch.relu(conv(x))  # [B, d_per, T']
            outs.append(y)
        out = torch.cat(outs, dim=1)  # [B, d_per*3, T']
        out = out.transpose(1, 2)  # [B, T', d_per*3]
        return self.norm(self.proj(out[:, -1]))  # [B, d]



class WaveletKANBlock(nn.Module):
    """Wavelet-KAN with Mexican hat basis functions for non-linear ratio features."""
    def __init__(self, in_dim: int, d: int, n_wavelets: int = 8):
        super().__init__()
        self.linear_in  = nn.Linear(in_dim, d)
        self.scales     = nn.Parameter(torch.rand(n_wavelets) + 0.5)
        self.shifts     = nn.Parameter(torch.randn(n_wavelets))
        self.coeffs     = nn.Linear(n_wavelets * in_dim, d)
        self.proj       = nn.Linear(d * 2, d)
        self.norm       = nn.LayerNorm(d)

    def forward(self, x):  # [B, T, D] → [B, d]
        t = x[:, -1]  # last time step [B, D]
        B, D = t.shape
        t_exp = t.unsqueeze(-1).expand(-1, -1, len(self.scales))  # [B, D, n_w]
        z = (t_exp - self.shifts) / (self.scales.abs() + 1e-4)
        psi = (1 - z**2) * torch.exp(-0.5 * z**2)  # Mexican hat
        psi_flat = psi.reshape(B, -1)  # [B, D*n_w]
        linear = torch.relu(self.linear_in(t))
        wavelet = torch.relu(self.coeffs(psi_flat))
        return self.norm(self.proj(torch.cat([linear, wavelet], dim=-1)))


class GUMNetHet(nn.Module):
    """
    GUMNet v3: Heterogeneous Expert Routing
    
    Each expert receives a SPECIALIZED feature subset:
      CNN ← price/benchmark series (captures multi-scale temporal patterns)
      GRU ← macro indicators (captures economic regime dynamics)  
      KAN ← ratio/momentum features (captures non-linear relationships)
    
    Theoretically justified by: Jacobs et al. (1991) MoE theory,
    and empirically motivated by the distinct information content of each
    feature group in petroleum price forecasting.
    """
    
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.output_dim = output_dim
        self.num_quantiles = num_quantiles
        self.d_feat = d_feat
        
        # Feature partition indices
        if feature_cols is not None:
            self.cnn_idx = get_feature_indices(feature_cols, CNN_FEAT_KEYS)
            self.gru_idx = get_feature_indices(feature_cols, GRU_FEAT_KEYS)
            self.kan_idx = get_feature_indices(feature_cols, KAN_FEAT_KEYS)
        else:
            # Fallback: use all features for all experts (same as v2)
            self.cnn_idx = list(range(input_dim))
            self.gru_idx = list(range(input_dim))
            self.kan_idx = list(range(input_dim))
        
        cnn_dim = len(self.cnn_idx)
        gru_dim = len(self.gru_idx)
        kan_dim = len(self.kan_idx)
        
        # Expert 1: Multi-Scale CNN (price series expert)
        self.cnn = MultiScaleCNN(cnn_dim, d_feat)
        self.cnn_attn = TemporalAttention(d_feat)
        self.cnn_proj = nn.Linear(d_feat, d_feat)  # re-project after attention
        
        # Expert 2: GRU + Attention (macro dynamics expert)
        self.gru = nn.GRU(gru_dim, d_feat, num_layers=2, batch_first=True, dropout=0.1)
        self.gru_attn = TemporalAttention(d_feat)
        
        # Expert 3: Wavelet-KAN (ratio/momentum expert)
        self.kan = WaveletKANBlock(kan_dim, d_feat)
        
        # Horizon position embedding (regime-aware context)
        self.pos_embed = nn.Embedding(horizon, d_feat)
        
        # Gate network: concatenate expert outputs + position + input STATS
        # Input stats: [mean, std] of full input → 2*input_dim features
        gate_in_dim = d_feat * 3 + d_feat + 2 * input_dim
        self.gate = nn.Sequential(
            nn.Linear(gate_in_dim, 256),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(256, 64),
            nn.GELU(),
            nn.Linear(64, 3),
            nn.Softmax(dim=-1),
        )
        
        # Prediction heads (horizon-grouped)
        self._horizon_group = 'short' if horizon <= 5 else ('medium' if horizon <= 15 else 'long')
        
        self.head = nn.Sequential(
            nn.Linear(d_feat, d_feat),
            nn.GELU(),
            nn.Dropout(0.1 if horizon <= 5 else 0.2),
            nn.Linear(d_feat, output_dim * num_quantiles),
        )
        
        # Per-step residual scaling vector
        self.residual_scale = nn.Parameter(torch.ones(horizon) * 0.1)
    
    def forward(self, x):  # [B, L, D]
        B, L, D = x.shape
        
        # Extract expert-specific inputs
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        # Input context statistics for gate (regime signal)
        x_mean = x.mean(dim=1)  # [B, D]
        x_std  = x.std(dim=1)   # [B, D]
        x_ctx  = torch.cat([x_mean, x_std], dim=-1)  # [B, 2D]
        
        # CNN Expert (price series)
        f_cnn = self.cnn(x_cnn)  # [B, d]
        
        # GRU Expert (macro)
        gru_out, _ = self.gru(x_gru)  # [B, L, d]
        f_gru = gru_out[:, -1]  # take last step [B, d]
        
        # KAN Expert (ratios)
        f_kan = self.kan(x_kan)  # [B, d]
        
        # Per-horizon predictions
        preds = []
        gates_list = []
        
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)  # [B, d]
            
            # Dynamic gating: conditioned on experts + position + global stats
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            w = self.gate(gate_input)  # [B, 3]
            gates_list.append(w)
            
            # Fused expert representation
            f_fused = (w[:, 0:1] * f_cnn +
                       w[:, 1:2] * f_gru +
                       w[:, 2:3] * f_kan)  # [B, d]
            
            # Prediction + horizon-step residual
            pred_h = self.head(f_fused)  # [B, C*Q]
            residual = x[:, -1, :self.output_dim].unsqueeze(-1) * self.residual_scale[h_idx]
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))  # [B, 1, C, Q]
        
        preds = torch.cat(preds, dim=1)  # [B, H, C, Q]
        gates = torch.stack(gates_list, dim=1)  # [B, H, 3]
        return preds, gates


if __name__ == '__main__':
    # Quick test
    from config import get_unified_config
    
    for target in ['XANG', 'DAU']:
        for h in [1, 3, 5, 10, 60]:
            cfg = get_unified_config(target, h)
            feats = cfg['feature_cols']
            d = cfg.get('d_feat', 64)
            
            model = GUMNetHet(
                seq_len=cfg['seq_len'], input_dim=len(feats),
                output_dim=2, horizon=h, d_feat=d,
                feature_cols=feats
            )
            x = torch.randn(4, cfg['seq_len'], len(feats))
            preds, gates = model(x)
            params = sum(p.numel() for p in model.parameters())
            
            cnn_n = len(get_feature_indices(feats, CNN_FEAT_KEYS))
            gru_n = len(get_feature_indices(feats, GRU_FEAT_KEYS))
            kan_n = len(get_feature_indices(feats, KAN_FEAT_KEYS))
            
            print(f'{target} H{h}: params={params:,} | '
                  f'CNN={cnn_n}f, GRU={gru_n}f, KAN={kan_n}f | '
                  f'preds={preds.shape}')
