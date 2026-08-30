import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

os.makedirs('paper_figures', exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'

def generate_compact_fig1():
    # Canvas dimensions: 18.5 x 7.6 inches (compact, elegant, focused only on GUMNetHet)
    fig, ax = plt.subplots(figsize=(18.5, 7.6), dpi=300)
    ax.set_xlim(0, 18.5)
    ax.set_ylim(0, 7.6)
    ax.axis('off')

    # --------------------------------------------------------------------------
    # MASTER HEADER BANNER (Navy with White Text)
    # --------------------------------------------------------------------------
    title_box = patches.FancyBboxPatch((0.25, 6.85), 18.0, 0.58, boxstyle='round,pad=0.02,rounding_size=0.03',
                                       facecolor='#1A365D', edgecolor='#0F294A', linewidth=1.5)
    ax.add_patch(title_box)
    ax.text(9.25, 7.14, 'NEURAL NETWORK ARCHITECTURE OF GUMNetHet', 
            ha='center', va='center', fontsize=14.5, fontweight='bold', color='#FFFFFF')

    # ==========================================================================
    # MAIN ARCHITECTURE CONTAINER
    # ==========================================================================
    panel_main = patches.FancyBboxPatch((0.25, 0.25), 18.0, 6.45, boxstyle='round,pad=0.02,rounding_size=0.03',
                                        facecolor='#F8FAFC', edgecolor='#2B6CB0', linewidth=1.6)
    ax.add_patch(panel_main)

    # --- 1. Input Tensor & Partitioning Column ---
    in_box = patches.FancyBboxPatch((0.45, 0.45), 2.50, 6.05, boxstyle='round,pad=0.02,rounding_size=0.03',
                                    facecolor='#EDF2F7', edgecolor='#4A5568', linewidth=1.4)
    ax.add_patch(in_box)
    ax.text(1.70, 6.18, 'Input Sequence Tensor', ha='center', va='center', fontsize=12, fontweight='bold', color='#000000')
    ax.text(1.70, 5.82, r'$X \in \mathbb{R}^{B \times L \times D}$ ($L=30$)', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000')

    # Sub-partition cards
    p1 = patches.FancyBboxPatch((0.55, 4.05), 2.30, 1.50, boxstyle='round,pad=0.02,rounding_size=0.02',
                                facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=1.2)
    ax.add_patch(p1)
    ax.text(1.70, 5.25, 'Spot Price Features', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(1.70, 4.85, r'$x^{\mathrm{CNN}} \in \mathbb{R}^{B \times L \times D_1}$', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000')
    ax.text(1.70, 4.38, '• MG95, MG92, MG97\n• DO 0.001%, DO 0.05%\n• WTI, Brent, Naphtha', ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    p2 = patches.FancyBboxPatch((0.55, 2.30), 2.30, 1.60, boxstyle='round,pad=0.02,rounding_size=0.02',
                                facecolor='#FAF5FF', edgecolor='#805AD5', linewidth=1.2)
    ax.add_patch(p2)
    ax.text(1.70, 3.58, 'Macro & GPR Risk', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(1.70, 3.18, r'$x^{\mathrm{GRU}} \in \mathbb{R}^{B \times L \times D_2}$', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000')
    ax.text(1.70, 2.70, '• Geopolitical Risk (GPR)\n• USD Index (DXY)\n• GPR_MA30, DXY_MA30', ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    p3 = patches.FancyBboxPatch((0.55, 0.60), 2.30, 1.55, boxstyle='round,pad=0.02,rounding_size=0.02',
                                facecolor='#FFF5F5', edgecolor='#E53E3E', linewidth=1.2)
    ax.add_patch(p3)
    ax.text(1.70, 1.85, 'Ratios & Volatility', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(1.70, 1.45, r'$x^{\mathrm{KAN}} \in \mathbb{R}^{B \times L \times D_3}$', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000')
    ax.text(1.70, 0.98, '• Crack Spread Ratios\n• Realized Vol (10d, 30d)\n• Day_sin, Day_cos', ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    # --- 2. Three Specialized Experts ---
    # Expert 1: CNN
    exp1_box = patches.FancyBboxPatch((3.45, 4.55), 3.50, 1.95, boxstyle='round,pad=0.02,rounding_size=0.03',
                                     facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=1.4)
    ax.add_patch(exp1_box)
    ax.text(5.20, 6.15, 'Expert 1: Multi-Scale 1D-CNN', ha='center', va='center', fontsize=12, fontweight='bold', color='#000000')
    exp1_text = (
        '• Multi-Resolution Inception: $k \\in \\{3, 7, 15\\}$\n'
        '• Temporal Convolution + LayerNorm\n'
        '• Softmax Temporal Attention Pooling\n'
        '• Output: ' + r'$f_{\mathrm{cnn}} \in \mathbb{R}^{B \times d}$'
    )
    ax.text(5.20, 5.25, exp1_text, ha='center', va='center', fontsize=10.5, color='#000000', linespacing=1.3)

    # Expert 2: GRU
    exp2_box = patches.FancyBboxPatch((3.45, 2.50), 3.50, 1.85, boxstyle='round,pad=0.02,rounding_size=0.03',
                                     facecolor='#FAF5FF', edgecolor='#805AD5', linewidth=1.4)
    ax.add_patch(exp2_box)
    ax.text(5.20, 4.00, 'Expert 2: Stacked GRU-Attention', ha='center', va='center', fontsize=12, fontweight='bold', color='#000000')
    exp2_text = (
        '• 2-Layer Stacked Recurrent GRU (dim $d$)\n'
        '• Temporal Multi-Head Attention Alignment\n'
        '• Captures Low-Frequency Macro Trends\n'
        '• Output: ' + r'$f_{\mathrm{gru}} \in \mathbb{R}^{B \times d}$'
    )
    ax.text(5.20, 3.10, exp2_text, ha='center', va='center', fontsize=10.5, color='#000000', linespacing=1.3)

    # Expert 3: Wavelet-KAN
    exp3_box = patches.FancyBboxPatch((3.45, 0.60), 3.50, 1.70, boxstyle='round,pad=0.02,rounding_size=0.03',
                                     facecolor='#FFF5F5', edgecolor='#E53E3E', linewidth=1.4)
    ax.add_patch(exp3_box)
    ax.text(5.20, 1.95, 'Expert 3: Wavelet-KAN Shock Block', ha='center', va='center', fontsize=12, fontweight='bold', color='#000000')
    exp3_text = (
        '• Mexican Hat Wavelet: ' + r'$\psi(z) = (1-z^2) e^{-0.5 z^2}$' + '\n'
        '• Learnable Non-linear Spline Projections\n'
        '• Dampens Geopolitical Tail Risk Spikes\n'
        '• Output: ' + r'$f_{\mathrm{kan}} \in \mathbb{R}^{B \times d}$'
    )
    ax.text(5.20, 1.20, exp3_text, ha='center', va='center', fontsize=10.5, color='#000000', linespacing=1.3)

    # --- 3. Horizon-Aware Dynamic Gating Router ---
    gate_outer = patches.FancyBboxPatch((7.40, 0.45), 4.75, 6.05, boxstyle='round,pad=0.02,rounding_size=0.03',
                                        facecolor='#FEFCBF', edgecolor='#D69E2E', linewidth=1.5)
    ax.add_patch(gate_outer)
    ax.text(9.77, 6.18, 'Step 2: Horizon-Aware Dynamic Router', ha='center', va='center',
            fontsize=12.5, fontweight='bold', color='#000000')

    # Concat Box
    cat_box = patches.FancyBboxPatch((7.55, 0.65), 1.55, 5.10, boxstyle='round,pad=0.02,rounding_size=0.02',
                                     facecolor='#FFFFFF', edgecolor='#D69E2E', linewidth=1.2)
    ax.add_patch(cat_box)
    ax.text(8.32, 5.35, 'Feature Concat', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    cat_content = (
        r'$f_{\mathrm{cnn}} \in \mathbb{R}^d$' + '\n\n' +
        r'$f_{\mathrm{gru}} \in \mathbb{R}^d$' + '\n\n' +
        r'$f_{\mathrm{kan}} \in \mathbb{R}^d$' + '\n\n' +
        r'Pos Emb $\mathrm{Pos}_h$' + '\n\n' +
        r'Context $[\mu_X, \sigma_X]$'
    )
    ax.text(8.32, 2.95, cat_content, ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000')

    # MLP Gate Box
    mlp_gate = patches.FancyBboxPatch((9.30, 2.10), 1.25, 2.70, boxstyle='round,pad=0.02,rounding_size=0.02',
                                      facecolor='#FAF089', edgecolor='#B7791F', linewidth=1.2)
    ax.add_patch(mlp_gate)
    ax.text(9.92, 4.40, 'MLP Gate', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000')
    ax.text(9.92, 3.20, '(128 units)\n+\nGELU\n+\nSoftmax\nLayer', ha='center', va='center', fontsize=10, fontweight='bold', color='#000000', linespacing=1.25)

    # Weights & Fusion Box
    fuse_box = patches.FancyBboxPatch((10.75, 0.65), 1.25, 5.10, boxstyle='round,pad=0.02,rounding_size=0.02',
                                      facecolor='#FFFFFF', edgecolor='#D69E2E', linewidth=1.2)
    ax.add_patch(fuse_box)
    ax.text(11.37, 5.35, 'Router Weights', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    fuse_content = (
        r'$w_1$ (CNN)' + '\n' +
        r'$w_2$ (GRU)' + '\n' +
        r'$w_3$ (KAN)' + '\n\n' +
        r'$\sum_{i=1}^3 w_i = 1$' + '\n\n' +
        'Fused Feature:\n' +
        r'$f_{\mathrm{fused}} = \sum w_i f_i$' + '\n' +
        r'$\in \mathbb{R}^{B \times d}$'
    )
    ax.text(11.37, 2.90, fuse_content, ha='center', va='center', fontsize=10, fontweight='bold', color='#000000', linespacing=1.25)

    # --- 4. Horizon Heads & Quantile Heads ---
    head_outer = patches.FancyBboxPatch((12.55, 0.45), 5.50, 6.05, boxstyle='round,pad=0.02,rounding_size=0.03',
                                        facecolor='#E6FFFA', edgecolor='#319795', linewidth=1.5)
    ax.add_patch(head_outer)
    ax.text(15.30, 6.18, 'Step 3: Horizon Heads & Residual Scaling', ha='center', va='center',
            fontsize=12.5, fontweight='bold', color='#000000')

    # 3 Head Specialized Cards
    h1 = patches.FancyBboxPatch((12.70, 4.30), 2.50, 1.45, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#319795', linewidth=1.1)
    ax.add_patch(h1)
    ax.text(13.95, 5.40, 'Short Head: $h \\in \\{1, 3\\}$', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(13.95, 4.80, '• Direct Linear Projection\n• Preserves Short Momentum\n• Fast O(1) Latency Execution', 
            ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    h2 = patches.FancyBboxPatch((12.70, 2.45), 2.50, 1.60, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#319795', linewidth=1.1)
    ax.add_patch(h2)
    ax.text(13.95, 3.68, 'Medium Head: $h \\in \\{5, 7, 10\\}$', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(13.95, 3.00, '• 2-Layer MLP + GELU Act\n• Regulatory Cycle Calibration\n• Non-linear Policy Mapping', 
            ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    h3 = patches.FancyBboxPatch((12.70, 0.65), 2.50, 1.55, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#319795', linewidth=1.1)
    ax.add_patch(h3)
    ax.text(13.95, 1.85, 'Long Head: $h \\in \\{20, 60\\}$', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(13.95, 1.15, '• Deep 3-Layer MLP + Norm\n• Extrapolation Drift Bounding\n• Strategic Term Forecast', 
            ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    # Quantile Output & Residual Bounding Box
    res_box = patches.FancyBboxPatch((15.40, 0.65), 2.50, 5.10, boxstyle='round,pad=0.02,rounding_size=0.02',
                                     facecolor='#FFFFFF', edgecolor='#319795', linewidth=1.2)
    ax.add_patch(res_box)
    ax.text(16.65, 5.35, 'Calibrated Tail Risk', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000')
    res_content = (
        'Quantile Formulation:\n' +
        r'$\hat{y}_{t+h}^{(q)} = \mathrm{Head}_q(f_{\mathrm{fused}})$' + '\n' +
        r'$+ \gamma_h \cdot x_{t}^{\mathrm{target}}$' + '\n\n' +
        'Quantile Grid:\n' +
        r'$q \in \{0.1, 0.5, 0.9\}$' + '\n' +
        r'($80\%$ Prediction Bounds)' + '\n\n' +
        'Inverse Mapping:\n' +
        r'$\hat{P}_{t+h} = P_t \cdot e^{\hat{R}_{t \to t+h}}$' + '\n\n' +
        'Output Tensor Shape:\n' +
        r'$(B, C \times |\mathcal{Q}|)$'
    )
    ax.text(16.65, 2.95, res_content, ha='center', va='center', fontsize=9.8, fontweight='bold', color='#000000', linespacing=1.25)

    # Connecting Arrows
    arr = dict(facecolor='#000000', edgecolor='#000000', width=1.8, headwidth=7, headlength=7)
    ax.annotate('', xy=(3.45, 5.50), xytext=(2.95, 4.80), arrowprops=arr)
    ax.annotate('', xy=(3.45, 3.40), xytext=(2.95, 3.10), arrowprops=arr)
    ax.annotate('', xy=(3.45, 1.45), xytext=(2.95, 1.45), arrowprops=arr)

    ax.annotate('', xy=(7.55, 4.80), xytext=(6.95, 5.50), arrowprops=arr)
    ax.annotate('', xy=(7.55, 3.40), xytext=(6.95, 3.40), arrowprops=arr)
    ax.annotate('', xy=(7.55, 2.10), xytext=(6.95, 1.45), arrowprops=arr)

    ax.annotate('', xy=(9.30, 3.45), xytext=(9.10, 3.45), arrowprops=arr)
    ax.annotate('', xy=(10.75, 3.45), xytext=(10.55, 3.45), arrowprops=arr)

    ax.annotate('', xy=(12.70, 5.00), xytext=(12.00, 4.00), arrowprops=arr)
    ax.annotate('', xy=(12.70, 3.30), xytext=(12.00, 3.30), arrowprops=arr)
    ax.annotate('', xy=(12.70, 1.50), xytext=(12.00, 2.60), arrowprops=arr)

    ax.annotate('', xy=(15.40, 3.20), xytext=(15.20, 3.20), arrowprops=arr)

    plt.tight_layout()
    output_path = 'paper_figures/fig1_gumnethet_compact.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"✓ Successfully generated compact Figure 1: {output_path}")

generate_compact_fig1()
