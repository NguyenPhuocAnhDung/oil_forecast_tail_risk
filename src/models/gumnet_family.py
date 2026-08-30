import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional
from src.models.gumnet_het import GUMNetHet, WaveletKANBlock, MultiScaleCNN

class SSMBlock(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.a = nn.Parameter(torch.ones(1, d_model) * 0.9)
        self.b = nn.Parameter(torch.ones(1, d_model) * 0.1)
        self.c = nn.Parameter(torch.ones(1, d_model))
        
    def forward(self, x):
        out = []
        y = torch.zeros_like(x[:, 0])
        for t in range(x.shape[1]):
            y = self.a * y + self.b * x[:, t]
            out.append(y.unsqueeze(1))
        return torch.cat(out, dim=1) * self.c


# 1. GUMNetMamba
class GUMNetMamba(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        gru_dim = len(self.gru_idx)
        self.mamba_proj = nn.Linear(gru_dim, d_feat)
        self.mamba_ssm = SSMBlock(d_feat)
        self.gru = None
        
    def forward(self, x):
        B, L, D = x.shape
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        x_mean = x.mean(dim=1)
        x_std = x.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        f_cnn = self.cnn(x_cnn)
        
        h_gru = self.mamba_proj(x_gru)
        f_gru = self.mamba_ssm(h_gru)[:, -1]
        
        f_kan = self.kan(x_kan)
        
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            w = self.gate(gate_input)
            gates_list.append(w)
            
            f_fused = (w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan)
            pred_h = self.head(f_fused)
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# 2. GUMNetiTrans
class GUMNetiTrans(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        cnn_dim = len(self.cnn_idx)
        self.itrans_embed = nn.Linear(seq_len, d_feat)
        self.itrans_attn = nn.MultiheadAttention(d_feat, 4, batch_first=True)
        self.itrans_proj = nn.Linear(cnn_dim * d_feat, d_feat)
        self.cnn = None
        
    def forward(self, x):
        B, L, D = x.shape
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        x_mean = x.mean(dim=1)
        x_std = x.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        x_cnn_t = x_cnn.transpose(1, 2)
        h_cnn = self.itrans_embed(x_cnn_t)
        attn_out, _ = self.itrans_attn(h_cnn, h_cnn, h_cnn)
        f_cnn = self.itrans_proj(attn_out.reshape(B, -1))
        
        gru_out, _ = self.gru(x_gru)
        f_gru = gru_out[:, -1]
        
        f_kan = self.kan(x_kan)
        
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            w = self.gate(gate_input)
            gates_list.append(w)
            
            f_fused = (w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan)
            pred_h = self.head(f_fused)
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# 3. GUMNetWavelet
class GUMNetWavelet(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        cnn_dim = len(self.cnn_idx)
        gru_dim = len(self.gru_idx)
        self.cnn_kan = WaveletKANBlock(cnn_dim, d_feat)
        self.gru_kan = WaveletKANBlock(gru_dim, d_feat)
        self.cnn = None
        self.gru = None
        
    def forward(self, x):
        B, L, D = x.shape
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        x_mean = x.mean(dim=1)
        x_std = x.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        f_cnn = self.cnn_kan(x_cnn)
        f_gru = self.gru_kan(x_gru)
        f_kan = self.kan(x_kan)
        
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            w = self.gate(gate_input)
            gates_list.append(w)
            
            f_fused = (w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan)
            pred_h = self.head(f_fused)
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# 4. GUMNetPatch
class GUMNetPatch(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        self.patch_size = 5
        self.n_patches = max(1, seq_len // self.patch_size)
        cnn_dim = len(self.cnn_idx)
        self.patch_proj = nn.Linear(self.patch_size * cnn_dim, d_feat)
        self.cnn = MultiScaleCNN(d_feat, d_feat)
        
    def forward(self, x):
        B, L, D = x.shape
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        x_mean = x.mean(dim=1)
        x_std = x.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        cnn_dim = x_cnn.shape[2]
        x_cnn_pad = F.pad(x_cnn.transpose(1, 2), (0, self.n_patches * self.patch_size - L))
        x_cnn_patches = x_cnn_pad.reshape(B, cnn_dim, self.n_patches, self.patch_size).transpose(1, 2).reshape(B, self.n_patches, -1)
        x_cnn_token = self.patch_proj(x_cnn_patches)
        
        f_cnn = self.cnn(x_cnn_token)
        
        gru_out, _ = self.gru(x_gru)
        f_gru = gru_out[:, -1]
        
        f_kan = self.kan(x_kan)
        
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            w = self.gate(gate_input)
            gates_list.append(w)
            
            f_fused = (w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan)
            pred_h = self.head(f_fused)
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# 5. GUMNetFourier
class GUMNetFourier(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        cnn_dim = len(self.cnn_idx)
        self.freq_len = seq_len // 2 + 1
        self.freq_proj = nn.Linear(self.freq_len, d_feat)
        self.cnn = None
        
    def forward(self, x):
        B, L, D = x.shape
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        x_mean = x.mean(dim=1)
        x_std = x.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        x_f = torch.fft.rfft(x_cnn.transpose(1, 2), dim=2)
        f_cnn = self.freq_proj(x_f.real).mean(dim=1) + self.freq_proj(x_f.imag).mean(dim=1)
        
        gru_out, _ = self.gru(x_gru)
        f_gru = gru_out[:, -1]
        
        f_kan = self.kan(x_kan)
        
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            w = self.gate(gate_input)
            gates_list.append(w)
            
            f_fused = (w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan)
            pred_h = self.head(f_fused)
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# 6. GUMNetDiffusion
class GUMNetDiffusion(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        self.noise_model = nn.Sequential(
            nn.Linear(d_feat + output_dim * num_quantiles, d_feat),
            nn.ReLU(),
            nn.Linear(d_feat, output_dim * num_quantiles)
        )
        
    def forward(self, x):
        B, L, D = x.shape
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        x_mean = x.mean(dim=1)
        x_std = x.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        f_cnn = self.cnn(x_cnn)
        gru_out, _ = self.gru(x_gru)
        f_gru = gru_out[:, -1]
        f_kan = self.kan(x_kan)
        
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            w = self.gate(gate_input)
            gates_list.append(w)
            
            f_fused = (w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan)
            
            y_t = torch.randn(B, self.output_dim * self.num_quantiles, device=x.device)
            for t in range(3):
                eps = self.noise_model(torch.cat([f_fused, y_t], dim=-1))
                y_t = y_t - 0.3 * eps
                
            pred_h = y_t.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# 7. GUMNetGraph
class GUMNetGraph(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        self.adj = nn.Parameter(torch.ones(input_dim, input_dim) / input_dim)
        self.gcn_proj = nn.Linear(input_dim, input_dim)
        
    def forward(self, x):
        B, L, D = x.shape
        x_gcn = torch.matmul(x, self.adj)
        x_gcn = torch.relu(self.gcn_proj(x_gcn))
        
        x_cnn = x_gcn[:, :, self.cnn_idx] if self.cnn_idx else x_gcn
        x_gru = x_gcn[:, :, self.gru_idx] if self.gru_idx else x_gcn
        x_kan = x_gcn[:, :, self.kan_idx] if self.kan_idx else x_gcn
        
        x_mean = x_gcn.mean(dim=1)
        x_std = x_gcn.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        f_cnn = self.cnn(x_cnn)
        gru_out, _ = self.gru(x_gru)
        f_gru = gru_out[:, -1]
        f_kan = self.kan(x_kan)
        
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            w = self.gate(gate_input)
            gates_list.append(w)
            
            f_fused = (w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan)
            pred_h = self.head(f_fused)
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# 8. GUMNetRL
class GUMNetRL(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        gate_in_dim = d_feat * 3 + d_feat + 2 * input_dim
        self.gate = nn.Sequential(
            nn.Linear(gate_in_dim, 256),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(256, 3)
        )
        
    def forward(self, x):
        B, L, D = x.shape
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        x_mean = x.mean(dim=1)
        x_std = x.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        f_cnn = self.cnn(x_cnn)
        gru_out, _ = self.gru(x_gru)
        f_gru = gru_out[:, -1]
        f_kan = self.kan(x_kan)
        
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            
            logits = self.gate(gate_input)
            w = torch.softmax(logits, dim=-1)
            gates_list.append(w)
            
            f_fused = (w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan)
            pred_h = self.head(f_fused)
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# 9. GUMNetMoESparse
class GUMNetMoESparse(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None, k: int = 2):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        self.k = k
        
    def forward(self, x):
        B, L, D = x.shape
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        x_mean = x.mean(dim=1)
        x_std = x.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        f_cnn = self.cnn(x_cnn)
        gru_out, _ = self.gru(x_gru)
        f_gru = gru_out[:, -1]
        f_kan = self.kan(x_kan)
        
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            w = self.gate(gate_input)
            
            topk_w, topk_idx = torch.topk(w, self.k, dim=-1)
            topk_w = topk_w / (topk_w.sum(dim=-1, keepdim=True) + 1e-8)
            
            w_sparse = torch.zeros_like(w)
            w_sparse.scatter_(-1, topk_idx, topk_w)
            gates_list.append(w_sparse)
            
            f_fused = (w_sparse[:, 0:1] * f_cnn + w_sparse[:, 1:2] * f_gru + w_sparse[:, 2:3] * f_kan)
            pred_h = self.head(f_fused)
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# 10. GUMNetFusion (Champion)
class GUMNetFusion(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None, temp: float = 0.5):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        self.temp = temp
        
        cnn_dim = len(self.cnn_idx)
        self.itrans_embed = nn.Linear(seq_len, d_feat)
        self.itrans_attn = nn.MultiheadAttention(d_feat, 4, batch_first=True)
        self.itrans_proj = nn.Linear(cnn_dim * d_feat, d_feat)
        self.cnn = None
        
        gru_dim = len(self.gru_idx)
        self.mamba_proj = nn.Linear(gru_dim, d_feat)
        self.mamba_ssm = SSMBlock(d_feat)
        self.gru = None
        
        gate_in_dim = d_feat * 3 + d_feat + 2 * input_dim
        self.gate_logits = nn.Sequential(
            nn.Linear(gate_in_dim, 256),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(256, 3)
        )
        self.gate = None
        
    def forward(self, x):
        B, L, D = x.shape
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        x_mean = x.mean(dim=1)
        x_std = x.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        x_cnn_t = x_cnn.transpose(1, 2)
        h_cnn = self.itrans_embed(x_cnn_t)
        attn_out, _ = self.itrans_attn(h_cnn, h_cnn, h_cnn)
        f_cnn = self.itrans_proj(attn_out.reshape(B, -1))
        
        h_gru = self.mamba_proj(x_gru)
        f_gru = self.mamba_ssm(h_gru)[:, -1]
        
        f_kan = self.kan(x_kan)
        
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            
            logits = self.gate_logits(gate_input) / self.temp
            w = torch.softmax(logits, dim=-1)
            gates_list.append(w)
            
            f_fused = (w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan)
            pred_h = self.head(f_fused)
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# 11. GUMNetDecomp (DLinear Decomposition + GUMNet v3)
class MovingAvgDecomp(nn.Module):
    """Moving Average decomposition block (borrowed from DLinear architecture)."""
    def __init__(self, kernel_size: int):
        super().__init__()
        self.kernel_size = kernel_size
        self.avg = nn.AvgPool1d(kernel_size=kernel_size, stride=1, padding=0)

    def forward(self, x):  # x: [B, L, D]
        front = x[:, :1, :].repeat(1, (self.kernel_size - 1) // 2, 1)
        back  = x[:, -1:, :].repeat(1, self.kernel_size // 2, 1)
        x_pad = torch.cat([front, x, back], dim=1).transpose(1, 2)  # [B, D, L+pad]
        trend = self.avg(x_pad).transpose(1, 2)  # [B, L, D]
        return trend


class GUMNetDecomp(GUMNetHet):
    """
    GUMNetDecomp — DLinear Series Decomposition integrated into GUMNet v3 Expert Routing.
    Innovation: Pre-decomposes input into Trend (BOG-smoothed) and Seasonal+Shock components.
    - GRU Expert receives only the TREND component → learns stable long-run dynamics.
    - CNN + Wavelet-KAN Experts receive only SEASONAL+SHOCK residuals → focus 100% on
      absorbing geopolitical impulses and short-run momentum.
    This solves the Phantom Volatility problem in quiet periods while preserving the
    shock-absorption advantage of Wavelet-KAN in tail-risk windows.
    """
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        kernel_size = min(25, seq_len // 2 * 2 + 1)
        if kernel_size % 2 == 0:
            kernel_size = max(1, kernel_size - 1)
        self.decomp = MovingAvgDecomp(kernel_size)

    def forward(self, x):  # x: [B, L, D]
        B, L, D = x.shape

        # ── 1. DLinear Decomposition ─────────────────────────────────────────
        x_trend    = self.decomp(x)         # Trend (BOG-smoothed): [B, L, D]
        x_seasonal = x - x_trend            # Seasonal + shock residuals: [B, L, D]

        # ── 2. Heterogeneous Expert Routing ──────────────────────────────────
        # GRU: receives stable TREND component only (no GPR noise)
        x_gru = x_trend[:, :, self.gru_idx] if self.gru_idx else x_trend
        # CNN: receives SEASONAL component (short-term momentum / pattern learning)
        x_cnn = x_seasonal[:, :, self.cnn_idx] if self.cnn_idx else x_seasonal
        # Wavelet-KAN: receives SEASONAL component (geopolitical shock absorption)
        x_kan = x_seasonal[:, :, self.kan_idx] if self.kan_idx else x_seasonal

        # Global context from raw input
        x_mean = x.mean(dim=1)
        x_std  = x.std(dim=1)
        x_ctx  = torch.cat([x_mean, x_std], dim=-1)  # [B, 2D]

        # ── 3. Expert Forward Passes ─────────────────────────────────────────
        f_cnn = self.cnn(x_cnn)               # CNN on seasonal
        gru_out, _ = self.gru(x_gru)
        f_gru = gru_out[:, -1]                # GRU on trend
        f_kan = self.kan(x_kan)               # Wavelet-KAN on seasonal/shock

        # ── 4. Horizon-aware Gating and Prediction Head ──────────────────────
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            w = self.gate(gate_input)         # [B, 3] softmax weights
            gates_list.append(w)

            f_fused = w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan
            pred_h  = self.head(f_fused).reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))

        preds = torch.cat(preds, dim=1)       # [B, H, C, Q]
        gates = torch.stack(gates_list, dim=1) # [B, H, 3]
        return preds, gates


# 12. GUMNetAdaptive (VAT-Gate & Adaptive Calibration)
class GUMNetAdaptive(GUMNetHet):
    def __init__(self, seq_len: int = 30, input_dim: int = 16, output_dim: int = 2,
                 horizon: int = 5, d_feat: int = 64, num_quantiles: int = 3,
                 feature_cols: Optional[list] = None):
        super().__init__(seq_len, input_dim, output_dim, horizon, d_feat, num_quantiles, feature_cols)
        
        # Upgraded Inverted Attention Expert (replacing standard CNN)
        cnn_dim = len(self.cnn_idx)
        self.itrans_embed = nn.Linear(seq_len, d_feat)
        self.itrans_attn = nn.MultiheadAttention(d_feat, 4, batch_first=True)
        self.itrans_proj = nn.Linear(cnn_dim * d_feat, d_feat)
        self.cnn = None  # Disable standard CNN
        
        # Redefine gate to output raw logits (Softmax is applied manually with temperature in forward)
        gate_in_dim = d_feat * 3 + d_feat + 2 * input_dim
        self.gate = nn.Sequential(
            nn.Linear(gate_in_dim, 256),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(256, 64),
            nn.GELU(),
            nn.Linear(64, 3)
        )
        
        self.gpr_idx = -1
        self.vol_idx = -1
        if feature_cols is not None:
            if 'GPR' in feature_cols:
                self.gpr_idx = feature_cols.index('GPR')
            if 'Vol_WTI_10d' in feature_cols:
                self.vol_idx = feature_cols.index('Vol_WTI_10d')
                
    def forward(self, x):
        B, L, D = x.shape
        x_cnn = x[:, :, self.cnn_idx] if self.cnn_idx else x
        x_gru = x[:, :, self.gru_idx] if self.gru_idx else x
        x_kan = x[:, :, self.kan_idx] if self.kan_idx else x
        
        x_mean = x.mean(dim=1)
        x_std = x.std(dim=1)
        x_ctx = torch.cat([x_mean, x_std], dim=-1)
        
        # Inverted Attention forwarding (CNN replacement)
        x_cnn_t = x_cnn.transpose(1, 2)  # [B, D_cnn, L]
        h_cnn = self.itrans_embed(x_cnn_t)  # [B, D_cnn, d_feat]
        attn_out, _ = self.itrans_attn(h_cnn, h_cnn, h_cnn)
        f_cnn = self.itrans_proj(attn_out.reshape(B, -1))  # [B, d_feat]
        
        gru_out, _ = self.gru(x_gru)
        f_gru = gru_out[:, -1]
        f_kan = self.kan(x_kan)
        
        # Volatility-Adaptive Temperature scaling
        temp = torch.ones(B, 1, device=x.device)
        if self.gpr_idx != -1:
            gpr_val = x[:, -1, self.gpr_idx]
            temp = temp + 1.5 * torch.log10(1.0 + torch.clamp(gpr_val, min=0.0) / 100.0).unsqueeze(-1)
        if self.vol_idx != -1:
            vol_val = x[:, -1, self.vol_idx]
            temp = temp + 2.0 * torch.clamp(vol_val, min=0.0).unsqueeze(-1)
            
        # Target price volatility adaptive scaling (index 0 of x_std is target petroleum product)
        target_vol = x_std[:, 0].unsqueeze(-1)
        temp = temp + 1.5 * torch.clamp(target_vol, min=0.0)
            
        preds, gates_list = [], []
        for h_idx in range(self.horizon):
            pos = self.pos_embed(torch.tensor([h_idx], device=x.device)).expand(B, -1)
            gate_input = torch.cat([f_cnn, f_gru, f_kan, pos, x_ctx], dim=-1)
            
            logits = self.gate(gate_input)
            w = F.softmax(logits / temp, dim=-1)
            gates_list.append(w)
            
            f_fused = (w[:, 0:1] * f_cnn + w[:, 1:2] * f_gru + w[:, 2:3] * f_kan)
            pred_h = self.head(f_fused)
            
            pred_h = pred_h.reshape(B, self.output_dim, self.num_quantiles)
            preds.append(pred_h.unsqueeze(1))
            
        preds = torch.cat(preds, dim=1)
        gates = torch.stack(gates_list, dim=1)
        return preds, gates


# Registry of GUMNet Family
GUMNET_FAMILY_REGISTRY = {
    "GUMNet_Mamba":     GUMNetMamba,
    "GUMNet_iTrans":    GUMNetiTrans,
    "GUMNet_Wavelet":   GUMNetWavelet,
    "GUMNet_Patch":     GUMNetPatch,
    "GUMNet_Fourier":   GUMNetFourier,
    "GUMNet_Diffusion": GUMNetDiffusion,
    "GUMNet_Graph":     GUMNetGraph,
    "GUMNet_RL":        GUMNetRL,
    "GUMNet_MoE_Sparse":GUMNetMoESparse,
    "GUMNet_Fusion":    GUMNetFusion,
    "GUMNet_Decomp":    GUMNetDecomp,
    "GUMNet_Adaptive":  GUMNetAdaptive,
}
