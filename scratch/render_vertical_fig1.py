import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
os.makedirs('paper_figures', exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'

def generate_vertical_fig1_perfect():
    # Width = 8.0 inches, Height = 12.34 inches (aspect ratio exactly 1.5425, matches Word's 3182112 x 4908003 EMUs)
    fig, ax = plt.subplots(figsize=(8.0, 12.34), dpi=300)
    ax.set_xlim(0, 8.0)
    ax.set_ylim(0, 12.34)
    ax.axis('off')

    # Background pure white
    fig.patch.set_facecolor('#FFFFFF')

    # --------------------------------------------------------------------------
    # TOP TITLE BANNER (White Box, Black Border, Regular Text)
    # --------------------------------------------------------------------------
    title_box = patches.FancyBboxPatch((0.20, 11.70), 7.60, 0.46, boxstyle='round,pad=0.02,rounding_size=0.03',
                                       facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.1)
    ax.add_patch(title_box)
    ax.text(4.00, 11.93, 'NEURAL NETWORK ARCHITECTURE OF GUMNetHet',
            ha='center', va='center', fontsize=12.0, fontweight='normal', color='#000000')

    # --------------------------------------------------------------------------
    # TIER 1: INPUT SEQUENCE TENSOR & PARTITIONING (y = 9.60 to 11.55)
    # --------------------------------------------------------------------------
    t1_box = patches.FancyBboxPatch((0.20, 9.60), 7.60, 1.95, boxstyle='round,pad=0.02,rounding_size=0.03',
                                    facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.0)
    ax.add_patch(t1_box)
    ax.text(4.00, 11.35, r'Step 1: Input Sequence Tensor $X \in \mathbb{R}^{B \times L \times D}$ ($L = 30$ Lookback Window)',
            ha='center', va='center', fontsize=10.5, fontweight='normal', color='#000000')

    # 3 Partition Cards (Width = 2.30, Gap = 0.15)
    # Card 1: Spot Price
    p1 = patches.FancyBboxPatch((0.35, 9.72), 2.30, 1.40, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(p1)
    ax.text(1.50, 10.88, 'Spot Price Series', ha='center', va='center', fontsize=10.0, fontweight='normal', color='#000000')
    ax.text(1.50, 10.58, r'$x^{\mathrm{CNN}} \in \mathbb{R}^{B \times L \times D_1}$', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    ax.text(1.50, 10.08, '• MG95, MG92, MG97\n• DO 0.001%, DO 0.05%\n• WTI, Brent, Naphtha',
            ha='center', va='center', fontsize=8.5, fontweight='normal', color='#000000', linespacing=1.25)

    # Card 2: Macro & GPR
    p2 = patches.FancyBboxPatch((2.85, 9.72), 2.30, 1.40, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(p2)
    ax.text(4.00, 10.88, 'Macro & GPR Risk', ha='center', va='center', fontsize=10.0, fontweight='normal', color='#000000')
    ax.text(4.00, 10.58, r'$x^{\mathrm{GRU}} \in \mathbb{R}^{B \times L \times D_2}$', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    ax.text(4.00, 10.08, '• Geopolitical Risk (GPR)\n• USD Index (DXY)\n• GPR_MA30, DXY_MA30',
            ha='center', va='center', fontsize=8.5, fontweight='normal', color='#000000', linespacing=1.25)

    # Card 3: Ratios & Volatility
    p3 = patches.FancyBboxPatch((5.35, 9.72), 2.30, 1.40, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(p3)
    ax.text(6.50, 10.88, 'Ratios & Volatility', ha='center', va='center', fontsize=10.0, fontweight='normal', color='#000000')
    ax.text(6.50, 10.58, r'$x^{\mathrm{KAN}} \in \mathbb{R}^{B \times L \times D_3}$', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    ax.text(6.50, 10.08, '• Crack Spread Ratios\n• Realized Vol (10d, 30d)\n• Day_sin, Day_cos',
            ha='center', va='center', fontsize=8.5, fontweight='normal', color='#000000', linespacing=1.25)

    # Arrows Tier 1 -> Tier 2
    arr = dict(facecolor='#000000', edgecolor='#000000', width=1.1, headwidth=4.5, headlength=4.5)
    ax.annotate('', xy=(1.50, 9.15), xytext=(1.50, 9.72), arrowprops=arr)
    ax.annotate('', xy=(4.00, 9.15), xytext=(4.00, 9.72), arrowprops=arr)
    ax.annotate('', xy=(6.50, 9.15), xytext=(6.50, 9.72), arrowprops=arr)

    # --------------------------------------------------------------------------
    # TIER 2: THREE HETEROGENEOUS SPECIALIZED EXPERTS (y = 7.40 to 9.15)
    # --------------------------------------------------------------------------
    t2_box = patches.FancyBboxPatch((0.20, 7.40), 7.60, 1.75, boxstyle='round,pad=0.02,rounding_size=0.03',
                                    facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.0)
    ax.add_patch(t2_box)
    ax.text(4.00, 8.95, 'Specialized Domain Experts (Parallel Processing)',
            ha='center', va='center', fontsize=10.5, fontweight='normal', color='#000000')

    # Expert 1 Box
    e1 = patches.FancyBboxPatch((0.35, 7.52), 2.30, 1.22, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(e1)
    ax.text(1.50, 8.55, 'Expert 1: 1D-CNN', ha='center', va='center', fontsize=10.0, fontweight='normal', color='#000000')
    e1_txt = '• Inception: $k \\in \\{3, 7, 15\\}$\n• Temporal Attention\n• ' + r'$f_{\mathrm{cnn}} \in \mathbb{R}^{B \times d}$'
    ax.text(1.50, 7.98, e1_txt, ha='center', va='center', fontsize=8.5, fontweight='normal', color='#000000', linespacing=1.28)

    # Expert 2 Box
    e2 = patches.FancyBboxPatch((2.85, 7.52), 2.30, 1.22, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(e2)
    ax.text(4.00, 8.55, 'Expert 2: GRU-Attention', ha='center', va='center', fontsize=10.0, fontweight='normal', color='#000000')
    e2_txt = '• 2-Layer Stacked GRU\n• Multi-Head Alignment\n• ' + r'$f_{\mathrm{gru}} \in \mathbb{R}^{B \times d}$'
    ax.text(4.00, 7.98, e2_txt, ha='center', va='center', fontsize=8.5, fontweight='normal', color='#000000', linespacing=1.28)

    # Expert 3 Box
    e3 = patches.FancyBboxPatch((5.35, 7.52), 2.30, 1.22, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(e3)
    ax.text(6.50, 8.55, 'Expert 3: Wavelet-KAN', ha='center', va='center', fontsize=10.0, fontweight='normal', color='#000000')
    e3_txt = '• Mexican Hat Wavelet\n• Non-linear Spline Map\n• ' + r'$f_{\mathrm{kan}} \in \mathbb{R}^{B \times d}$'
    ax.text(6.50, 7.98, e3_txt, ha='center', va='center', fontsize=8.5, fontweight='normal', color='#000000', linespacing=1.28)

    # Arrows Tier 2 -> Tier 3
    ax.annotate('', xy=(1.80, 6.95), xytext=(1.50, 7.52), arrowprops=arr)
    ax.annotate('', xy=(4.00, 6.95), xytext=(4.00, 7.52), arrowprops=arr)
    ax.annotate('', xy=(6.20, 6.95), xytext=(6.50, 7.52), arrowprops=arr)

    # --------------------------------------------------------------------------
    # TIER 3: HORIZON-AWARE DYNAMIC GATING ROUTER (y = 4.90 to 6.95)
    # --------------------------------------------------------------------------
    t3_box = patches.FancyBboxPatch((0.20, 4.90), 7.60, 2.05, boxstyle='round,pad=0.02,rounding_size=0.03',
                                    facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.0)
    ax.add_patch(t3_box)
    ax.text(4.00, 6.75, 'Step 2: Horizon-Aware Dynamic Gating Router',
            ha='center', va='center', fontsize=10.5, fontweight='normal', color='#000000')

    # Subbox 1: Concat Input
    r_cat = patches.FancyBboxPatch((0.35, 5.02), 2.10, 1.50, boxstyle='round,pad=0.01,rounding_size=0.02',
                                   facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(r_cat)
    ax.text(1.40, 6.32, 'Representation Input', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    r_cat_txt = r'$f_{\mathrm{cnn}}, f_{\mathrm{gru}}, f_{\mathrm{kan}} \in \mathbb{R}^d$' + '\n' + r'Pos Emb: $\mathrm{Pos}_h$' + '\n' + r'Context: $[\mu_X, \sigma_X]$'
    ax.text(1.40, 5.60, r_cat_txt, ha='center', va='center', fontsize=8.5, fontweight='normal', color='#000000', linespacing=1.35)

    # Subbox 2: MLP Gating
    r_mlp = patches.FancyBboxPatch((2.65, 5.02), 2.15, 1.50, boxstyle='round,pad=0.01,rounding_size=0.02',
                                   facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(r_mlp)
    ax.text(3.72, 6.32, 'MLP Gating Network', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    r_mlp_txt = 'Linear(3d+ctx, 128)\n+ GELU Activation\n+ Linear(128, 3)\n+ Softmax Layer'
    ax.text(3.72, 5.60, r_mlp_txt, ha='center', va='center', fontsize=8.2, fontweight='normal', color='#000000', linespacing=1.25)

    # Subbox 3: Dynamic Weights & Fusion
    r_fuse = patches.FancyBboxPatch((5.00, 5.02), 2.65, 1.50, boxstyle='round,pad=0.01,rounding_size=0.02',
                                    facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(r_fuse)
    ax.text(6.32, 6.32, 'Dynamic Fusion', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    r_fuse_txt = (
        r'Weights: $w_1, w_2, w_3 \in [0, 1]$' + '\n' +
        r'Constraint: $\sum_{i=1}^3 w_i = 1$' + '\n' +
        r'Fused: $f_{\mathrm{fused}} = \sum w_i f_i \in \mathbb{R}^{B \times d}$' + '\n' +
        r'Shock: $w_{\mathrm{kan}}$ surges in top GPR'
    )
    ax.text(6.32, 5.60, r_fuse_txt, ha='center', va='center', fontsize=8.0, fontweight='normal', color='#000000', linespacing=1.30)

    # Internal Router Arrows
    ax.annotate('', xy=(2.65, 5.77), xytext=(2.45, 5.77), arrowprops=arr)
    ax.annotate('', xy=(5.00, 5.77), xytext=(4.80, 5.77), arrowprops=arr)

    # Arrow Tier 3 -> Tier 4
    ax.annotate('', xy=(4.00, 4.45), xytext=(4.00, 4.90), arrowprops=arr)

    # --------------------------------------------------------------------------
    # TIER 4: HORIZON-SPECIALIZED OUTPUT HEADS (y = 2.60 to 4.45)
    # --------------------------------------------------------------------------
    t4_box = patches.FancyBboxPatch((0.20, 2.60), 7.60, 1.85, boxstyle='round,pad=0.02,rounding_size=0.03',
                                    facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.0)
    ax.add_patch(t4_box)
    ax.text(4.00, 4.25, 'Step 3: Horizon-Specialized Output Prediction Heads',
            ha='center', va='center', fontsize=10.5, fontweight='normal', color='#000000')

    # Head 1
    h1 = patches.FancyBboxPatch((0.35, 2.72), 2.30, 1.30, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(h1)
    ax.text(1.50, 3.82, 'Short Head: $h \\in \\{1, 3\\}$', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    h1_txt = '• Linear Projection\n• Preserves Momentum\n• Fast $O(1)$ Execution'
    ax.text(1.50, 3.22, h1_txt, ha='center', va='center', fontsize=8.2, fontweight='normal', color='#000000', linespacing=1.25)

    # Head 2
    h2 = patches.FancyBboxPatch((2.85, 2.72), 2.30, 1.30, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(h2)
    ax.text(4.00, 3.82, 'Medium Head: $h \\in \\{5, 7, 10\\}$', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    h2_txt = '• 2-Layer MLP + GELU\n• Fuel Cycle Alignment\n• Non-linear Policy Map'
    ax.text(4.00, 3.22, h2_txt, ha='center', va='center', fontsize=8.2, fontweight='normal', color='#000000', linespacing=1.25)

    # Head 3
    h3 = patches.FancyBboxPatch((5.35, 2.72), 2.30, 1.30, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(h3)
    ax.text(6.50, 3.82, 'Long Head: $h \\in \\{20, 60\\}$', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    h3_txt = '• Deep 3-Layer MLP\n• LayerNorm + Drift Bound\n• Strategic Long Trend'
    ax.text(6.50, 3.22, h3_txt, ha='center', va='center', fontsize=8.2, fontweight='normal', color='#000000', linespacing=1.25)

    # Arrow Tier 4 -> Tier 5
    ax.annotate('', xy=(4.00, 2.15), xytext=(4.00, 2.60), arrowprops=arr)

    # --------------------------------------------------------------------------
    # TIER 5: CALIBRATED TAIL RISK & INVERSE PRICE MAPPING (y = 0.25 to 2.15)
    # --------------------------------------------------------------------------
    t5_box = patches.FancyBboxPatch((0.20, 0.25), 7.60, 1.90, boxstyle='round,pad=0.02,rounding_size=0.03',
                                    facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.0)
    ax.add_patch(t5_box)
    ax.text(4.00, 1.95, 'Step 4: Calibrated Multi-Quantile Tail Risk & Price Reconstruction',
            ha='center', va='center', fontsize=10.5, fontweight='normal', color='#000000')

    # Output Card 1: Quantile formulation
    o1 = patches.FancyBboxPatch((0.35, 0.38), 3.50, 1.35, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(o1)
    ax.text(2.10, 1.52, 'Quantile Returns & Residual Scaling', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    o1_txt = (
        r'$\hat{y}_{t+h}^{(q)} = \mathrm{Head}_q(f_{\mathrm{fused}}) + \gamma_h \cdot x_t^{\mathrm{target}}$' + '\n' +
        r'Quantile Grid: $q \in \{0.1, 0.5, 0.9\}$ ($80\%$ Prediction Interval)' + '\n' +
        r'Pinball Loss Optimization + Calibrated $\mathrm{PICP}=82.4\%$'
    )
    ax.text(2.10, 0.92, o1_txt, ha='center', va='center', fontsize=8.2, fontweight='normal', color='#000000', linespacing=1.35)

    # Output Card 2: Price Mapping
    o2 = patches.FancyBboxPatch((4.15, 0.38), 3.50, 1.35, boxstyle='round,pad=0.01,rounding_size=0.02',
                                facecolor='#FFFFFF', edgecolor='#000000', linewidth=0.8)
    ax.add_patch(o2)
    ax.text(5.90, 1.52, 'Physical Oil Price Reconstruction', ha='center', va='center', fontsize=9.5, fontweight='normal', color='#000000')
    o2_txt = (
        r'Log-Price Inversion: $\hat{P}_{t+h, c} = P_{t, c} \cdot \exp(\hat{R}_{t \to t+h, c})$' + '\n' +
        r'Output Shape: $(B, C \times |\mathcal{Q}|)$ across 7 Lead Horizons' + '\n' +
        'Guaranteed Non-Negative Price Levels & Bounded Volatility'
    )
    ax.text(5.90, 0.92, o2_txt, ha='center', va='center', fontsize=8.2, fontweight='normal', color='#000000', linespacing=1.35)

    plt.tight_layout()
    output_path = 'paper_figures/fig1_gumnethet_vertical.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close(fig)
    print(f"Successfully generated perfect vertical architecture Figure 1: {output_path}")

generate_vertical_fig1_perfect()
