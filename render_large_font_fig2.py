import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

os.makedirs('paper_figures', exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'

def generate_perfect_fig2():
    # Canvas dimensions: 18.5 x 10.8 inches
    fig, ax = plt.subplots(figsize=(18.5, 10.8), dpi=300)
    ax.set_xlim(0, 18.5)
    ax.set_ylim(0, 10.8)
    ax.axis('off')

    # --------------------------------------------------------------------------
    # MASTER HEADER BANNER (Navy with White Text)
    # --------------------------------------------------------------------------
    title_box = patches.FancyBboxPatch((0.25, 10.10), 18.0, 0.60, boxstyle='round,pad=0.02,rounding_size=0.03',
                                       facecolor='#1A365D', edgecolor='#0F294A', linewidth=1.5)
    ax.add_patch(title_box)
    ax.text(9.25, 10.40, 'NEURAL NETWORK ARCHITECTURE OF GUMNetHet & BASELINE PARADIGMS', 
            ha='center', va='center', fontsize=14.5, fontweight='bold', color='#FFFFFF')

    # ==========================================================================
    # PANEL (A): GUMNetHet Core Architecture (Expanded & Rich)
    # ==========================================================================
    panel_top = patches.FancyBboxPatch((0.25, 3.25), 18.0, 6.65, boxstyle='round,pad=0.02,rounding_size=0.03',
                                       facecolor='#F8FAFC', edgecolor='#2B6CB0', linewidth=1.6)
    ax.add_patch(panel_top)
    
    # Sub-header A Banner
    sh_a = patches.FancyBboxPatch((0.45, 9.35), 9.6, 0.45, boxstyle='round,pad=0.02,rounding_size=0.02',
                                  facecolor='#2B6CB0', edgecolor='#2B6CB0', linewidth=1.0)
    ax.add_patch(sh_a)
    ax.text(5.25, 9.57, '(A) GUMNetHet: Heterogeneous Mixture of Local-Global Experts', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#FFFFFF')

    # --- 1. Input Tensor & Partitioning Column ---
    in_box = patches.FancyBboxPatch((0.45, 3.45), 2.50, 5.75, boxstyle='round,pad=0.02,rounding_size=0.03',
                                    facecolor='#EDF2F7', edgecolor='#4A5568', linewidth=1.4)
    ax.add_patch(in_box)
    ax.text(1.70, 8.85, 'Input Sequence Tensor', ha='center', va='center', fontsize=12, fontweight='bold', color='#000000')
    ax.text(1.70, 8.50, r'$X \in \mathbb{R}^{B \times L \times D}$ ($L=30$)', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000')

    # Sub-partition cards (All text in black)
    p1 = patches.FancyBboxPatch((0.55, 6.85), 2.30, 1.45, boxstyle='round,pad=0.02,rounding_size=0.02',
                                facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=1.2)
    ax.add_patch(p1)
    ax.text(1.70, 8.00, 'Spot Price Features', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(1.70, 7.60, r'$x^{\mathrm{CNN}} \in \mathbb{R}^{B \times L \times D_1}$', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000')
    ax.text(1.70, 7.15, '• MG95, MG92, MG97\n• DO 0.001%, DO 0.05%\n• WTI, Brent, Naphtha', ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    p2 = patches.FancyBboxPatch((0.55, 5.15), 2.30, 1.55, boxstyle='round,pad=0.02,rounding_size=0.02',
                                facecolor='#FAF5FF', edgecolor='#805AD5', linewidth=1.2)
    ax.add_patch(p2)
    ax.text(1.70, 6.35, 'Macro & GPR Risk', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(1.70, 5.95, r'$x^{\mathrm{GRU}} \in \mathbb{R}^{B \times L \times D_2}$', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000')
    ax.text(1.70, 5.50, '• Geopolitical Risk (GPR)\n• USD Index (DXY)\n• GPR_MA30, DXY_MA30', ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    p3 = patches.FancyBboxPatch((0.55, 3.60), 2.30, 1.40, boxstyle='round,pad=0.02,rounding_size=0.02',
                                facecolor='#FFF5F5', edgecolor='#E53E3E', linewidth=1.2)
    ax.add_patch(p3)
    ax.text(1.70, 4.65, 'Ratios & Volatility', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(1.70, 4.25, r'$x^{\mathrm{KAN}} \in \mathbb{R}^{B \times L \times D_3}$', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000')
    ax.text(1.70, 3.88, '• Crack Spread Ratios\n• Realized Vol (10d, 30d)\n• Day_sin, Day_cos', ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    # --- 2. Three Specialized Experts ---
    # Expert 1: CNN
    exp1_box = patches.FancyBboxPatch((3.45, 7.25), 3.50, 1.95, boxstyle='round,pad=0.02,rounding_size=0.03',
                                     facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=1.4)
    ax.add_patch(exp1_box)
    ax.text(5.20, 8.85, 'Expert 1: Multi-Scale 1D-CNN', ha='center', va='center', fontsize=12, fontweight='bold', color='#000000')
    exp1_text = (
        '• Multi-Resolution Inception: $k \\in \\{3, 7, 15\\}$\n'
        '• Temporal Convolution + LayerNorm\n'
        '• Softmax Temporal Attention Pooling\n'
        '• Output: ' + r'$f_{\mathrm{cnn}} \in \mathbb{R}^{B \times d}$'
    )
    ax.text(5.20, 7.95, exp1_text, ha='center', va='center', fontsize=10.5, color='#000000', linespacing=1.3)

    # Expert 2: GRU
    exp2_box = patches.FancyBboxPatch((3.45, 5.25), 3.50, 1.85, boxstyle='round,pad=0.02,rounding_size=0.03',
                                     facecolor='#FAF5FF', edgecolor='#805AD5', linewidth=1.4)
    ax.add_patch(exp2_box)
    ax.text(5.20, 6.75, 'Expert 2: Stacked GRU-Attention', ha='center', va='center', fontsize=12, fontweight='bold', color='#000000')
    exp2_text = (
        '• 2-Layer Stacked Recurrent GRU (dim $d$)\n'
        '• Temporal Multi-Head Attention Alignment\n'
        '• Captures Low-Frequency Macro Trends\n'
        '• Output: ' + r'$f_{\mathrm{gru}} \in \mathbb{R}^{B \times d}$'
    )
    ax.text(5.20, 5.85, exp2_text, ha='center', va='center', fontsize=10.5, color='#000000', linespacing=1.3)

    # Expert 3: Wavelet-KAN
    exp3_box = patches.FancyBboxPatch((3.45, 3.45), 3.50, 1.65, boxstyle='round,pad=0.02,rounding_size=0.03',
                                     facecolor='#FFF5F5', edgecolor='#E53E3E', linewidth=1.4)
    ax.add_patch(exp3_box)
    ax.text(5.20, 4.75, 'Expert 3: Wavelet-KAN Shock Block', ha='center', va='center', fontsize=12, fontweight='bold', color='#000000')
    exp3_text = (
        '• Mexican Hat Wavelet: ' + r'$\psi(z) = (1-z^2) e^{-0.5 z^2}$' + '\n'
        '• Learnable Non-linear Spline Projections\n'
        '• Dampens Geopolitical Tail Risk Spikes\n'
        '• Output: ' + r'$f_{\mathrm{kan}} \in \mathbb{R}^{B \times d}$'
    )
    ax.text(5.20, 4.00, exp3_text, ha='center', va='center', fontsize=10.5, color='#000000', linespacing=1.3)

    # --- 3. Horizon-Aware Dynamic Gating Router ---
    gate_outer = patches.FancyBboxPatch((7.40, 3.45), 4.75, 5.75, boxstyle='round,pad=0.02,rounding_size=0.03',
                                        facecolor='#FEFCBF', edgecolor='#D69E2E', linewidth=1.5)
    ax.add_patch(gate_outer)
    ax.text(9.77, 8.85, 'Step 2: Horizon-Aware Dynamic Router', ha='center', va='center',
            fontsize=12.5, fontweight='bold', color='#000000')

    # Concat Box
    cat_box = patches.FancyBboxPatch((7.55, 3.65), 1.55, 4.80, boxstyle='round,pad=0.02,rounding_size=0.02',
                                     facecolor='#FFFFFF', edgecolor='#D69E2E', linewidth=1.2)
    ax.add_patch(cat_box)
    ax.text(8.32, 8.10, 'Feature Concat', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    cat_content = (
        r'$f_{\mathrm{cnn}} \in \mathbb{R}^d$' + '\n\n' +
        r'$f_{\mathrm{gru}} \in \mathbb{R}^d$' + '\n\n' +
        r'$f_{\mathrm{kan}} \in \mathbb{R}^d$' + '\n\n' +
        r'Pos Emb $\mathrm{Pos}_h$' + '\n\n' +
        r'Context $[\mu_X, \sigma_X]$'
    )
    ax.text(8.32, 5.75, cat_content, ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000')

    # MLP Gate Box
    mlp_gate = patches.FancyBboxPatch((9.30, 4.90), 1.25, 2.70, boxstyle='round,pad=0.02,rounding_size=0.02',
                                      facecolor='#FAF089', edgecolor='#B7791F', linewidth=1.2)
    ax.add_patch(mlp_gate)
    ax.text(9.92, 7.20, 'MLP Gate', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000')
    ax.text(9.92, 6.00, '(128 units)\n+\nGELU\n+\nSoftmax\nLayer', ha='center', va='center', fontsize=10, fontweight='bold', color='#000000', linespacing=1.25)

    # Weights & Fusion Box
    fuse_box = patches.FancyBboxPatch((10.75, 3.65), 1.25, 4.80, boxstyle='round,pad=0.02,rounding_size=0.02',
                                      facecolor='#FFFFFF', edgecolor='#D69E2E', linewidth=1.2)
    ax.add_patch(fuse_box)
    ax.text(11.37, 8.10, 'Router Weights', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    fuse_content = (
        r'$w_1$ (CNN)' + '\n' +
        r'$w_2$ (GRU)' + '\n' +
        r'$w_3$ (KAN)' + '\n\n' +
        r'$\sum_{i=1}^3 w_i = 1$' + '\n\n' +
        'Fused Feature:\n' +
        r'$f_{\mathrm{fused}} = \sum w_i f_i$' + '\n' +
        r'$\in \mathbb{R}^{B \times d}$'
    )
    ax.text(11.37, 5.70, fuse_content, ha='center', va='center', fontsize=10, fontweight='bold', color='#000000', linespacing=1.25)

    # --- 4. Horizon Heads & Quantile Heads ---
    head_outer = patches.FancyBboxPatch((12.55, 3.45), 5.50, 5.75, boxstyle='round,pad=0.02,rounding_size=0.03',
                                        facecolor='#E6FFFA', edgecolor='#319795', linewidth=1.5)
    ax.add_patch(head_outer)
    ax.text(15.30, 8.85, 'Step 3: Horizon Heads & Residual Scaling', ha='center', va='center',
            fontsize=12.5, fontweight='bold', color='#000000')

    # 3 Head Specialized Cards (All text black)
    h1 = patches.FancyBboxPatch((12.70, 7.05), 2.50, 1.40, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#319795', linewidth=1.1)
    ax.add_patch(h1)
    ax.text(13.95, 8.15, 'Short Head: $h \\in \\{1, 3\\}$', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(13.95, 7.55, '• Direct Linear Projection\n• Preserves Short Momentum\n• Fast O(1) Latency Execution', 
            ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    h2 = patches.FancyBboxPatch((12.70, 5.35), 2.50, 1.50, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#319795', linewidth=1.1)
    ax.add_patch(h2)
    ax.text(13.95, 6.55, 'Medium Head: $h \\in \\{5, 7, 10\\}$', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(13.95, 5.85, '• 2-Layer MLP + GELU Act\n• Regulatory Cycle Calibration\n• Non-linear Policy Mapping', 
            ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    h3 = patches.FancyBboxPatch((12.70, 3.65), 2.50, 1.50, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#319795', linewidth=1.1)
    ax.add_patch(h3)
    ax.text(13.95, 4.85, 'Long Head: $h \\in \\{20, 60\\}$', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    ax.text(13.95, 4.15, '• Deep 3-Layer MLP + Norm\n• Extrapolation Drift Bounding\n• Strategic Term Forecast', 
            ha='center', va='center', fontsize=9.2, color='#000000', linespacing=1.2)

    # Quantile Output & Residual Bounding Box
    res_box = patches.FancyBboxPatch((15.40, 3.65), 2.50, 4.80, boxstyle='round,pad=0.02,rounding_size=0.02',
                                     facecolor='#FFFFFF', edgecolor='#319795', linewidth=1.2)
    ax.add_patch(res_box)
    ax.text(16.65, 8.10, 'Calibrated Tail Risk', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000')
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
    ax.text(16.65, 5.75, res_content, ha='center', va='center', fontsize=9.8, fontweight='bold', color='#000000', linespacing=1.25)

    # Connecting Arrows
    arr = dict(facecolor='#000000', edgecolor='#000000', width=1.8, headwidth=7, headlength=7)
    ax.annotate('', xy=(3.45, 8.20), xytext=(2.95, 7.50), arrowprops=arr)
    ax.annotate('', xy=(3.45, 6.20), xytext=(2.95, 5.90), arrowprops=arr)
    ax.annotate('', xy=(3.45, 4.30), xytext=(2.95, 4.30), arrowprops=arr)

    ax.annotate('', xy=(7.55, 7.50), xytext=(6.95, 8.20), arrowprops=arr)
    ax.annotate('', xy=(7.55, 6.20), xytext=(6.95, 6.20), arrowprops=arr)
    ax.annotate('', xy=(7.55, 4.90), xytext=(6.95, 4.30), arrowprops=arr)

    ax.annotate('', xy=(9.30, 6.25), xytext=(9.10, 6.25), arrowprops=arr)
    ax.annotate('', xy=(10.75, 6.25), xytext=(10.55, 6.25), arrowprops=arr)

    ax.annotate('', xy=(12.70, 7.75), xytext=(12.00, 6.80), arrowprops=arr)
    ax.annotate('', xy=(12.70, 6.10), xytext=(12.00, 6.10), arrowprops=arr)
    ax.annotate('', xy=(12.70, 4.40), xytext=(12.00, 5.40), arrowprops=arr)

    ax.annotate('', xy=(15.40, 6.05), xytext=(15.20, 6.05), arrowprops=arr)

    # ==========================================================================
    # PANEL (B): Architectural Paradigms of Competitive Baselines (COMPACT & SNUG)
    # ==========================================================================
    panel_bot = patches.FancyBboxPatch((0.25, 0.20), 18.0, 2.75, boxstyle='round,pad=0.02,rounding_size=0.03',
                                       facecolor='#F8FAFC', edgecolor='#718096', linewidth=1.6)
    ax.add_patch(panel_bot)

    sh_b = patches.FancyBboxPatch((0.45, 2.58), 8.5, 0.34, boxstyle='round,pad=0.02,rounding_size=0.02',
                                  facecolor='#4A5568', edgecolor='#4A5568', linewidth=1.0)
    ax.add_patch(sh_b)
    ax.text(4.70, 2.75, '(B) Architectural Paradigms of Competitive Baselines', 
            ha='center', va='center', fontsize=11, fontweight='bold', color='#FFFFFF')

    b_w = 4.15
    b_gap = 0.24
    b_start_x = 0.45
    card_h = 2.15

    # 1. PatchTST Block
    b1_x = b_start_x
    b1_box = patches.FancyBboxPatch((b1_x, 0.32), b_w, card_h, boxstyle='round,pad=0.02,rounding_size=0.02',
                                   facecolor='#FFFFFF', edgecolor='#3182CE', linewidth=1.3)
    ax.add_patch(b1_box)
    
    tab1 = patches.FancyBboxPatch((b1_x + 0.05, 2.05), b_w - 0.10, 0.38, boxstyle='round,pad=0.01,rounding_size=0.02',
                                  facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=1.0)
    ax.add_patch(tab1)
    ax.text(b1_x + b_w/2, 2.24, 'PatchTST (Transformer)', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    
    b1_text = (
        '• Channel-Independent Sub-series Patching\n'
        '• Multi-Head Self-Attention Across Patches\n'
        '• Direct Linear Projection to Horizon $H$\n'
        '• Captures Local Semantic Temporal Patterns\n'
        '• High Memory & Long-Horizon Drift at H60'
    )
    ax.text(b1_x + b_w/2, 1.20, b1_text, ha='center', va='center', fontsize=9.8, color='#000000', linespacing=1.32)

    # 2. DLinear Block
    b2_x = b_start_x + (b_w + b_gap)
    b2_box = patches.FancyBboxPatch((b2_x, 0.32), b_w, card_h, boxstyle='round,pad=0.02,rounding_size=0.02',
                                   facecolor='#FFFFFF', edgecolor='#DD6B20', linewidth=1.3)
    ax.add_patch(b2_box)
    
    tab2 = patches.FancyBboxPatch((b2_x + 0.05, 2.05), b_w - 0.10, 0.38, boxstyle='round,pad=0.01,rounding_size=0.02',
                                  facecolor='#FEEBC8', edgecolor='#DD6B20', linewidth=1.0)
    ax.add_patch(tab2)
    ax.text(b2_x + b_w/2, 2.24, 'DLinear (Decomposition)', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    
    b2_text = (
        '• Moving Average Series Trend Extraction\n'
        '• Residual Seasonal Component Extraction\n'
        '• Two Independent 1-Layer Linear Projections\n'
        '• Minimalist Architecture with $O(L)$ Cost\n'
        '• Underfits Non-linear Geopolitical Shocks'
    )
    ax.text(b2_x + b_w/2, 1.20, b2_text, ha='center', va='center', fontsize=9.8, color='#000000', linespacing=1.32)

    # 3. Recurrent + Attention Block
    b3_x = b_start_x + 2 * (b_w + b_gap)
    b3_box = patches.FancyBboxPatch((b3_x, 0.32), b_w, card_h, boxstyle='round,pad=0.02,rounding_size=0.02',
                                   facecolor='#FFFFFF', edgecolor='#805AD5', linewidth=1.3)
    ax.add_patch(b3_box)
    
    tab3 = patches.FancyBboxPatch((b3_x + 0.05, 2.05), b_w - 0.10, 0.38, boxstyle='round,pad=0.01,rounding_size=0.02',
                                  facecolor='#FAF5FF', edgecolor='#805AD5', linewidth=1.0)
    ax.add_patch(tab3)
    ax.text(b3_x + b_w/2, 2.24, 'LSTM / GRU-Attention', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    
    b3_text = (
        '• Sequential Hidden State Recursion ($h_t$)\n'
        '• Temporal Multi-Head Attention Alignment\n'
        '• Hidden Aggregation for Point Forecasts\n'
        '• Effective for Macro Trend Sequences\n'
        '• Gradient Dissipation on Long Multi-Step'
    )
    ax.text(b3_x + b_w/2, 1.20, b3_text, ha='center', va='center', fontsize=9.8, color='#000000', linespacing=1.32)

    # 4. Tree-based XGBoost Block
    b4_x = b_start_x + 3 * (b_w + b_gap)
    b4_box = patches.FancyBboxPatch((b4_x, 0.32), b_w, card_h, boxstyle='round,pad=0.02,rounding_size=0.02',
                                   facecolor='#FFFFFF', edgecolor='#38A169', linewidth=1.3)
    ax.add_patch(b4_box)
    
    tab4 = patches.FancyBboxPatch((b4_x + 0.05, 2.05), b_w - 0.10, 0.38, boxstyle='round,pad=0.01,rounding_size=0.02',
                                  facecolor='#F0FFF4', edgecolor='#38A169', linewidth=1.0)
    ax.add_patch(tab4)
    ax.text(b4_x + b_w/2, 2.24, 'XGBoost MultiOutput', ha='center', va='center', fontsize=11, fontweight='bold', color='#000000')
    
    b4_text = (
        '• Gradient Boosted Decision Tree Ensembles\n'
        '• Direct Multi-Horizon Target Regressors\n'
        '• Tabular Feature Splitting & Regularization\n'
        '• Competitive Static Tabular Baseline\n'
        '• Lacks Temporal Latent Dynamics Modeling'
    )
    ax.text(b4_x + b_w/2, 1.20, b4_text, ha='center', va='center', fontsize=9.8, color='#000000', linespacing=1.32)

    plt.tight_layout()
    fig.savefig('paper_figures/fig2_gumnethet_architecture.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("✓ Successfully generated all-black-text fig2_gumnethet_architecture.png")

generate_perfect_fig2()
