import torch
import torch.nn as nn
import torch.nn.functional as F

class TimesNet(nn.Module):
    """
    TimesNet (ICLR 2023) - Simplified, lightweight, and shape-robust version.
    Converts 1D time series into 2D variations based on estimated periods.
    """
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, d_model: int = 32, k: int = 3):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.k = k
        self.d_model = d_model
        
        self.token_embed = nn.Linear(input_dim, d_model)
        self.conv = nn.Sequential(
            nn.Conv2d(d_model, d_model, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(d_model, d_model, kernel_size=3, padding=1)
        )
        self.predict_head = nn.Linear(seq_len * d_model, horizon * output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x_embed = self.token_embed(x) # [B, L, d_model]
        
        # FFT to estimate period lengths
        try:
            xf = torch.fft.rfft(x_embed, dim=1)
            amplitudes = torch.mean(torch.abs(xf), dim=(0, 2))
            amplitudes[0] = 0
            k_val = min(self.k, len(amplitudes) - 1)
            if k_val > 0:
                _, topk_indices = torch.topk(amplitudes, k_val)
                periods = [L // idx.item() for idx in topk_indices if idx.item() > 0]
            else:
                periods = []
        except Exception:
            periods = []
            
        periods = [p for p in periods if p > 1 and p < L]
        if not periods:
            periods = [2, 3, 5]  # Fallback
            
        out_fused = torch.zeros_like(x_embed)
        for p in periods:
            if L % p != 0:
                pad_len = p - (L % p)
                x_padded = F.pad(x_embed, (0, 0, 0, pad_len))
            else:
                pad_len = 0
                x_padded = x_embed
                
            padded_L = L + pad_len
            # Reshape 1D sequence to 2D tensor: [B, C, H, W]
            x_2d = x_padded.transpose(1, 2).reshape(B, self.d_model, p, padded_L // p)
            conv_out = self.conv(x_2d)
            conv_1d = conv_out.reshape(B, self.d_model, padded_L).transpose(1, 2)
            out_fused += conv_1d[:, :L, :] / len(periods)
            
        out_flat = out_fused.reshape(B, -1)
        pred = self.predict_head(out_flat)
        return pred.view(B, self.horizon, self.output_dim)


class iTransformer(nn.Module):
    """
    iTransformer (ICLR 2024) - Inverted Transformer.
    Embeds each individual feature time series as a token, and encodes them.
    """
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, d_model: int = 32, nhead: int = 4, num_layers: int = 2):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        self.feature_embed = nn.Linear(seq_len, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=d_model * 2,
            batch_first=True, dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.predict_head = nn.Linear(d_model, horizon)
        self.channel_projection = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x_trans = x.transpose(1, 2) # [B, D, L]
        x_embed = self.feature_embed(x_trans) # [B, D, d_model]
        x_enc = self.transformer(x_embed) # [B, D, d_model]
        out = self.predict_head(x_enc) # [B, D, horizon]
        out = out.transpose(1, 2) # [B, horizon, D]
        return self.channel_projection(out)


class TimeMixer(nn.Module):
    """
    TimeMixer (ICLR 2025) - Multi-scale mixing network.
    Aggregates downsampled, multi-resolution temporal features.
    """
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, d_model: int = 32):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.token_embed = nn.Linear(input_dim, d_model)
        
        self.len0 = seq_len
        self.k1 = min(2, seq_len)
        self.len1 = max(1, seq_len // self.k1)
        self.k2 = min(4, seq_len)
        self.len2 = max(1, seq_len // self.k2)
        
        self.mix0 = nn.Linear(self.len0, self.len0)
        self.mix1 = nn.Linear(self.len1, self.len1)
        self.mix2 = nn.Linear(self.len2, self.len2)
        
        self.predict_head = nn.Linear(seq_len * d_model, horizon * output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x_embed = self.token_embed(x)
        
        # Scale 0 mixing
        x0 = x_embed
        mix0_out = self.mix0(x0.transpose(1, 2)).transpose(1, 2)
        
        # Scale 1 mixing
        x1 = F.avg_pool1d(x_embed.transpose(1, 2), kernel_size=self.k1, stride=self.k1).transpose(1, 2)
        if x1.shape[1] > self.len1:
            x1 = x1[:, :self.len1, :]
        elif x1.shape[1] < self.len1:
            x1 = F.pad(x1, (0, 0, 0, self.len1 - x1.shape[1]))
        mix1_out = self.mix1(x1.transpose(1, 2)).transpose(1, 2)
        
        # Scale 2 mixing
        x2 = F.avg_pool1d(x_embed.transpose(1, 2), kernel_size=self.k2, stride=self.k2).transpose(1, 2)
        if x2.shape[1] > self.len2:
            x2 = x2[:, :self.len2, :]
        elif x2.shape[1] < self.len2:
            x2 = F.pad(x2, (0, 0, 0, self.len2 - x2.shape[1]))
        mix2_out = self.mix2(x2.transpose(1, 2)).transpose(1, 2)
        
        # Cross-scale Fusion
        mix1_up = F.interpolate(mix1_out.transpose(1, 2), size=L, mode='linear', align_corners=False).transpose(1, 2)
        mix2_up = F.interpolate(mix2_out.transpose(1, 2), size=L, mode='linear', align_corners=False).transpose(1, 2)
        
        fused = mix0_out + mix1_up + mix2_up
        pred = self.predict_head(fused.reshape(B, -1))
        return pred.view(B, self.horizon, self.output_dim)


class GRN(nn.Module):
    """Gated Residual Network helper block for TFT."""
    def __init__(self, in_dim: int, out_dim: int):
        super().__init__()
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.linear1 = nn.Linear(in_dim, out_dim)
        self.linear2 = nn.Linear(out_dim, out_dim)
        self.gate = nn.Linear(in_dim, out_dim)
        self.layernorm = nn.LayerNorm(out_dim)
        if in_dim != out_dim:
            self.project = nn.Linear(in_dim, out_dim)
        else:
            self.project = nn.Identity()
            
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = F.elu(self.linear1(x))
        h = self.linear2(h)
        g = torch.sigmoid(self.gate(x))
        return self.layernorm(self.project(x) + g * h)


class SimplifiedTFT(nn.Module):
    """
    Temporal Fusion Transformer (TFT) - Simplified PyTorch version.
    Utilizes GRN feature selection gating and Multihead temporal self-attention.
    """
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, d_model: int = 32, nhead: int = 4):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        self.input_grn = GRN(input_dim, d_model)
        self.attn = nn.MultiheadAttention(embed_dim=d_model, num_heads=nhead, batch_first=True)
        self.post_grn = GRN(d_model, d_model)
        self.predict_head = nn.Linear(seq_len * d_model, horizon * output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x_embed = self.input_grn(x)
        attn_out, _ = self.attn(x_embed, x_embed, x_embed)
        fused = self.post_grn(attn_out + x_embed)
        pred = self.predict_head(fused.reshape(B, -1))
        return pred.view(B, self.horizon, self.output_dim)


class NHitsBlock(nn.Module):
    """NHits individual hierarchical block."""
    def __init__(self, input_len: int, input_dim: int, horizon: int, output_dim: int, pool_size: int, d_model: int = 32):
        super().__init__()
        self.pool_size = pool_size
        self.input_len = input_len
        self.input_dim = input_dim
        self.horizon = horizon
        self.output_dim = output_dim
        
        self.pool = nn.AvgPool1d(kernel_size=pool_size, stride=pool_size)
        pooled_len = max(1, input_len // pool_size)
        
        self.mlp = nn.Sequential(
            nn.Linear(pooled_len * input_dim, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model),
            nn.ReLU()
        )
        self.fc_forecast = nn.Linear(d_model, horizon * output_dim)
        self.fc_backcast = nn.Linear(d_model, input_len * input_dim)
        
    def forward(self, x: torch.Tensor) -> tuple:
        B, L, D = x.shape
        x_t = x.transpose(1, 2)
        if L >= self.pool_size:
            pooled = self.pool(x_t)
        else:
            pooled = F.avg_pool1d(x_t, kernel_size=L)
            
        pooled = pooled.transpose(1, 2)
        feat = self.mlp(pooled.reshape(B, -1))
        forecast = self.fc_forecast(feat).view(B, self.horizon, self.output_dim)
        backcast = self.fc_backcast(feat).view(B, L, D)
        return backcast, forecast


class SimplifiedNHits(nn.Module):
    """
    N-HiTS - Simplified PyTorch version.
    Performs hierarchical multi-rate temporal pooling and residual projections.
    """
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, d_model: int = 32):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        self.blocks = nn.ModuleList([
            NHitsBlock(seq_len, input_dim, horizon, output_dim, pool_size=4, d_model=d_model),
            NHitsBlock(seq_len, input_dim, horizon, output_dim, pool_size=2, d_model=d_model),
            NHitsBlock(seq_len, input_dim, horizon, output_dim, pool_size=1, d_model=d_model)
        ])
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        y_pred = torch.zeros(B, self.horizon, self.output_dim, device=x.device)
        res = x
        for block in self.blocks:
            backcast, forecast = block(res)
            res = res - backcast
            y_pred += forecast
        return y_pred
