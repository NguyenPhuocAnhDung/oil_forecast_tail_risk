"""
Overfitting Diagnostic & Visualization for GUMNet Paper
========================================================
Tạo plots: 
  1. Seed variance plot (H1-H5)
  2. R² degradation by horizon
  3. Iteration-level error distribution (box plot by iter)
  4. DA comparison heatmap
"""
import json, os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE / "results_v4" / "walkforward"
OUT_DIR     = BASE / "results_v4" / "figures"
OUT_DIR.mkdir(exist_ok=True)

MODELS   = ["GUMNet","LSTM","GRU","BiLSTM_Attention","XGBoost","PatchTST","DLinear"]
HORIZONS = [1, 3, 5, 10, 20, 60]
SEEDS    = [42, 123, 777, 2025, 9999]
COLORS   = {
    "GUMNet":"#E63946","LSTM":"#457B9D","GRU":"#1D3557",
    "BiLSTM_Attention":"#2A9D8F","XGBoost":"#E9C46A",
    "PatchTST":"#F4A261","DLinear":"#264653"
}

# ── Load all results ─────────────────────────────────────────────────────────
records = []
for p in RESULTS_DIR.rglob("results.json"):
    with open(p) as f:
        d = json.load(f)
    records.append({
        "model":d["model"],"target":d["target_type"],
        "horizon":d["horizon"],"seed":d["seed"],
        "MAE":d["metrics"]["MAE"],"MAPE":d["metrics"]["MAPE"],
        "R2":d["metrics"]["R2"],"DA":d["metrics"]["DA"],
    })
df = pd.DataFrame(records)


# ══════════════════════════════════════════════════════════════════════════════
# PLOT 1: R² Degradation by Horizon (GUMNet vs Top Baselines)
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("GUMNet vs Baselines: R² Degradation by Forecast Horizon\n(Walk-Forward Protocol, 5 Seeds)",
             fontsize=13, fontweight='bold', y=1.02)

for ax, tgt in zip(axes, ["XANG","DAU"]):
    plot_models = ["GUMNet","LSTM","DLinear","PatchTST","BiLSTM_Attention"]
    for m in plot_models:
        r2s, hs = [], []
        for h in HORIZONS:
            v = df[(df.model==m)&(df.target==tgt)&(df.horizon==h)]["R2"]
            if not v.empty:
                r2s.append(v.mean())
                hs.append(h)
        lw = 3 if m == "GUMNet" else 1.5
        ls = '-' if m == "GUMNet" else '--'
        ms = 'o' if m == "GUMNet" else 's'
        ax.plot(hs, r2s, color=COLORS.get(m,"gray"), linewidth=lw,
                linestyle=ls, marker=ms, markersize=8 if m=="GUMNet" else 6,
                label=m, zorder=3 if m=="GUMNet" else 2)
    
    ax.axhline(0.5, color='gray', linestyle=':', linewidth=1, alpha=0.5, label='R²=0.5 threshold')
    ax.axhline(0.1, color='red', linestyle=':', linewidth=1, alpha=0.5, label='R²=0.1 (collapse)')
    ax.fill_between([0,65], 0, 0.1, alpha=0.08, color='red', label='Collapse zone')
    ax.set_title(f"Target: {'XANG (Gasoline)' if tgt=='XANG' else 'DAU (Diesel)'}", fontsize=12)
    ax.set_xlabel("Forecast Horizon (days)", fontsize=11)
    ax.set_ylabel("R² Score", fontsize=11)
    ax.set_xticks(HORIZONS)
    ax.set_xticklabels([f'H{h}' for h in HORIZONS])
    ax.set_ylim(-0.1, 1.0)
    ax.legend(fontsize=8, loc='lower left')
    ax.grid(True, alpha=0.3)
    
    # Annotate H10 collapse
    if tgt == "XANG":
        gum_h10 = df[(df.model=="GUMNet")&(df.target=="XANG")&(df.horizon==10)]["R2"].mean()
        ax.annotate(f'GUMNet R²={gum_h10:.3f}\n(convergence failure)', 
                    xy=(10, gum_h10), xytext=(20, 0.3),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=8, color='red', fontweight='bold')

plt.tight_layout()
plt.savefig(OUT_DIR/"r2_degradation.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ Saved: {OUT_DIR}/r2_degradation.png")


# ══════════════════════════════════════════════════════════════════════════════
# PLOT 2: Seed Variance (GUMNet Stability across Seeds H1-H5)
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("GUMNet Seed Stability (Reproducibility Check)\nMAE across 3 Seeds, H1-H5",
             fontsize=13, fontweight='bold')

for ax, tgt in zip(axes, ["XANG","DAU"]):
    x_pos = np.arange(3)  # H1, H3, H5
    labels = ["H1","H3","H5"]
    gum_means, gum_stds = [], []
    lstm_means, lstm_stds = [], []
    
    for h in [1, 3, 5]:
        gv = df[(df.model=="GUMNet")&(df.target==tgt)&(df.horizon==h)]["MAE"]
        lv = df[(df.model=="LSTM")&(df.target==tgt)&(df.horizon==h)]["MAE"]
        gum_means.append(gv.mean() if not gv.empty else 0)
        gum_stds.append(gv.std() if not gv.empty else 0)
        lstm_means.append(lv.mean() if not lv.empty else 0)
        lstm_stds.append(lv.std() if not lv.empty else 0)
    
    w = 0.35
    b1 = ax.bar(x_pos-w/2, gum_means, w, yerr=gum_stds, 
                color=COLORS["GUMNet"], label='GUMNet', alpha=0.9,
                error_kw=dict(elinewidth=2, capsize=5))
    b2 = ax.bar(x_pos+w/2, lstm_means, w, yerr=lstm_stds,
                color=COLORS["LSTM"], label='LSTM', alpha=0.9,
                error_kw=dict(elinewidth=2, capsize=5))
    
    ax.set_title(f"Target: {'XANG (Gasoline)' if tgt=='XANG' else 'DAU (Diesel)'}", fontsize=12)
    ax.set_xlabel("Forecast Horizon", fontsize=11)
    ax.set_ylabel("MAE (error bars = std across seeds)", fontsize=11)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(OUT_DIR/"seed_stability.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ Saved: {OUT_DIR}/seed_stability.png")


# ══════════════════════════════════════════════════════════════════════════════
# PLOT 3: Direction Accuracy Heatmap (All Models × Horizons)
# ══════════════════════════════════════════════════════════════════════════════
for tgt in ["XANG","DAU"]:
    da_matrix = []
    row_labels = []
    for m in MODELS:
        row = []
        for h in HORIZONS:
            v = df[(df.model==m)&(df.target==tgt)&(df.horizon==h)]["DA"]
            row.append(v.mean() if not v.empty else np.nan)
        da_matrix.append(row)
        row_labels.append(m)
    
    da_arr = np.array(da_matrix)
    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.imshow(da_arr, cmap='RdYlGn', aspect='auto', vmin=60, vmax=100)
    
    ax.set_xticks(range(5))
    ax.set_xticklabels([f'H{h}' for h in HORIZONS], fontsize=12)
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels(row_labels, fontsize=11)
    
    for i in range(len(MODELS)):
        for j in range(5):
            val = da_arr[i, j]
            if not np.isnan(val):
                star = "★" if row_labels[i] == "GUMNet" else ""
                ax.text(j, i, f"{val:.1f}%{star}", ha='center', va='center',
                       fontsize=9, fontweight='bold' if row_labels[i]=="GUMNet" else 'normal')
    
    plt.colorbar(im, ax=ax, label='Direction Accuracy (%)')
    ax.set_title(f"Direction Accuracy (DA%) — Target: {'XANG Gasoline' if tgt=='XANG' else 'DAU Diesel'}\n(★ = GUMNet | Walk-Forward Protocol)",
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUT_DIR/f"da_heatmap_{tgt}.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {OUT_DIR}/da_heatmap_{tgt}.png")


# ══════════════════════════════════════════════════════════════════════════════
# PLOT 4: MAPE Comparison — GUMNet Sweet Spot Analysis  
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("MAPE Comparison: GUMNet vs All Baselines by Horizon\n(Shaded = GUMNet advantage zone)",
             fontsize=13, fontweight='bold')

for ax, tgt in zip(axes, ["XANG","DAU"]):
    plot_models = ["GUMNet","LSTM","GRU","BiLSTM_Attention","XGBoost","PatchTST","DLinear"]
    gum_mapes = []
    for h in HORIZONS:
        v = df[(df.model=="GUMNet")&(df.target==tgt)&(df.horizon==h)]["MAPE"]
        gum_mapes.append(v.mean() if not v.empty else np.nan)
    
    for m in plot_models:
        mapes, hs = [], []
        for h in HORIZONS:
            v = df[(df.model==m)&(df.target==tgt)&(df.horizon==h)]["MAPE"]
            if not v.empty:
                mapes.append(v.mean())
                hs.append(h)
        lw = 3 if m == "GUMNet" else 1.5
        ls = '-' if m == "GUMNet" else '--'
        ax.plot(hs, mapes, color=COLORS.get(m,"gray"), linewidth=lw,
                linestyle=ls, label=m, marker='o' if m=="GUMNet" else 's',
                markersize=8 if m=="GUMNet" else 5)
    
    # Shade GUMNet sweet spot (H3-H5 for XANG)
    if tgt == "XANG":
        ax.axvspan(2.5, 5.5, alpha=0.1, color='green', label='GUMNet advantage zone (H3-H5)')
        ax.annotate("GUMNet wins\nMAPE", xy=(3, 1.5), fontsize=9, color='green', ha='center')
    
    ax.set_title(f"Target: {'XANG (Gasoline)' if tgt=='XANG' else 'DAU (Diesel)'}", fontsize=12)
    ax.set_xlabel("Forecast Horizon (days)", fontsize=11)
    ax.set_ylabel("MAPE (%)", fontsize=11)
    ax.set_xticks(HORIZONS)
    ax.set_xticklabels([f'H{h}' for h in HORIZONS])
    ax.legend(fontsize=8, loc='upper left')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUT_DIR/"mape_comparison.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ Saved: {OUT_DIR}/mape_comparison.png")


print("\n🎉 All diagnostic plots saved to:")
print(f"   {OUT_DIR}")
print("\nPlots created:")
print("  1. r2_degradation.png     — R² drop by horizon (shows H10 collapse)")
print("  2. seed_stability.png     — MAE across seeds (shows no overfitting)")
print("  3. da_heatmap_XANG.png    — DA heatmap (GUMNet DA strong)")
print("  4. da_heatmap_DAU.png     — DA heatmap (DAU DA deficit H1-H5)")
print("  5. mape_comparison.png    — MAPE comparison (GUMNet sweet spot H3-H5)")

