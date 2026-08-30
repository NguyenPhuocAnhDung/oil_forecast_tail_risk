#!/usr/bin/env python3
"""
Script: plot_results_figures.py
Generate Figures 3-6 for the paper:
- Fig 3: R² degradation by horizon, Diesel (DAU)
- Fig 4: R² degradation by horizon, Gasoline (XANG)
- Fig 5: MAPE bar chart, Diesel
- Fig 6: MAPE bar chart, Gasoline
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import os

BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESDIR = os.path.join(BASE, 'results_v4')
FIGDIR = os.path.join(RESDIR, 'figures')
os.makedirs(FIGDIR, exist_ok=True)

df = pd.read_csv(os.path.join(RESDIR, 'compiled_results.csv'))

MODELS = ['GUMNet', 'LSTM', 'GRU', 'BiLSTM_Attention', 'XGBoost', 'PatchTST', 'DLinear']
HORIZONS = [1, 3, 5, 10, 20, 60]
MODEL_LABELS = {
    'GUMNet': 'GUM-Net (ours)',
    'LSTM': 'LSTM',
    'GRU': 'GRU',
    'BiLSTM_Attention': 'BiLSTM-Attention',
    'XGBoost': 'XGBoost',
    'PatchTST': 'PatchTST',
    'DLinear': 'DLinear',
}

# Color scheme: colorblind-friendly, grayscale-compatible
COLORS = {
    'GUMNet':           '#000000',  # black (bold)
    'LSTM':             '#1f77b4',  # blue
    'GRU':              '#ff7f0e',  # orange
    'BiLSTM_Attention': '#2ca02c',  # green
    'XGBoost':          '#d62728',  # red
    'PatchTST':         '#9467bd',  # purple
    'DLinear':          '#8c564b',  # brown
}
LINESTYLES = {
    'GUMNet':           '-',
    'LSTM':             '--',
    'GRU':              '--',
    'BiLSTM_Attention': '-.',
    'XGBoost':          ':',
    'PatchTST':         '-.',
    'DLinear':          ':',
}
LINEWIDTHS = {m: (2.5 if m == 'GUMNet' else 1.5) for m in MODELS}
MARKERS = {
    'GUMNet': 'o',
    'LSTM': 's',
    'GRU': '^',
    'BiLSTM_Attention': 'D',
    'XGBoost': 'x',
    'PatchTST': 'v',
    'DLinear': 'P',
}

# ── Elsevier-compatible font settings ──
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'legend.fontsize': 8,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.dpi': 300,
})

def plot_r2_degradation(target, fig_num):
    """Plot R² vs Horizon for all models (degradation curve)."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    for model in MODELS:
        sub = df[(df['Model']==model) & (df['Target']==target)].sort_values('Horizon')
        if sub.empty:
            continue
        r2_vals = sub['R2_mean'].values
        r2_std  = sub['R2_std'].values
        
        ax.plot(HORIZONS, r2_vals,
                color=COLORS[model],
                linestyle=LINESTYLES[model],
                linewidth=LINEWIDTHS[model],
                marker=MARKERS[model],
                markersize=6,
                label=MODEL_LABELS[model])
        
        # Error band (±std)
        ax.fill_between(HORIZONS,
                        r2_vals - r2_std,
                        r2_vals + r2_std,
                        alpha=0.08,
                        color=COLORS[model])
    
    # Formatting
    target_label = 'Diesel (DO 0.001%, DO 0.05%)' if target == 'DAU' else 'Gasoline (RON95, RON92)'
    ax.set_title(f'Hình {fig_num}. R² Degradation — {target_label}', 
                 pad=10, fontweight='bold')
    ax.set_xlabel('Forecast Horizon (business days)')
    ax.set_ylabel('R² Score (↑ higher is better)')
    ax.set_xticks(HORIZONS)
    ax.set_xticklabels([f'H{h}' for h in HORIZONS])
    ax.set_ylim(-0.2, 1.0)
    ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5, linewidth=0.8)
    ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.3, linewidth=0.8)
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='upper right', framealpha=0.9, ncol=2, fontsize=8)
    
    plt.tight_layout()
    out = os.path.join(FIGDIR, f'fig{fig_num}_r2_degradation_{target.lower()}.png')
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved: {out}')
    return out

def plot_mape_barchart(target, fig_num):
    """Plot MAPE bar chart grouped by horizon."""
    n_models = len(MODELS)
    n_horizons = len(HORIZONS)
    bar_width = 0.11
    x = np.arange(n_horizons)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    for i, model in enumerate(MODELS):
        sub = df[(df['Model']==model) & (df['Target']==target)].sort_values('Horizon')
        if sub.empty:
            continue
        mape_vals = sub['MAPE_mean'].values
        mape_std  = sub['MAPE_std'].values
        
        offset = (i - n_models/2 + 0.5) * bar_width
        bars = ax.bar(x + offset, mape_vals,
                      bar_width,
                      label=MODEL_LABELS[model],
                      color=COLORS[model],
                      alpha=0.85 if model != 'GUMNet' else 1.0,
                      edgecolor='black' if model == 'GUMNet' else 'none',
                      linewidth=1.2 if model == 'GUMNet' else 0)
        ax.errorbar(x + offset, mape_vals, yerr=mape_std,
                   fmt='none', color='black', capsize=2, linewidth=0.8)
    
    target_label = 'Diesel (DO 0.001%, DO 0.05%)' if target == 'DAU' else 'Gasoline (RON95, RON92)'
    ax.set_title(f'Hình {fig_num}. MAPE (%) by Horizon — {target_label}',
                 pad=10, fontweight='bold')
    ax.set_xlabel('Forecast Horizon')
    ax.set_ylabel('MAPE (%)')
    ax.set_xticks(x)
    ax.set_xticklabels([f'H{h}' for h in HORIZONS])
    ax.legend(loc='upper left', framealpha=0.9, ncol=2, fontsize=8)
    ax.grid(True, alpha=0.3, axis='y', linestyle=':')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    out = os.path.join(FIGDIR, f'fig{fig_num}_mape_{target.lower()}.png')
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'✅ Saved: {out}')
    return out

# Generate all 4 figures
print("Generating paper figures...")
fig3 = plot_r2_degradation('DAU', 3)
fig4 = plot_r2_degradation('XANG', 4)
fig5 = plot_mape_barchart('DAU', 5)
fig6 = plot_mape_barchart('XANG', 6)

print(f'\n✅ All 4 figures generated in {FIGDIR}')
print('Files:')
for p in [fig3, fig4, fig5, fig6]:
    size = os.path.getsize(p)
    print(f'  {os.path.basename(p)}: {size:,} bytes')
