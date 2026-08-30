import torch
import torch.nn as nn
import torch.nn.functional as F

class MovingAvg(nn.Module):
    def __init__(self, kernel_size: int):
        super().__init__()
        self.kernel_size = kernel_size
        self.avg = nn.AvgPool1d(kernel_size=kernel_size, stride=1, padding=0)
  
    def forward(self, x):
        front = x[:, :1, :].repeat(1, (self.kernel_size - 1) // 2, 1)
        back = x[:, -1:, :].repeat(1, self.kernel_size // 2, 1)
        x = torch.cat([front, x, back], dim=1)
        x = x.transpose(1, 2)
        x = self.avg(x)
        return x.transpose(1, 2)


class SSMBlock(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.a = nn.Parameter(torch.ones(1, d_model) * 0.9)
        self.b = nn.Parameter(torch.ones(1, d_model) * 0.1)
        self.c = nn.Parameter(torch.ones(1, d_model))
        
    def forward(self, x):
        # Scan-like operation: y_t = a*y_{t-1} + b*x_t
        out = []
        y = torch.zeros_like(x[:, 0])
        for t in range(x.shape[1]):
            y = self.a * y + self.b * x[:, t]
            out.append(y.unsqueeze(1))
        return torch.cat(out, dim=1) * self.c


# 1. RLinear
class RLinear(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        self.linear = nn.Linear(seq_len, horizon)
        self.projector = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mean = x.mean(dim=1, keepdim=True)
        stdev = torch.sqrt(x.var(dim=1, keepdim=True, unbiased=False) + 1e-5)
        x_norm = (x - mean) / stdev
        
        x_trans = x_norm.transpose(1, 2)
        out_time = self.linear(x_trans).transpose(1, 2)
        
        stdev_tgt = self.projector(stdev[:, 0, :]).unsqueeze(1)
        mean_tgt = self.projector(mean[:, 0, :]).unsqueeze(1)
        
        out = self.projector(out_time)
        out = out * stdev_tgt + mean_tgt
        return out


# 2. LTSF_Linear
class LTSF_Linear(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.linear = nn.Linear(seq_len, horizon)
        self.projection = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x_t = x.transpose(1, 2)
        out = self.linear(x_t).transpose(1, 2)
        return self.projection(out)


# 3. NBEATS
class NBEATSBlock(nn.Module):
    def __init__(self, seq_len: int, input_dim: int, horizon: int, output_dim: int, d_model: int = 64):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(seq_len * input_dim, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model),
            nn.ReLU(),
        )
        self.basis_coef_b = nn.Linear(d_model, seq_len * input_dim)
        self.basis_coef_f = nn.Linear(d_model, horizon * output_dim)
        self.horizon = horizon
        self.output_dim = output_dim
        
    def forward(self, x: torch.Tensor) -> tuple:
        B, L, D = x.shape
        h = self.fc(x.reshape(B, -1))
        backcast = self.basis_coef_b(h).reshape(B, L, D)
        forecast = self.basis_coef_f(h).reshape(B, self.horizon, self.output_dim)
        return backcast, forecast

class NBEATS(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.blocks = nn.ModuleList([
            NBEATSBlock(seq_len, input_dim, horizon, output_dim) for _ in range(3)
        ])
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        res = x
        forecast_total = 0
        for block in self.blocks:
            backcast, forecast = block(res)
            res = res - backcast
            forecast_total = forecast_total + forecast
        return forecast_total


# 4. Autoformer
class AutoCorrelation(nn.Module):
    def __init__(self, d_model: int, n_heads: int = 4):
        super().__init__()
        self.n_heads = n_heads
        
    def forward(self, q, k, v):
        B, L, d_model = q.shape
        q_fft = torch.fft.rfft(q, dim=1)
        k_fft = torch.fft.rfft(k, dim=1)
        res = q_fft * torch.conj(k_fft)
        corr = torch.fft.irfft(res, n=L, dim=1)
        w = torch.softmax(corr, dim=1)
        out = w * v
        return out

class Autoformer(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        self.embed = nn.Linear(input_dim, 64)
        self.decomp = MovingAvg(kernel_size=min(25, seq_len // 2 * 2 + 1))
        self.corr = AutoCorrelation(64)
        self.linear = nn.Linear(seq_len, horizon)
        self.proj = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        trend = self.decomp(x)
        seasonal = x - trend
        
        s_embed = self.embed(seasonal)
        t_embed = self.embed(trend)
        
        s_corr = self.corr(s_embed, s_embed, s_embed)
        
        s_out = self.proj(self.linear(s_corr.transpose(1, 2)).transpose(1, 2))
        t_out = self.proj(self.linear(t_embed.transpose(1, 2)).transpose(1, 2))
        return s_out + t_out


# 5. FedFormer
class FourierAttention(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.linear = nn.Linear(d_model, d_model)
        
    def forward(self, q, k, v):
        q_f = torch.fft.rfft(q, dim=1)
        k_f = torch.fft.rfft(k, dim=1)
        out_f = q_f * torch.conj(k_f)
        out_r = self.linear(out_f.real)
        out_i = self.linear(out_f.imag)
        out_f_new = torch.complex(out_r, out_i)
        out = torch.fft.irfft(out_f_new, n=q.shape[1], dim=1)
        return out + v

class FedFormer(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.embed = nn.Linear(input_dim, 64)
        self.decomp = MovingAvg(kernel_size=min(25, seq_len // 2 * 2 + 1))
        self.fea = FourierAttention(64)
        self.linear = nn.Linear(seq_len, horizon)
        self.proj = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        trend = self.decomp(x)
        seasonal = x - trend
        s_embed = self.embed(seasonal)
        t_embed = self.embed(trend)
        
        s_attn = self.fea(s_embed, s_embed, s_embed)
        s_out = self.proj(self.linear(s_attn.transpose(1, 2)).transpose(1, 2))
        t_out = self.proj(self.linear(t_embed.transpose(1, 2)).transpose(1, 2))
        return s_out + t_out


# 6. Informer
class Informer(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.embed = nn.Linear(input_dim, 64)
        self.attn = nn.MultiheadAttention(64, 4, batch_first=True)
        self.linear = nn.Linear(seq_len, horizon)
        self.proj = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x)
        attn_out, _ = self.attn(h, h, h)
        out = self.linear(attn_out.transpose(1, 2)).transpose(1, 2)
        return self.proj(out)


# 7. Reformer
class LSHAttention(nn.Module):
    def __init__(self, d_model: int, n_buckets: int = 4):
        super().__init__()
        self.n_buckets = n_buckets
        self.proj = nn.Linear(d_model, n_buckets)
        
    def forward(self, q, k, v):
        B, L, D = q.shape
        buckets = torch.argmax(self.proj(q), dim=-1)
        mask = (buckets.unsqueeze(1) == buckets.unsqueeze(2)).float()
        scores = torch.matmul(q, k.transpose(1, 2)) / (D ** 0.5)
        scores = scores.masked_fill(mask == 0, -1e9)
        attn = torch.softmax(scores, dim=-1)
        attn = torch.nan_to_num(attn, 0.0)
        return torch.matmul(attn, v)

class Reformer(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.embed = nn.Linear(input_dim, 64)
        self.lsh_attn = LSHAttention(64)
        self.linear = nn.Linear(seq_len, horizon)
        self.proj = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x)
        h_attn = self.lsh_attn(h, h, h)
        out = self.linear(h_attn.transpose(1, 2)).transpose(1, 2)
        return self.proj(out)


# 8. UniTS
class UniTS(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        self.seq_embed = nn.Linear(seq_len, 64)
        self.channel_embed = nn.Linear(input_dim, 64)
        self.mix = nn.Sequential(
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64)
        )
        self.predict_head = nn.Linear(64, horizon * output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x_seq = self.seq_embed(x.transpose(1, 2))
        x_chan = self.channel_embed(x)
        
        feat = torch.cat([x_seq.mean(dim=1), x_chan.mean(dim=1)], dim=-1)
        out = self.mix(feat)
        pred = self.predict_head(out)
        return pred.reshape(B, self.horizon, self.output_dim)


# 9. TimeXer
class TimeXer(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.feature_embed = nn.Linear(seq_len, 64)
        self.temporal_embed = nn.Linear(input_dim, 64)
        self.cross_attn = nn.MultiheadAttention(64, 4, batch_first=True)
        self.fc = nn.Linear(seq_len, horizon)
        self.projection = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        var_tokens = self.feature_embed(x.transpose(1, 2))
        time_tokens = self.temporal_embed(x)
        
        out, _ = self.cross_attn(time_tokens, var_tokens, var_tokens)
        pred = self.fc(out.transpose(1, 2)).transpose(1, 2)
        return self.projection(pred)


# 10. Crossformer
class Crossformer(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.seg_len = 5
        self.n_segs = max(1, seq_len // self.seg_len)
        self.dsw_proj = nn.Linear(self.seg_len, 64)
        self.time_attn = nn.MultiheadAttention(64, 2, batch_first=True)
        self.dim_attn = nn.MultiheadAttention(64, 2, batch_first=True)
        self.fc = nn.Linear(self.n_segs * 64, horizon)
        self.proj = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x_pad = F.pad(x.transpose(1, 2), (0, self.n_segs * self.seg_len - L))
        x_segs = x_pad.reshape(B, D, self.n_segs, self.seg_len)
        
        emb = self.dsw_proj(x_segs)
        
        emb_time = emb.reshape(B * D, self.n_segs, 64)
        time_out, _ = self.time_attn(emb_time, emb_time, emb_time)
        time_out = time_out.reshape(B, D, self.n_segs, 64)
        
        emb_dim = time_out.transpose(1, 2).reshape(B * self.n_segs, D, 64)
        dim_out, _ = self.dim_attn(emb_dim, emb_dim, emb_dim)
        dim_out = dim_out.reshape(B, self.n_segs, D, 64).transpose(1, 2)
        
        out = self.fc(dim_out.reshape(B, D, -1))
        return self.proj(out.transpose(1, 2))


# 11. CARD
class CARD(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        self.backbone = nn.Sequential(
            nn.Linear(seq_len * input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU()
        )
        self.noise_net = nn.Sequential(
            nn.Linear(64 + horizon * output_dim, 128),
            nn.ReLU(),
            nn.Linear(128, horizon * output_dim)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        cond = self.backbone(x.reshape(B, -1))
        
        y_t = torch.zeros(B, self.horizon * self.output_dim, device=x.device)
        for _ in range(3):
            eps = self.noise_net(torch.cat([cond, y_t], dim=-1))
            y_t = y_t + eps * 0.3
            
        return y_t.reshape(B, self.horizon, self.output_dim)


# 12. FITS
class FITS(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        
        self.cut_freq = min(10, seq_len // 2)
        self.cut_freq_out = min(10, horizon // 2)
        if self.cut_freq_out == 0:
            self.cut_freq_out = 1
            
        self.fc_r = nn.Linear(self.cut_freq + 1, self.cut_freq_out + 1)
        self.fc_i = nn.Linear(self.cut_freq + 1, self.cut_freq_out + 1)
        self.proj = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x_f = torch.fft.rfft(x, dim=1)
        
        x_f_low = x_f[:, :self.cut_freq + 1, :]
        
        out_r = self.fc_r(x_f_low.real.transpose(1, 2)).transpose(1, 2)
        out_i = self.fc_i(x_f_low.imag.transpose(1, 2)).transpose(1, 2)
        out_f = torch.complex(out_r, out_i)
        
        tgt_f_len = self.horizon // 2 + 1
        out_f_pad = F.pad(out_f, (0, 0, 0, max(0, tgt_f_len - out_f.shape[1])))[:, :tgt_f_len, :]
        
        out = torch.fft.irfft(out_f_pad, n=self.horizon, dim=1)
        return self.proj(out)


# 13. CoST
class CoST(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.embed = nn.Linear(input_dim, 64)
        self.trend_conv = nn.Conv1d(64, 64, kernel_size=3, padding=1)
        self.seasonal_embed = nn.Linear(seq_len, 64)
        self.linear_t = nn.Linear(seq_len, horizon)
        self.linear_s = nn.Linear(64, horizon)
        self.proj = nn.Linear(128, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x) # [B, L, 64]
        
        trend_feat = torch.relu(self.trend_conv(h.transpose(1, 2))) # [B, 64, L]
        trend_out = self.linear_t(trend_feat).transpose(1, 2) # [B, H, 64]
        
        seasonal_feat = self.seasonal_embed(h.transpose(1, 2)).transpose(1, 2) # [B, 64, 64]
        seasonal_out = self.linear_s(seasonal_feat.transpose(1, 2)).transpose(1, 2) # [B, H, 64]
        
        fused = torch.cat([trend_out, seasonal_out], dim=-1) # [B, H, 128]
        return self.proj(fused)


# 14. TTM
class TTM(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.patch_size = 5
        self.n_patches = max(1, seq_len // self.patch_size)
        self.fc_in = nn.Linear(self.patch_size, 32)
        self.patch_mix = nn.Linear(self.n_patches, self.n_patches)
        self.feat_mix = nn.Linear(32, 32)
        self.fc_out = nn.Linear(self.n_patches * 32, horizon)
        self.proj = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x_pad = F.pad(x.transpose(1, 2), (0, self.n_patches * self.patch_size - L))
        patches = x_pad.reshape(B * D, self.n_patches, self.patch_size)
        
        emb = torch.relu(self.fc_in(patches))
        emb = emb + torch.relu(self.patch_mix(emb.transpose(1, 2)).transpose(1, 2))
        emb = emb + torch.relu(self.feat_mix(emb))
        
        out = self.fc_out(emb.reshape(B * D, -1))
        out = out.reshape(B, D, -1).transpose(1, 2)
        return self.proj(out)


# 15. TimeMachine
class TimeMachine(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.embed = nn.Linear(input_dim, 64)
        self.ssm_time = SSMBlock(64)
        self.ssm_chan = SSMBlock(seq_len)
        self.linear = nn.Linear(seq_len, horizon)
        self.proj = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x)
        h_t = self.ssm_time(h)
        h_c = self.ssm_chan(h_t.transpose(1, 2)).transpose(1, 2)
        out = self.linear(h_c.transpose(1, 2)).transpose(1, 2)
        return self.proj(out)


# 16. S_Mamba
class S_Mamba(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.embed = nn.Linear(input_dim, 64)
        self.ssm = SSMBlock(64)
        self.linear = nn.Linear(seq_len, horizon)
        self.proj = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x)
        h_ssm = self.ssm(h)
        out = self.linear(h_ssm.transpose(1, 2)).transpose(1, 2)
        return self.proj(out)


# 17. MambaFormer
class MambaFormer(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.embed = nn.Linear(input_dim, 64)
        self.ssm = SSMBlock(64)
        self.attn = nn.MultiheadAttention(64, 2, batch_first=True)
        self.linear = nn.Linear(seq_len, horizon)
        self.proj = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x)
        h = self.ssm(h) + h
        attn_out, _ = self.attn(h, h, h)
        h = attn_out + h
        out = self.linear(h.transpose(1, 2)).transpose(1, 2)
        return self.proj(out)


# 18. BiMamba
class BiSSMBlock(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.fwd_ssm = SSMBlock(d_model)
        self.bwd_ssm = SSMBlock(d_model)
        
    def forward(self, x):
        fwd_out = self.fwd_ssm(x)
        x_flip = torch.flip(x, dims=[1])
        bwd_out = torch.flip(self.bwd_ssm(x_flip), dims=[1])
        return fwd_out + bwd_out

class BiMamba(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.embed = nn.Linear(input_dim, 64)
        self.bi_ssm = BiSSMBlock(64)
        self.linear = nn.Linear(seq_len, horizon)
        self.proj = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x)
        h_ssm = self.bi_ssm(h)
        out = self.linear(h_ssm.transpose(1, 2)).transpose(1, 2)
        return self.proj(out)


# 19. Time_MoE
class Time_MoE(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        self.experts = nn.ModuleList([
            nn.Linear(seq_len, horizon) for _ in range(3)
        ])
        self.gate = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 3),
            nn.Softmax(dim=-1)
        )
        self.proj = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mean_feat = x.mean(dim=1)
        weights = self.gate(mean_feat)
        
        x_t = x.transpose(1, 2)
        exp_outs = [exp(x_t).transpose(1, 2) for exp in self.experts]
        
        fused = 0
        for idx, out in enumerate(exp_outs):
            fused = fused + weights[:, idx].view(-1, 1, 1) * out
            
        return self.proj(fused)


# 20. Gated_TabNet
class Gated_TabNet(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.gate = nn.Sequential(
            nn.Linear(input_dim, input_dim),
            nn.Sigmoid()
        )
        self.fc = nn.Linear(seq_len * input_dim, horizon * output_dim)
        self.horizon = horizon
        self.output_dim = output_dim
        
        self.register_parameter('dummy', nn.Parameter(torch.zeros(1)))
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mask = self.gate(x.mean(dim=1, keepdim=True))
        x_gated = x * mask
        pred = self.fc(x_gated.reshape(x.shape[0], -1))
        return pred.reshape(x.shape[0], self.horizon, self.output_dim)


# 21. Chronos
class Chronos(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.seq_len = seq_len
        self.horizon = horizon
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        self.tokenizer_proj = nn.Linear(seq_len, 256)
        self.t5_sim = nn.Sequential(
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, horizon)
        )
        self.proj = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x_t = x.transpose(1, 2)
        tokens = torch.softmax(self.tokenizer_proj(x_t), dim=-1)
        out_time = self.t5_sim(tokens)
        return self.proj(out_time.transpose(1, 2))


# 22. TimesFM
class TimesFM(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.patch_size = min(32, seq_len)
        self.n_patches = max(1, seq_len // self.patch_size)
        self.patch_proj = nn.Linear(self.patch_size, 64)
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=64, nhead=2, batch_first=True),
            num_layers=1
        )
        self.head = nn.Linear(self.n_patches * 64, horizon)
        self.proj = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x_pad = F.pad(x.transpose(1, 2), (0, self.n_patches * self.patch_size - L))
        patches = x_pad.reshape(B * D, self.n_patches, self.patch_size)
        
        emb = self.patch_proj(patches)
        h = self.transformer(emb)
        out_time = self.head(h.reshape(B * D, -1))
        out = out_time.reshape(B, D, -1).transpose(1, 2)
        return self.proj(out)


# 23. Moirai
class Moirai(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.p1, self.p2 = 8, 16
        self.n1 = max(1, seq_len // self.p1)
        self.n2 = max(1, seq_len // self.p2)
        
        self.proj1 = nn.Linear(self.p1, 32)
        self.proj2 = nn.Linear(self.p2, 32)
        
        self.attn = nn.MultiheadAttention(64, 2, batch_first=True)
        self.head = nn.Linear(64, horizon)
        self.proj = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x1 = F.pad(x.transpose(1, 2), (0, self.n1 * self.p1 - L)).reshape(B * D, self.n1, self.p1)
        x2 = F.pad(x.transpose(1, 2), (0, self.n2 * self.p2 - L)).reshape(B * D, self.n2, self.p2)
        
        emb1 = self.proj1(x1).mean(dim=1, keepdim=True)
        emb2 = self.proj2(x2).mean(dim=1, keepdim=True)
        
        emb = torch.cat([emb1, emb2], dim=-1)
        out_time, _ = self.attn(emb, emb, emb)
        out_time = self.head(out_time.squeeze(1))
        
        out = out_time.reshape(B, D, -1).transpose(1, 2)
        return self.proj(out)


# 24. Lag_Llama
class Lag_Llama(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.lags = [1, 2, 3, 5, 10]
        self.embed = nn.Linear(len(self.lags) * input_dim, 64)
        self.llama_layers = nn.Sequential(
            nn.Linear(64, 64),
            nn.SiLU(),
            nn.Linear(64, 64)
        )
        self.linear = nn.Linear(seq_len, horizon)
        self.proj = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        lag_feats = []
        for lag in self.lags:
            feat = torch.cat([x[:, :lag].repeat(1, 1, 1)[:, :lag], x[:, :-lag]], dim=1) if lag < L else x
            lag_feats.append(feat)
        x_lags = torch.cat(lag_feats, dim=-1)
        h = self.embed(x_lags)
        h = self.llama_layers(h)
        out = self.linear(h.transpose(1, 2)).transpose(1, 2)
        return self.proj(out)


# 25. TEMPO
class TEMPO(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.prompts = nn.Parameter(torch.randn(5, 64))
        self.embed = nn.Linear(input_dim, 64)
        self.decomp = MovingAvg(kernel_size=min(25, seq_len // 2 * 2 + 1))
        
        self.linear_t = nn.Linear(seq_len, horizon)
        self.linear_s = nn.Linear(seq_len, horizon)
        self.proj = nn.Linear(64, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        trend = self.decomp(x)
        seasonal = x - trend
        
        s_emb = self.embed(seasonal)
        sim = torch.matmul(s_emb.mean(dim=1), self.prompts.T)
        weights = torch.softmax(sim, dim=-1)
        matched_prompt = torch.matmul(weights, self.prompts).unsqueeze(1)
        
        s_emb = s_emb + matched_prompt
        
        s_out = self.proj(self.linear_s(s_emb.transpose(1, 2)).transpose(1, 2))
        t_out = self.proj(self.linear_t(self.embed(trend).transpose(1, 2)).transpose(1, 2))
        return s_out + t_out


# 26. GPT4TS
class GPT4TS(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int, **kwargs):
        super().__init__()
        self.patch_size = 4
        self.n_patches = max(1, seq_len // self.patch_size)
        self.embed = nn.Linear(self.patch_size, 64)
        
        self.gpt_attn = nn.MultiheadAttention(64, 4, batch_first=True)
        self.gpt_mlp = nn.Sequential(
            nn.Linear(64, 128),
            nn.GELU(),
            nn.Linear(128, 64)
        )
        self.head = nn.Linear(self.n_patches * 64, horizon)
        self.proj = nn.Linear(input_dim, output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, D = x.shape
        x_pad = F.pad(x.transpose(1, 2), (0, self.n_patches * self.patch_size - L))
        patches = x_pad.reshape(B * D, self.n_patches, self.patch_size)
        
        h = self.embed(patches)
        h_attn, _ = self.gpt_attn(h, h, h)
        h = h + h_attn
        h = h + self.gpt_mlp(h)
        
        out_time = self.head(h.reshape(B * D, -1))
        out = out_time.reshape(B, D, -1).transpose(1, 2)
        return self.proj(out)


# Registry of SOTA models
SOTA_CLASS_REGISTRY = {
    "RLinear": RLinear,
    "LTSF_Linear": LTSF_Linear,
    "NBEATS": NBEATS,
    "Autoformer": Autoformer,
    "FedFormer": FedFormer,
    "Informer": Informer,
    "Reformer": Reformer,
    "UniTS": UniTS,
    "TimeXer": TimeXer,
    "Crossformer": Crossformer,
    "CARD": CARD,
    "FITS": FITS,
    "CoST": CoST,
    "TTM": TTM,
    "TimeMachine": TimeMachine,
    "S_Mamba": S_Mamba,
    "MambaFormer": MambaFormer,
    "BiMamba": BiMamba,
    "Time_MoE": Time_MoE,
    "Gated_TabNet": Gated_TabNet,
    "Chronos": Chronos,
    "TimesFM": TimesFM,
    "Moirai": Moirai,
    "Lag_Llama": Lag_Llama,
    "TEMPO": TEMPO,
    "GPT4TS": GPT4TS,
}
