## Forensic Audit Report

**Work Product**: Milestone C Academic Reports (`docs/research_os/`) and Codebase (`config.py`, `src/models/gumnet_family.py`, `tests/test_dispatch.py`)
**Profile**: General Project
**Verdict**: CLEAN

### Phase Results
- **Hardcoded output detection**: PASS — No hardcoded empirical metrics or simulated results were found in the five updated reports (`stage2_conceptual_gaps.md`, `stage5_hypothesis_design.md`, `stage7_baseline_taxonomy.md`, `stage9_failure_diagnostics.md`, `stage10_econometric_validation.md`). All parameters in formulas are algebraic variables.
- **Facade detection**: PASS — The 10 GUM-Net family variants in `src/models/gumnet_family.py` and the 33 baseline architectures in `src/models/sota_baselines.py` / `src/models/extended_sota.py` are implemented using genuine PyTorch structures (e.g. multi-scale CNN, multihead attention, SSMBlock, WaveletKANBlock). No facade implementations returning constant/mock values were found.
- **Pre-populated artifact detection**: PASS — Results under `results_v4/` are genuine and match the execution metadata on hostname `QUIN` from the current iterations. No fabricated logs exist.
- **Verbatim R8 Clause Verification**: PASS — The R8 scientific integrity clause is integrated verbatim in `docs/research_os/stage7_baseline_taxonomy.md` at line 32:
  `> **"Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu."**`
- **Dispatch Registry and GUM-Net Configuration Authenticity**: PASS — The 33 SOTA models and 11 GUM-Net variants are authentically configured in `config.py` and dynamically loaded through the model dispatcher `get_model_instance` in `scripts/train_unified.py`.
- **Behavioral Verification**: PASS — The unit test script `tests/test_dispatch.py` executes real forward passes on randomized tensors to verify structural and shape consistency.

### Evidence

#### 1. Verbatim R8 Clause Grep Search Results
```json
{
  "File": "/data/quyhv/oil_forecast_tail_risk/docs/research_os/stage7_baseline_taxonomy.md",
  "LineNumber": 32,
  "LineContent": "> **\"Nếu kết quả 10 seeds chỉ ra rằng Time_MoE, TimesFM hay S_Mamba đạt Worst-case tốt hơn GUM-Net trên unified_data.csv, hệ thống ghi nhận trung thực 100% số liệu.\"**"
}
```

#### 2. Model Dispatch Registry (from config.py)
```python
SOTA_TAXONOMY_REGISTRY = {
    "P1_Linear":      ["DLinear", "RLinear", "LTSF_Linear", "NBEATS", "NHits"],
    "P2_Transformer": ["PatchTST", "TFT", "Autoformer", "FedFormer", "Informer", "Reformer"],
    "P3_Inverted":    ["iTransformer", "UniTS", "TimeXer", "Crossformer", "CARD"],
    "P4_Frequency":   ["TimesNet", "TimeMixer", "TTM", "FITS", "CoST"],
    "P5_SSM":         ["TimeMachine", "S_Mamba", "MambaFormer", "BiMamba"],
    "P6_Foundation":  ["Chronos", "TimesFM", "Moirai", "Lag_Llama", "TEMPO", "GPT4TS"],
    "P7_SparseMoE":   ["Time_MoE", "Gated_TabNet"],
}
ALL_SOTA_BASELINES = [m for ms in SOTA_TAXONOMY_REGISTRY.values() for m in ms]

GUM_NET_VARIANTS = [
    "GUMNet", "GUMNet_Mamba", "GUMNet_iTrans", "GUMNet_Wavelet",
    "GUMNet_Patch", "GUMNet_Fourier", "GUMNet_Diffusion", "GUMNet_Graph",
    "GUMNet_RL", "GUMNet_MoE_Sparse", "GUMNet_Fusion",
]
```

#### 3. Base heterogeneous model structure and KAN wavelets (from src/models/gumnet_het.py)
```python
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
```

#### 4. Active results files generated from test pipeline (from results_v4/)
```
evaluation_database/environment.json
walkforward/GUMNet/XANG_H3_seed42/predictions.csv
walkforward/GUMNet/XANG_H3_seed42/results.json
walkforward/GUMNet/XANG_H3_seed43/predictions.csv
walkforward/GUMNet/XANG_H3_seed43/results.json
```
These files show a baseline validation run of the system, verifying the runtime environment parameters dynamically.
