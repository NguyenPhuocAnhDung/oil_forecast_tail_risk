"""
plot_gating.py — Gating Weights Visualization for GUM-Net
Produces:
  1. Stacked bar: mean gating weight per horizon (aggregated over seeds, windows)
  2. Line plot: gating weight by horizon step h (for H60, shows CNN→GRU/KAN shift)
Output: results_v4/Gating_Weights_{XANG|DAU}.png
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from matplotlib.gridspec import GridSpec

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
from config import RESULTS_DIR, ALL_HORIZONS

# ─── style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'figure.dpi': 150,
})

EXPERT_NAMES  = ['CNN', 'GRU-Attention', 'Wavelet-KAN']
EXPERT_STYLES = [
    {'color': 'black',     'linestyle': '-',  'marker': 'o', 'hatch': ''},
    {'color': '#555555',   'linestyle': '--', 'marker': 's', 'hatch': '//'},
    {'color': '#999999',   'linestyle': ':',  'marker': '^', 'hatch': '..'},
]
SEEDS = [42, 123, 777, 2025, 9999]

def load_gating(target: str, horizon: int, seeds=SEEDS) -> np.ndarray | None:
    """Load gating_weights.npy for a (target, horizon); aggregate across seeds.
    Returns array [N_total, h, 3] or None if no file found."""
    arrays = []
    protocol, model = 'walkforward', 'GUMNet'
    for seed in seeds:
        folder = os.path.join(RESULTS_DIR, protocol, model,
                              f'{target}_H{horizon}_seed{seed}')
        npy = os.path.join(folder, 'gating_weights.npy')
        if os.path.exists(npy):
            try:
                gw = np.load(npy)   # [N_windows, h, 3]
                arrays.append(gw)
            except Exception as e:
                print(f"  Warning: could not load {npy}: {e}")
    if not arrays:
        return None
    return np.concatenate(arrays, axis=0)   # [N_total, h, 3]


def main():
    for target in ['XANG', 'DAU']:
        print(f"\n=== Processing {target} ===")

        # ── gather data ──────────────────────────────────────────────────────
        bar_rows = []       # for stacked bar (mean per horizon)
        line_data = {}      # for line plot per step h (only for H60)

        for h in ALL_HORIZONS:
            gw = load_gating(target, h)
            if gw is None:
                print(f"  No data for {target} H{h}")
                continue
            # gw: [N, horizon_steps, 3]
            mean_over_N = np.mean(gw, axis=0)  # [horizon_steps, 3]
            mean_total  = np.mean(gw, axis=(0, 1))  # [3]
            std_total   = np.std( gw, axis=(0, 1))  # [3]

            for i, ex in enumerate(EXPERT_NAMES):
                bar_rows.append({
                    'Horizon': f'H{h}',
                    'Expert':  ex,
                    'Weight':  mean_total[i],
                    'Std':     std_total[i],
                })

            if h == 60:
                line_data[h] = mean_over_N  # [60, 3]

        if not bar_rows:
            print(f"  Skipping {target} — no data found.")
            continue

        df = pd.DataFrame(bar_rows)
        horizons_order = [f'H{h}' for h in ALL_HORIZONS if f'H{h}' in df['Horizon'].unique()]

        # ── figure layout ────────────────────────────────────────────────────
        has_line = bool(line_data)
        ncols = 2 if has_line else 1
        fig = plt.figure(figsize=(14 if has_line else 8, 6))
        gs  = GridSpec(1, ncols, figure=fig,
                       left=0.08, right=0.97, wspace=0.38)

        ax1 = fig.add_subplot(gs[0, 0])

        # ── panel 1: stacked bar ─────────────────────────────────────────────
        pivot = (df.groupby(['Horizon', 'Expert'])['Weight']
                   .mean()
                   .unstack('Expert')
                   .reindex(horizons_order)[EXPERT_NAMES])

        x    = np.arange(len(horizons_order))
        bar_h = 0.55
        bottom = np.zeros(len(x))

        hatches = ['', '//', '..']
        grays   = ['#222222', '#777777', '#BBBBBB']

        for i, ex in enumerate(EXPERT_NAMES):
            vals = pivot[ex].values
            bars = ax1.bar(x, vals, bar_h, bottom=bottom,
                           color=grays[i], hatch=hatches[i],
                           label=ex, edgecolor='black', linewidth=0.7)
            bottom += vals

        ax1.set_xticks(x)
        ax1.set_xticklabels(horizons_order, fontsize=10)
        ax1.set_xlabel('Horizon', fontsize=11)
        ax1.set_ylabel('Mean Gating Weight', fontsize=11)
        ax1.set_ylim(0, 1.05)
        ax1.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
        ax1.set_title(f'(a) Mean Gating Weight per Horizon\n(Cluster: {target})', fontsize=11)
        ax1.legend(loc='upper right', fontsize=9, framealpha=0.8)

        # ── panel 2: line plot for H60 ───────────────────────────────────────
        if has_line:
            ax2 = fig.add_subplot(gs[0, 1])
            gw60 = line_data[60]  # [60, 3]
            steps = np.arange(1, gw60.shape[0] + 1)
            for i, ex in enumerate(EXPERT_NAMES):
                ax2.plot(steps, gw60[:, i],
                         color=EXPERT_STYLES[i]['color'],
                         linestyle=EXPERT_STYLES[i]['linestyle'],
                         marker=EXPERT_STYLES[i]['marker'],
                         markevery=10, markersize=5,
                         linewidth=1.5, label=ex)
            ax2.set_xlabel('Horizon Step h', fontsize=11)
            ax2.set_ylabel('Mean Gating Weight', fontsize=11)
            ax2.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
            ax2.set_title(f'(b) Gating Weight by Step h (H60)\n(Cluster: {target})', fontsize=11)
            ax2.legend(loc='upper right', fontsize=9, framealpha=0.8)
            ax2.set_xlim(1, gw60.shape[0])

        # ── save ─────────────────────────────────────────────────────────────
        out_path = os.path.join(RESULTS_DIR, f'Gating_Weights_{target}.png')
        os.makedirs(RESULTS_DIR, exist_ok=True)
        plt.savefig(out_path, dpi=300, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()
        print(f"  Saved → {out_path}")


if __name__ == '__main__':
    main()
