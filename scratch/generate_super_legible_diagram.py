import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_super_legible_ieee_architecture(out_path='scratch/images/image1.png'):
    # Compact canvas: 5.6 x 8.0 inches at 300 DPI
    # Scaled to 3.48 inches in Word, scaling ratio is 3.48/5.6 = 0.62
    # Fonts of 10-13pt scale to 6.2 - 8.1pt in Word, making text HUGE, razor sharp, and perfectly readable!
    fig, ax = plt.subplots(figsize=(5.6, 8.0), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['mathtext.fontset'] = 'dejavusans'
    
    # -------------------------------------------------------------------------
    # MAIN HEADER BANNER (Y: 94.5 to 98.8)
    # -------------------------------------------------------------------------
    title_box = patches.FancyBboxPatch((2, 94.5), 96, 4.3, boxstyle="square,pad=0",
                                      facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.1)
    ax.add_patch(title_box)
    ax.text(50, 96.65, "GUMNetHet & Baseline Paradigms", 
            color="#000000", fontsize=11.5, fontweight='normal', ha='center', va='center')

    # =========================================================================
    # PANEL (A): GUMNetHet Architecture (Y: 21.0 to 93.0)
    # =========================================================================
    panel_a = patches.FancyBboxPatch((2, 21.0), 96, 72.0, boxstyle="square,pad=0",
                                    facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.1)
    ax.add_patch(panel_a)
    
    # Panel A Title
    ax.text(4, 90.8, "(A) GUMNetHet: Heterogeneous Mixture of Local-Global Experts", 
            fontsize=9.8, fontweight='normal', color="#000000", ha='left', va='center')
    ax.plot([4, 96], [89.2, 89.2], color="#000000", linewidth=0.5)

    # -------------------------------------------------------------------------
    # (A.1) Stage 1: Input Sequence & Partitioning (Y: 75.5 to 88.0)
    # -------------------------------------------------------------------------
    ax.text(50, 87.2, r"Stage 1: Input Sequence & Feature Partitioning ($L = 30$ Days)", 
            fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    
    p_w = 29.5
    # Sub-box 1: Spot Price
    b1 = patches.FancyBboxPatch((4, 76.2), p_w, 9.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b1)
    ax.plot([4, 4 + p_w], [82.5, 82.5], color="#444444", linewidth=0.5)
    ax.text(4 + p_w/2, 83.8, "Spot Prices", fontsize=9.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(4 + p_w/2, 79.2, "• MG95, MG92, Gasoil\n• WTI, Brent, Naphtha", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 2: Macro & GPR
    b2 = patches.FancyBboxPatch((35.25, 76.2), p_w, 9.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b2)
    ax.plot([35.25, 35.25 + p_w], [82.5, 82.5], color="#444444", linewidth=0.5)
    ax.text(35.25 + p_w/2, 83.8, "Macro & GPR", fontsize=9.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(35.25 + p_w/2, 79.2, "• Geopolitical Risk\n• DXY Index, MA30", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 3: Shocks & Volatility
    b3 = patches.FancyBboxPatch((66.5, 76.2), p_w, 9.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b3)
    ax.plot([66.5, 66.5 + p_w], [82.5, 82.5], color="#444444", linewidth=0.5)
    ax.text(66.5 + p_w/2, 83.8, "Crack & Volatility", fontsize=9.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(66.5 + p_w/2, 79.2, r"• Crack Spread Ratios" + "\n" + r"• $\mathrm{Vol}_{10\mathrm{d}}, \mathrm{Vol}_{30\mathrm{d}}$", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Down Arrows from Stage 1 to Stage 2
    for xc in [4 + p_w/2, 35.25 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(xc, 72.0), xytext=(xc, 76.0),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.2, mutation_scale=9))

    # -------------------------------------------------------------------------
    # (A.2) Stage 2: Three Domain Experts (Y: 51.5 to 72.0)
    # -------------------------------------------------------------------------
    # Expert 1: 1D-CNN
    exp1 = patches.FancyBboxPatch((4, 52.0), p_w, 19.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(exp1)
    ax.text(4 + p_w/2, 69.5, "Expert 1: 1D-CNN", fontsize=9.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([5.5, 4 + p_w - 1.5], [68.0, 68.0], color="#CCCCCC", linewidth=0.5)
    ax.text(4 + p_w/2, 60.0, 
            r"• Kernels: $k \in \{3, 7, 15\}$" + "\n"
            r"• Temporal Inception" + "\n"
            r"• LayerNorm + Attention" + "\n\n"
            r"Output: $f_{\mathrm{cnn}} \in \mathbb{R}^d$", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 2: GRU-Attention
    exp2 = patches.FancyBboxPatch((35.25, 52.0), p_w, 19.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(exp2)
    ax.text(35.25 + p_w/2, 69.5, "Expert 2: GRU-Attn", fontsize=9.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([36.75, 35.25 + p_w - 1.5], [68.0, 68.0], color="#CCCCCC", linewidth=0.5)
    ax.text(35.25 + p_w/2, 60.0, 
            r"• 2-Layer Stacked GRU" + "\n"
            r"• Multi-Head Attention" + "\n"
            r"• Context Memory $L=30$" + "\n\n"
            r"Output: $f_{\mathrm{gru}} \in \mathbb{R}^d$", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 3: Wavelet-KAN
    exp3 = patches.FancyBboxPatch((66.5, 52.0), p_w, 19.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(exp3)
    ax.text(66.5 + p_w/2, 69.5, "Expert 3: Wav-KAN", fontsize=9.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([68.0, 66.5 + p_w - 1.5], [68.0, 68.0], color="#CCCCCC", linewidth=0.5)
    ax.text(66.5 + p_w/2, 60.0, 
            r"• Kolmogorov–Arnold Net" + "\n"
            r"• Mexican Hat Wavelet:" + "\n"
            r"  $\psi(z)=(1-z^2)e^{-0.5 z^2}$" + "\n\n"
            r"Output: $f_{\mathrm{kan}} \in \mathbb{R}^d$", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Converging Arrows from Stage 2 to Stage 3
    for xc in [4 + p_w/2, 35.25 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(50, 48.0), xytext=(xc, 52.0),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.2, mutation_scale=9))

    # -------------------------------------------------------------------------
    # (A.3) Stage 3: Horizon-Aware Dynamic Gating Router (Y: 37.0 to 48.0)
    # -------------------------------------------------------------------------
    r_box = patches.FancyBboxPatch((4, 37.0), 92, 10.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(r_box)
    
    # Left inside router
    ax.text(26.0, 42.25, 
            r"Router Input Conditioning:" + "\n" + 
            r"• $\mathbf{x}_{\mathrm{in}} = [f_{\mathrm{cnn}}, f_{\mathrm{gru}}, f_{\mathrm{kan}}]$" + "\n" + 
            r"• Positional Embedding: $\mathrm{Pos}_h$" + "\n" + 
            r"• Global Context: $[\mu_x, \sigma_x]$", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Center Arrow
    ax.annotate('', xy=(52.0, 42.25), xytext=(47.0, 42.25),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.3, mutation_scale=10))

    # Right inside router
    ax.text(74.0, 42.25, 
            r"MLP Gating Network ($d = 128$)" + "\n" + 
            r"Softmax Weights: $\sum_{j=1}^3 w_j = 1$" + "\n" + 
            r"Fused Output: $f_{\mathrm{fused}} = \sum w_j f_j \in \mathbb{R}^d$", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Down Arrow from Router to Heads
    ax.annotate('', xy=(50, 33.5), xytext=(50, 37.0),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.3, mutation_scale=10))

    # -------------------------------------------------------------------------
    # (A.4) Stage 4: Horizon Heads & Quantile Output (Y: 22.0 to 33.5)
    # -------------------------------------------------------------------------
    h_w = 21.5
    # Head 1: Short
    hb1 = patches.FancyBboxPatch((4.0, 22.0), h_w, 11.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(hb1)
    ax.plot([4.0, 4.0 + h_w], [30.4, 30.4], color="#555555", linewidth=0.4)
    ax.text(4.0 + h_w/2, 31.8, r"Short: $H \in \{1, 3\}$", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(4.0 + h_w/2, 26.2, r"• Linear Projection" + "\n" + r"• Preserves Momentum" + "\n" + r"• $\mathrm{DA} > 90\%$", fontsize=7.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 2: Medium
    hb2 = patches.FancyBboxPatch((27.5, 22.0), h_w, 11.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(hb2)
    ax.plot([27.5, 27.5 + h_w], [30.4, 30.4], color="#555555", linewidth=0.4)
    ax.text(27.5 + h_w/2, 31.8, r"Med: $H \in \{5, 7, 10\}$", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(27.5 + h_w/2, 26.2, "• 2-Layer MLP + GELU\n• 7-Day Cycle Revision\n• Pricing Calibration", fontsize=7.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 3: Long
    hb3 = patches.FancyBboxPatch((51.0, 22.0), h_w, 11.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(hb3)
    ax.plot([51.0, 51.0 + h_w], [30.4, 30.4], color="#555555", linewidth=0.4)
    ax.text(51.0 + h_w/2, 31.8, r"Long: $H \in \{20, 60\}$", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(51.0 + h_w/2, 26.2, r"• 3-Layer Deep MLP" + "\n" + r"• Residual Scaling $\gamma_h$" + "\n" + r"• Suppresses Drift", fontsize=7.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 4: Calibrated Quantile Output
    hb4 = patches.FancyBboxPatch((74.5, 22.0), h_w, 11.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.8)
    ax.add_patch(hb4)
    ax.plot([74.5, 74.5 + h_w], [30.4, 30.4], color="#000000", linewidth=0.5)
    ax.text(74.5 + h_w/2, 31.8, "Quantile Output", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(74.5 + h_w/2, 26.2, r"• $q \in \{0.1, 0.5, 0.9\}$" + "\n" + r"• $\hat{P}_{t+h} = P_t e^{\hat{r}}$" + "\n" + r"• $\mathrm{PICP} = 82.4\%$", fontsize=7.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # =========================================================================
    # PANEL (B): Architectural Paradigms of Competitive Baselines (Y: 2.0 to 19.5)
    # =========================================================================
    panel_b = patches.FancyBboxPatch((2, 2.0), 96, 17.5, boxstyle="square,pad=0",
                                    facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.1)
    ax.add_patch(panel_b)
    
    # Panel B Title
    ax.text(4, 17.8, "(B) Architectural Paradigms of Competitive Baselines", 
            fontsize=9.8, fontweight='normal', color="#000000", ha='left', va='center')
    ax.plot([4, 96], [16.5, 16.5], color="#000000", linewidth=0.5)

    # 4 Baseline Cards
    card_w = 21.5
    
    # Baseline 1: PatchTST
    b1_x = 4.0
    b1_c = patches.FancyBboxPatch((b1_x, 3.0), card_w, 12.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(b1_c)
    ax.text(b1_x + card_w/2, 13.5, "PatchTST", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b1_x + 1, b1_x + card_w - 1], [12.2, 12.2], color="#CCCCCC", linewidth=0.4)
    ax.text(b1_x + card_w/2, 7.5, 
            "• Sub-series Patching\n• Multi-Head Self-Attn\n• Direct Linear to H\n• Local Semantic Pattern", 
            fontsize=7.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.15)

    # Baseline 2: DLinear
    b2_x = 27.5
    b2_c = patches.FancyBboxPatch((b2_x, 3.0), card_w, 12.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(b2_c)
    ax.text(b2_x + card_w/2, 13.5, "DLinear", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b2_x + 1, b2_x + card_w - 1], [12.2, 12.2], color="#CCCCCC", linewidth=0.4)
    ax.text(b2_x + card_w/2, 7.5, 
            "• Trend/Season Decomp\n• 2 Linear Projections\n• Minimalist O(L) Cost\n• Underfits Shock Jumps", 
            fontsize=7.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.15)

    # Baseline 3: LSTM / GRU-Attention
    b3_x = 51.0
    b3_c = patches.FancyBboxPatch((b3_x, 3.0), card_w, 12.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(b3_c)
    ax.text(b3_x + card_w/2, 13.5, "GRU-Attention", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b3_x + 1, b3_x + card_w - 1], [12.2, 12.2], color="#CCCCCC", linewidth=0.4)
    ax.text(b3_x + card_w/2, 7.5, 
            r"• Hidden State ($h_t$)" + "\n" + r"• Temporal Attention" + "\n" + r"• Macro Sequence Rep" + "\n" + r"• Gradient Decay at H60", 
            fontsize=7.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.15)

    # Baseline 4: XGBoost MultiOutput
    b4_x = 74.5
    b4_c = patches.FancyBboxPatch((b4_x, 3.0), card_w, 12.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(b4_c)
    ax.text(b4_x + card_w/2, 13.5, "XGBoost", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b4_x + 1, b4_x + card_w - 1], [12.2, 12.2], color="#CCCCCC", linewidth=0.4)
    ax.text(b4_x + card_w/2, 7.5, 
            "• Boosted Tree Ensemble\n• Multi-Target Regressors\n• Tabular Feature Splits\n• Static Non-Temporal", 
            fontsize=7.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.15)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated SUPER LEGIBLE portrait architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_super_legible_ieee_architecture('scratch/images/image1.png')
