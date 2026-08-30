import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_latex_math_architecture_diagram(out_path='scratch/images/image1.png'):
    # Canvas size: 7.5 x 9.6 inches at 300 DPI
    fig, ax = plt.subplots(figsize=(7.5, 9.6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['mathtext.fontset'] = 'dejavusans'
    
    # -------------------------------------------------------------------------
    # 1. Main Title Box (Y: 94.0 to 99.0)
    # -------------------------------------------------------------------------
    title_box = patches.FancyBboxPatch((3, 94.0), 94, 5.0, boxstyle="square,pad=0",
                                      facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(title_box)
    ax.text(50, 96.5, "GUMNetHet Architecture Overview", 
            color="#000000", fontsize=11.5, fontweight='normal', ha='center', va='center')

    # Helper function for drawing outer section wrappers (NO BOLD)
    def draw_section_box(x, y, w, h, title):
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.1)
        ax.add_patch(card)
        
        # Header banner inside wrapper
        header_h = 3.6
        header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, 
                                       boxstyle="square,pad=0",
                                       facecolor="#F8FAFC", edgecolor="#000000", linewidth=0.8)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - header_h/2, title, color="#000000", fontsize=9.2, fontweight='normal', ha='center', va='center')

    # -------------------------------------------------------------------------
    # STAGE 1: INPUT SEQUENCE & DOMAIN PARTITIONING (Y: 76.5 to 91.5)
    # -------------------------------------------------------------------------
    draw_section_box(3, 76.5, 94, 15.0, r"Stage 1: Input Sequence & Feature Partitioning ($L = 30$ Days)")
    
    p_w = 28.5
    # Sub-box 1: Spot Price
    b1 = patches.FancyBboxPatch((5, 77.8), p_w, 9.8, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b1)
    ax.plot([5, 5 + p_w], [84.4, 84.4], color="#444444", linewidth=0.5)
    ax.text(5 + p_w/2, 85.8, "Spot Prices", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(5 + p_w/2, 81.0, "• MG95, MG92\n• Gasoil, WTI, Brent", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 2: Macro & GPR
    b2 = patches.FancyBboxPatch((35.75, 77.8), p_w, 9.8, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b2)
    ax.plot([35.75, 35.75 + p_w], [84.4, 84.4], color="#444444", linewidth=0.5)
    ax.text(35.75 + p_w/2, 85.8, "Macro & GPR", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(35.75 + p_w/2, 81.0, "• GPR Risk Index\n• DXY Index, MA30", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 3: Shocks & Volatility
    b3 = patches.FancyBboxPatch((66.5, 77.8), p_w, 9.8, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b3)
    ax.plot([66.5, 66.5 + p_w], [84.4, 84.4], color="#444444", linewidth=0.5)
    ax.text(66.5 + p_w/2, 85.8, "Crack & Volatility", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(66.5 + p_w/2, 81.0, r"• Crack Margins" + "\n" + r"• $\mathrm{Vol}_{10\mathrm{d}}$, $\mathrm{Vol}_{30\mathrm{d}}$", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Down Arrows from Stage 1 to Stage 2
    for xc in [5 + p_w/2, 35.75 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(xc, 72.0), xytext=(xc, 76.5),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.3, mutation_scale=11))

    # -------------------------------------------------------------------------
    # STAGE 2: THREE HETEROGENEOUS DOMAIN EXPERTS (Y: 49.0 to 72.0)
    # -------------------------------------------------------------------------
    # Expert 1: 1D-CNN
    exp1 = patches.FancyBboxPatch((5, 49.5), p_w, 22.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.0)
    ax.add_patch(exp1)
    h1 = patches.FancyBboxPatch((5, 68.2), p_w, 3.8, boxstyle="square,pad=0", facecolor="#F8FAFC", edgecolor="#000000", linewidth=0.7)
    ax.add_patch(h1)
    ax.text(5 + p_w/2, 70.1, "Expert 1: 1D-CNN", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(5 + p_w/2, 65.8, "Price Momentum", fontsize=7.8, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([6.5, 5 + p_w - 1.5], [64.2, 64.2], color="#DDDDDD", linewidth=0.5)
    ax.text(5 + p_w/2, 56.5, 
            r"• Kernels: $k \in \{3, 7, 15\}$" + "\n"
            r"• Temporal Convolutions" + "\n"
            r"• LayerNorm + Dropout" + "\n"
            r"• Softmax Attention" + "\n\n"
            r"Output: $f_{\mathrm{cnn}} \in \mathbb{R}^{128}$", 
            fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Expert 2: GRU-Attention
    exp2 = patches.FancyBboxPatch((35.75, 49.5), p_w, 22.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.0)
    ax.add_patch(exp2)
    h2 = patches.FancyBboxPatch((35.75, 68.2), p_w, 3.8, boxstyle="square,pad=0", facecolor="#F8FAFC", edgecolor="#000000", linewidth=0.7)
    ax.add_patch(h2)
    ax.text(35.75 + p_w/2, 70.1, "Expert 2: GRU-Attn", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(35.75 + p_w/2, 65.8, "Macroeconomic Regime", fontsize=7.8, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([37.25, 35.75 + p_w - 1.5], [64.2, 64.2], color="#DDDDDD", linewidth=0.5)
    ax.text(35.75 + p_w/2, 56.5, 
            r"• 2-Layer Stacked GRU" + "\n"
            r"• Hidden Dim: $d = 128$" + "\n"
            r"• Multi-Head Attention" + "\n"
            r"• Memory over $L = 30$" + "\n\n"
            r"Output: $f_{\mathrm{gru}} \in \mathbb{R}^{128}$", 
            fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Expert 3: Wavelet-KAN
    exp3 = patches.FancyBboxPatch((66.5, 49.5), p_w, 22.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.0)
    ax.add_patch(exp3)
    h3 = patches.FancyBboxPatch((66.5, 68.2), p_w, 3.8, boxstyle="square,pad=0", facecolor="#F8FAFC", edgecolor="#000000", linewidth=0.7)
    ax.add_patch(h3)
    ax.text(66.5 + p_w/2, 70.1, "Expert 3: Wav-KAN", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(66.5 + p_w/2, 65.8, "Non-Linear Shocks", fontsize=7.8, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([68.0, 66.5 + p_w - 1.5], [64.2, 64.2], color="#DDDDDD", linewidth=0.5)
    ax.text(66.5 + p_w/2, 56.5, 
            r"• Kolmogorov–Arnold Net" + "\n"
            r"• Mexican Hat Wavelet:" + "\n"
            r"  $\psi(z) = (1 - z^2)e^{-0.5 z^2}$" + "\n"
            r"• Shock Dampening" + "\n\n"
            r"Output: $f_{\mathrm{kan}} \in \mathbb{R}^{128}$", 
            fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Converging Arrows from Stage 2 to Stage 3
    for xc in [5 + p_w/2, 35.75 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(50, 45.0), xytext=(xc, 49.5),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.3, mutation_scale=11))

    # -------------------------------------------------------------------------
    # STAGE 3: HORIZON-AWARE DYNAMIC GATING ROUTER (Y: 27.5 to 45.0)
    # -------------------------------------------------------------------------
    draw_section_box(3, 27.5, 94, 17.5, "Stage 2: Horizon-Aware Dynamic Gating Router")
    
    # Left Box inside Router: Inputs
    r_in = patches.FancyBboxPatch((5.0, 29.0), 41.0, 11.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(r_in)
    ax.text(5.0 + 20.5, 34.8, 
            r"Router Input Conditioning:" + "\n"
            r"• $\mathbf{x}_{\mathrm{in}} = [f_{\mathrm{cnn}}, f_{\mathrm{gru}}, f_{\mathrm{kan}}]$" + "\n"
            r"• Positional Embedding: $\mathrm{Pos}_h$" + "\n"
            r"• Summary Statistics: $[\mu_x, \sigma_x]$", 
            fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Center Arrow
    ax.annotate('', xy=(52.0, 34.8), xytext=(47.0, 34.8),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5, mutation_scale=12))

    # Right Box inside Router: Gating MLP + Softmax
    r_out = patches.FancyBboxPatch((53.0, 29.0), 42.0, 11.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(r_out)
    ax.text(53.0 + 21.0, 34.8, 
            r"MLP Gating Network ($d = 128$)" + "\n"
            r"Softmax Weights: $\sum_{j=1}^3 w_j = 1$" + "\n"
            r"Fused: $f_{\mathrm{fused}} = \sum w_j f_j \in \mathbb{R}^{128}$", 
            fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Down Arrow from Stage 3 to Stage 4
    ax.annotate('', xy=(50, 23.0), xytext=(50, 27.5),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5, mutation_scale=12))

    # -------------------------------------------------------------------------
    # STAGE 4: MULTI-HORIZON HEADS & QUANTILE OUTPUTS (Y: 1.5 to 23.0)
    # -------------------------------------------------------------------------
    draw_section_box(3, 1.5, 94, 21.5, "Stage 3: Multi-Horizon Heads & Calibrated Quantile Outputs")

    # 4 Horizon/Tail Sub-boxes
    h_w = 20.8
    # Head 1: Short
    hb1 = patches.FancyBboxPatch((5.0, 2.8), h_w, 15.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(hb1)
    ax.plot([5.0, 5.0 + h_w], [14.0, 14.0], color="#444444", linewidth=0.5)
    ax.text(5.0 + h_w/2, 15.6, r"Short: $H \in \{1, 3\}$", fontsize=8.4, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(5.0 + h_w/2, 8.4, 
            "• Linear Projection\n• Preserves Momentum\n• Fast " + r"$O(1)$" + " Latency\n• " + r"$\mathrm{DA} > 90\%$", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Head 2: Medium
    hb2 = patches.FancyBboxPatch((27.75, 2.8), h_w, 15.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(hb2)
    ax.plot([27.75, 27.75 + h_w], [14.0, 14.0], color="#444444", linewidth=0.5)
    ax.text(27.75 + h_w/2, 15.6, r"Med: $H \in \{5, 7, 10\}$", fontsize=8.4, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(27.75 + h_w/2, 8.4, 
            "• 2-Layer MLP + GELU\n• 7-Day Cycle Alignment\n• Non-linear Price Shift\n• Smooth Transition", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Head 3: Long
    hb3 = patches.FancyBboxPatch((50.5, 2.8), h_w, 15.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(hb3)
    ax.plot([50.5, 50.5 + h_w], [14.0, 14.0], color="#444444", linewidth=0.5)
    ax.text(50.5 + h_w/2, 15.6, r"Long: $H \in \{20, 60\}$", fontsize=8.4, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(50.5 + h_w/2, 8.4, 
            r"• 3-Layer Deep MLP" + "\n"
            r"• Layer Normalization" + "\n"
            r"• Residual Scaling $\gamma_h$" + "\n"
            r"• Suppresses Drift", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Head 4: Calibrated Quantile Output
    hb4 = patches.FancyBboxPatch((73.25, 2.8), 21.75, 15.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(hb4)
    ax.plot([73.25, 73.25 + 21.75], [14.0, 14.0], color="#000000", linewidth=0.6)
    ax.text(73.25 + 10.875, 15.6, "Quantile Tail Bounds", fontsize=8.4, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(73.25 + 10.875, 8.4, 
            r"• $q \in \{0.1, 0.5, 0.9\}$" + "\n"
            r"• $\hat{y}^{(q)} = \mathrm{Head} + \gamma_h x_t$" + "\n"
            r"• $\hat{P}_{t+h} = P_t e^{\hat{r}}$" + "\n"
            r"• $\mathrm{PICP} = 82.4\%$", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated clean LaTeX math architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_latex_math_architecture_diagram('scratch/images/image1.png')
