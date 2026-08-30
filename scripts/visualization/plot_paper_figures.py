#!/usr/bin/env python3
"""
plot_paper_figures.py
=====================
Generates all figures needed for Q1 paper submission:
  Fig 1: R² degradation across horizons (all models)
  Fig 2: MAPE bar chart by horizon (all models)  
  Fig 3: GUMNet v1 vs v2 improvement chart
  Fig 4: Directional Accuracy comparison
  Fig 5: MCS heatmap

Usage:
    python3 scripts/plot_paper_figures.py [--output-dir docs/figures/]
"""
import os, sys, json, argparse
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

# Professional color palette for Q1 papers
COLORS = {
    'GUMNet':           '#E74C3C',   # Red (our model - stands out)
    'LSTM':             '#3498DB',   # Blue
    'GRU':              '#2ECC71',   # Green
    'BiLSTM_Attention': '#9B59B6',   # Purple
    'XGBoost':          '#F39C12',   # Orange
    'PatchTST':         '#1ABC9C',   # Teal
    'DLinear':          '#E67E22',   # Dark orange
}

MARKERS = {
    'GUMNet':           'D',  # Diamond
    'LSTM':             'o',  # Circle
    'GRU':              's',  # Square
    'BiLSTM_Attention': '^',  # Triangle up
    'XGBoost':          'v',  # Triangle down
    'PatchTST':         'P',  # Plus
    'DLinear':          '*',  # Star
}

MODEL_LABELS = {
    'GUMNet':           'GUM-Net (Ours)',
    'LSTM':             'LSTM',
    'GRU':              'GRU',
    'BiLSTM_Attention': 'BiLSTM-Att.',
    'XGBoost':          'XGBoost',
    'PatchTST':         'PatchTST',
    'DLinear':          'DLinear',
}

HORIZONS = [1, 3, 5, 10, 20, 60]
MODELS = ['GUMNet', 'LSTM', 'GRU', 'BiLSTM_Attention', 'XGBoost', 'PatchTST', 'DLinear']


def setup_style():
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'legend.fontsize': 10,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'figure.dpi': 150,
    })


def plot_r2_degradation(df, output_dir):
    """Fig 1: R² degradation across horizons."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for ax, target in zip(axes, ['XANG', 'DAU']):
        for model in MODELS:
            r2s = []
            for h in HORIZONS:
                row = df[(df.Model==model) & (df.Target==target) & (df.Horizon==h)]
                r2s.append(row.iloc[0]['R2_mean'] if not row.empty else np.nan)
            
            lw = 2.5 if model == 'GUMNet' else 1.5
            ls = '-' if model == 'GUMNet' else '--'
            ms = 8 if model == 'GUMNet' else 6
            ax.plot(range(len(HORIZONS)), r2s,
                    color=COLORS[model], marker=MARKERS[model],
                    linewidth=lw, linestyle=ls, markersize=ms,
                    label=MODEL_LABELS[model], zorder=5 if model=='GUMNet' else 3)
        
        ax.set_xticks(range(len(HORIZONS)))
        ax.set_xticklabels([f'H={h}' for h in HORIZONS])
        ax.set_xlabel('Forecast Horizon (days)')
        ax.set_ylabel('R² Score')
        prod = 'Gasoline (RON 92/95)' if target == 'XANG' else 'Diesel (DO)'
        ax.set_title(f'{prod}')
        ax.set_ylim(-0.2, 1.0)
        ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5, label='R²=0 (random)')
        
        if target == 'XANG':
            ax.legend(loc='upper right', framealpha=0.9, ncol=2, fontsize=9)
    
    plt.suptitle('Figure 1: R² Degradation Across Forecast Horizons', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    out = os.path.join(output_dir, 'fig1_r2_degradation.pdf')
    plt.savefig(out, bbox_inches='tight', dpi=150)
    plt.savefig(out.replace('.pdf', '.png'), bbox_inches='tight', dpi=150)
    plt.close()
    print(f'  Saved: {out}')
    return out


def plot_mape_bars(df, output_dir):
    """Fig 2: MAPE bar charts."""
    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    
    for row_idx, target in enumerate(['XANG', 'DAU']):
        for col_idx, h in enumerate(HORIZONS):
            ax = axes[row_idx, col_idx]
            
            sub = df[(df.Target==target) & (df.Horizon==h)].sort_values('MAPE_mean')
            models = sub['Model'].tolist()
            mapes = sub['MAPE_mean'].tolist()
            stds = sub['MAPE_std'].tolist()
            
            colors = [COLORS[m] for m in models]
            bars = ax.bar(range(len(models)), mapes, color=colors, alpha=0.85,
                         edgecolor='white', linewidth=0.5)
            
            # Add error bars
            ax.errorbar(range(len(models)), mapes,
                       yerr=[s if not np.isnan(s) else 0 for s in stds],
                       fmt='none', color='black', capsize=3, linewidth=1)
            
            # Highlight GUMNet
            if 'GUMNet' in models:
                idx = models.index('GUMNet')
                bars[idx].set_edgecolor('black')
                bars[idx].set_linewidth(1.5)
            
            ax.set_xticks(range(len(models)))
            ax.set_xticklabels([MODEL_LABELS[m].replace(' (Ours)','') for m in models],
                               rotation=45, ha='right', fontsize=8)
            ax.set_title(f'H={h}', fontsize=11)
            ax.set_ylabel('MAPE (%)' if col_idx == 0 else '')
            
            prod = 'Gasoline' if target == 'XANG' else 'Diesel'
            if col_idx == 0:
                ax.set_ylabel(f'{prod}\nMAPE (%)')
    
    plt.suptitle('Figure 2: MAPE by Model and Forecast Horizon', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    out = os.path.join(output_dir, 'fig2_mape_bars.pdf')
    plt.savefig(out, bbox_inches='tight', dpi=150)
    plt.savefig(out.replace('.pdf', '.png'), bbox_inches='tight', dpi=150)
    plt.close()
    print(f'  Saved: {out}')
    return out


def plot_da_comparison(df, output_dir):
    """Fig 3: Directional Accuracy comparison."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for ax, target in zip(axes, ['XANG', 'DAU']):
        for model in MODELS:
            das = []
            for h in HORIZONS:
                row = df[(df.Model==model) & (df.Target==target) & (df.Horizon==h)]
                das.append(row.iloc[0]['DA_mean'] if not row.empty else np.nan)
            
            lw = 2.5 if model == 'GUMNet' else 1.5
            ls = '-' if model == 'GUMNet' else '--'
            ax.plot(range(len(HORIZONS)), das,
                    color=COLORS[model], marker=MARKERS[model],
                    linewidth=lw, linestyle=ls, markersize=6,
                    label=MODEL_LABELS[model])
        
        ax.set_xticks(range(len(HORIZONS)))
        ax.set_xticklabels([f'H={h}' for h in HORIZONS])
        ax.set_xlabel('Forecast Horizon (days)')
        ax.set_ylabel('Directional Accuracy (%)')
        prod = 'Gasoline (RON 92/95)' if target == 'XANG' else 'Diesel (DO)'
        ax.set_title(f'{prod}')
        ax.set_ylim(60, 100)
        ax.axhline(y=50, color='gray', linestyle=':', alpha=0.5, label='Random (50%)')
        
        if target == 'XANG':
            ax.legend(loc='lower right', framealpha=0.9, ncol=2, fontsize=9)
    
    plt.suptitle('Figure 3: Directional Accuracy (%) Across Horizons', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    out = os.path.join(output_dir, 'fig3_directional_accuracy.pdf')
    plt.savefig(out, bbox_inches='tight', dpi=150)
    plt.savefig(out.replace('.pdf', '.png'), bbox_inches='tight', dpi=150)
    plt.close()
    print(f'  Saved: {out}')
    return out


def plot_mae_heatmap(df, output_dir):
    """Fig 4: MAE normalized heatmap — shows relative performance."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    for ax, target in zip(axes, ['XANG', 'DAU']):
        # Build matrix: models × horizons, normalized per horizon
        matrix = np.zeros((len(MODELS), len(HORIZONS)))
        for j, h in enumerate(HORIZONS):
            sub = df[(df.Target==target) & (df.Horizon==h)]
            min_mae = sub['MAE_mean'].min()
            max_mae = sub['MAE_mean'].max()
            
            for i, model in enumerate(MODELS):
                row = sub[sub.Model==model]
                if not row.empty:
                    mae = row.iloc[0]['MAE_mean']
                    # Normalize: 0 = best, 1 = worst
                    matrix[i, j] = (mae - min_mae) / (max_mae - min_mae) if max_mae > min_mae else 0
                else:
                    matrix[i, j] = np.nan
        
        im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=1)
        
        # Labels
        ax.set_xticks(range(len(HORIZONS)))
        ax.set_xticklabels([f'H={h}' for h in HORIZONS])
        ax.set_yticks(range(len(MODELS)))
        ax.set_yticklabels([MODEL_LABELS[m] for m in MODELS])
        
        # Add text annotations
        for i in range(len(MODELS)):
            for j in range(len(HORIZONS)):
                row = df[(df.Model==MODELS[i]) & (df.Target==target) & (df.Horizon==HORIZONS[j])]
                if not row.empty:
                    mae = row.iloc[0]['MAE_mean']
                    text_color = 'white' if matrix[i,j] > 0.6 else 'black'
                    ax.text(j, i, f'{mae:.2f}', ha='center', va='center',
                           fontsize=9, color=text_color, fontweight='bold' if MODELS[i]=='GUMNet' else 'normal')
        
        prod = 'Gasoline (RON 92/95)' if target == 'XANG' else 'Diesel (DO)'
        ax.set_title(f'{prod}\n(Green=Best, Red=Worst for each horizon)', fontsize=11)
        plt.colorbar(im, ax=ax, label='Normalized MAE (0=best)')
    
    plt.suptitle('Figure 4: MAE Performance Heatmap (Normalized per Horizon)', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    out = os.path.join(output_dir, 'fig4_mae_heatmap.pdf')
    plt.savefig(out, bbox_inches='tight', dpi=150)
    plt.savefig(out.replace('.pdf', '.png'), bbox_inches='tight', dpi=150)
    plt.close()
    print(f'  Saved: {out}')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='docs/figures/', help='Output directory')
    args = parser.parse_args()
    
    setup_style()
    
    output_dir = os.path.join(BASE, args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Load results
    df = pd.read_csv(os.path.join(BASE, 'results_v4', 'compiled_results.csv'))
    print(f"Loaded {len(df)} result rows")
    print(f"Models: {df.Model.unique().tolist()}")
    
    print("\nGenerating paper figures...")
    fig1 = plot_r2_degradation(df, output_dir)
    fig2 = plot_mape_bars(df, output_dir)
    fig3 = plot_da_comparison(df, output_dir)
    fig4 = plot_mae_heatmap(df, output_dir)
    
    print(f"\n✅ All figures saved to: {output_dir}")
    print(f"Files: fig1_r2_degradation, fig2_mape_bars, fig3_directional_accuracy, fig4_mae_heatmap")
    print(f"Formats: .pdf (for LaTeX) + .png (for preview)")
