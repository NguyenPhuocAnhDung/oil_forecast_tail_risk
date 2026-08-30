import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_flawless_ieee_architecture(out_path='scratch/images/image1.png'):
    # Canvas size: 6.0 x 9.2 inches at 300 DPI
    fig, ax = plt.subplots(figsize=(6.0, 9.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['mathtext.fontset'] = 'dejavusans'
    
    # -------------------------------------------------------------------------
    # MAIN HEADER BANNER (Y: 95.0 to 99.0)
    # -------------------------------------------------------------------------
    title_box = patches.FancyBboxPatch((2, 95.0), 96, 4.0, boxstyle="square,pad=0",
                                      facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.1)
    ax.add_patch(title_box)
    ax.text(50, 97.0, "GUMNetHet & Baseline Paradigms", 
            color="#000000", fontsize=11.5, fontweight='normal', ha='center', va='center')

    # =========================================================================
    # PANEL (A): GUMNetHet Architecture (Y: 23.5 to 93.5)
    # =========================================================================
    panel_a = patches.FancyBboxPatch((2, 23.5), 96, 70.0, boxstyle="square,pad=0",
                                    facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.1)
    ax.add_patch(panel_a)
    
    # Panel A Title
    ax.text(4, 91.5, "(A) GUMNetHet: Heterogeneous Mixture of Local-Global Experts", 
            fontsize=9.5, fontweight='normal', color="#000000", ha='left', va='center')
    ax.plot([4, 96], [90.0, 90.0], color="#000000", linewidth=0.5)

    # -------------------------------------------------------------------------
    # (A.1) Stage 1: Input Sequence & Partitioning (Y: 76.5 to 89.0)
    # -------------------------------------------------------------------------
    ax.text(50, 88.0, r"Stage 1: Input Sequence & Feature Partitioning ($L = 30$ Days)", 
            fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center')
    
    p_w = 29.5
    # Sub-box 1: Spot Price
    b1 = patches.FancyBboxPatch((4, 77.0), p_w, 9.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b1)
    ax.plot([4, 4 + p_w], [83.5, 83.5], color="#444444", linewidth=0.5)
    ax.text(4 + p_w/2, 84.8, "Spot Prices", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(4 + p_w/2, 80.2, "• MG95, MG92, Gasoil\n• WTI, Brent, Naphtha", fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 2: Macro & GPR
    b2 = patches.FancyBboxPatch((35.25, 77.0), p_w, 9.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b2)
    ax.plot([35.25, 35.25 + p_w], [83.5, 83.5], color="#444444", linewidth=0.5)
    ax.text(35.25 + p_w/2, 84.8, "Macro & GPR", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(35.25 + p_w/2, 80.2, "• Geopolitical Risk\n• DXY Index, MA30", fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 3: Shocks & Volatility
    b3 = patches.FancyBboxPatch((66.5, 77.0), p_w, 9.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b3)
    ax.plot([66.5, 66.5 + p_w], [83.5, 83.5], color="#444444", linewidth=0.5)
    ax.text(66.5 + p_w/2, 84.8, "Crack & Volatility", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(66.5 + p_w/2, 80.2, r"• Crack Spread Ratios" + "\n" + r"• $\mathrm{Vol}_{10\mathrm{d}}, \mathrm{Vol}_{30\mathrm{d}}$", fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Down Arrows from Stage 1 to Stage 2
    for xc in [4 + p_w/2, 35.25 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(xc, 72.8), xytext=(xc, 77.0),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.2, mutation_scale=9))

    # -------------------------------------------------------------------------
    # (A.2) Stage 2: Three Domain Experts (Y: 53.0 to 72.8)
    # -------------------------------------------------------------------------
    # Expert 1: 1D-CNN
    exp1 = patches.FancyBboxPatch((4, 53.5), p_w, 19.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(exp1)
    ax.text(4 + p_w/2, 70.8, "Expert 1: 1D-CNN", fontsize=9.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([5.5, 4 + p_w - 1.5], [69.2, 69.2], color="#CCCCCC", linewidth=0.5)
    ax.text(4 + p_w/2, 61.2, 
            r"• Kernels: $k \in \{3, 7, 15\}$" + "\n"
            r"• Temporal Inception" + "\n"
            r"• LayerNorm + Attention" + "\n\n"
            r"Output: $f_{\mathrm{cnn}} \in \mathbb{R}^d$", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 2: GRU-Attention
    exp2 = patches.FancyBboxPatch((35.25, 53.5), p_w, 19.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(exp2)
    ax.text(35.25 + p_w/2, 70.8, "Expert 2: GRU-Attn", fontsize=9.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([36.75, 35.25 + p_w - 1.5], [69.2, 69.2], color="#CCCCCC", linewidth=0.5)
    ax.text(35.25 + p_w/2, 61.2, 
            r"• 2-Layer Stacked GRU" + "\n"
            r"• Multi-Head Attention" + "\n"
            r"• Context Memory $L=30$" + "\n\n"
            r"Output: $f_{\mathrm{gru}} \in \mathbb{R}^d$", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 3: Wavelet-KAN
    exp3 = patches.FancyBboxPatch((66.5, 53.5), p_w, 19.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(exp3)
    ax.text(66.5 + p_w/2, 70.8, "Expert 3: Wav-KAN", fontsize=9.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([68.0, 66.5 + p_w - 1.5], [69.2, 69.2], color="#CCCCCC", linewidth=0.5)
    ax.text(66.5 + p_w/2, 61.2, 
            r"• Kolmogorov–Arnold Net" + "\n"
            r"• Mexican Hat Wavelet:" + "\n"
            r"  $\psi(z)=(1-z^2)e^{-0.5 z^2}$" + "\n\n"
            r"Output: $f_{\mathrm{kan}} \in \mathbb{R}^d$", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Converging Arrows from Stage 2 to Stage 3
    for xc in [4 + p_w/2, 35.25 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(50, 49.5), xytext=(xc, 53.5),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.2, mutation_scale=9))

    # -------------------------------------------------------------------------
    # (A.3) Stage 3: Horizon-Aware Dynamic Gating Router (Y: 38.0 to 49.5)
    # ZERO OVERLAP: Separate text elements with clean vertical spacing!
    # -------------------------------------------------------------------------
    r_box = patches.FancyBboxPatch((4, 38.5), 92, 11.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(r_box)
    
    # Left inside router
    ax.text(26.0, 44.0, 
            r"Router Input Conditioning:" + "\n" + 
            r"• $\mathbf{x}_{\mathrm{in}} = [f_{\mathrm{cnn}}, f_{\mathrm{gru}}, f_{\mathrm{kan}}]$" + "\n" + 
            r"• Positional Embedding: $\mathrm{Pos}_h$" + "\n" + 
            r"• Global Context: $[\mu_x, \sigma_x]$", 
            fontsize=7.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Center Arrow
    ax.annotate('', xy=(52.0, 44.0), xytext=(47.0, 44.0),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.3, mutation_scale=10))

    # Right inside router (Clean separated lines, NO overlapping math symbols!)
    ax.text(74.0, 46.8, r"MLP Gating Network ($d = 128$)", fontsize=7.6, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(74.0, 44.0, r"Softmax Weights: $w_1 + w_2 + w_3 = 1$", fontsize=7.6, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(74.0, 41.2, r"Fused Output: $f_{\mathrm{fused}} = \sum w_j f_j \in \mathbb{R}^d$", fontsize=7.6, fontweight='normal', color="#000000", ha='center', va='center')

    # Down Arrow from Router to Heads
    ax.annotate('', xy=(50, 35.0), xytext=(50, 38.5),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.3, mutation_scale=10))

    # -------------------------------------------------------------------------
    # (A.4) Stage 4: Horizon Heads & Quantile Output (Y: 24.5 to 35.0)
    # ZERO OVERLAP: Increased height, ample padding on all sides!
    # -------------------------------------------------------------------------
    h_w = 21.5
    h_h = 10.2
    
    # Head 1: Short
    hb1 = patches.FancyBboxPatch((4.0, 24.5), h_w, h_h, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(hb1)
    ax.plot([4.0, 4.0 + h_w], [32.5, 32.5], color="#555555", linewidth=0.4)
    ax.text(4.0 + h_w/2, 33.6, r"Short: $H \in \{1, 3\}$", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(4.0 + h_w/2, 28.5, r"• Linear Projection" + "\n" + r"• Preserves Momentum" + "\n" + r"• $\mathrm{DA} > 90\%$", fontsize=7.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 2: Medium
    hb2 = patches.FancyBboxPatch((27.5, 24.5), h_w, h_h, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(hb2)
    ax.plot([27.5, 27.5 + h_w], [32.5, 32.5], color="#555555", linewidth=0.4)
    ax.text(27.5 + h_w/2, 33.6, r"Med: $H \in \{5, 7, 10\}$", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(27.5 + h_w/2, 28.5, "• 2-Layer MLP + GELU\n• 7-Day Cycle Revision\n• Pricing Calibration", fontsize=7.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 3: Long
    hb3 = patches.FancyBboxPatch((51.0, 24.5), h_w, h_h, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(hb3)
    ax.plot([51.0, 51.0 + h_w], [32.5, 32.5], color="#555555", linewidth=0.4)
    ax.text(51.0 + h_w/2, 33.6, r"Long: $H \in \{20, 60\}$", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(51.0 + h_w/2, 28.5, r"• 3-Layer Deep MLP" + "\n" + r"• Residual Scaling $\gamma_h$" + "\n" + r"• Suppresses Drift", fontsize=7.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 4: Calibrated Quantile Output
    hb4 = patches.FancyBboxPatch((74.5, 24.5), h_w, h_h, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.8)
    ax.add_patch(hb4)
    ax.plot([74.5, 74.5 + h_w], [32.5, 32.5], color="#000000", linewidth=0.5)
    ax.text(74.5 + h_w/2, 33.6, "Quantile Output", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(74.5 + h_w/2, 28.5, r"• $q \in \{0.1, 0.5, 0.9\}$" + "\n" + r"• $\hat{P}_{t+h} = P_t e^{\hat{r}}$" + "\n" + r"• $\mathrm{PICP} = 82.4\%$", fontsize=7.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # =========================================================================
    # PANEL (B): Architectural Paradigms of Competitive Baselines (Y: 2.0 to 22.0)
    # ZERO OVERLAP: Generous box height and ample padding!
    # =========================================================================
    panel_b = patches.FancyBboxPatch((2, 2.0), 96, 20.0, boxstyle="square,pad=0",
                                    facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.1)
    ax.add_patch(panel_b)
    
    # Panel B Title
    ax.text(4, 20.2, "(B) Architectural Paradigms of Competitive Baselines", 
            fontsize=9.5, fontweight='normal', color="#000000", ha='left', va='center')
    ax.plot([4, 96], [18.8, 18.8], color="#000000", linewidth=0.5)

    # 4 Baseline Cards (Height = 14.5, perfectly contains 3-4 clean lines with 30% margin!)
    card_w = 21.5
    card_h = 14.5
    
    # Baseline 1: PatchTST
    b1_x = 4.0
    b1_c = patches.FancyBboxPatch((b1_x, 3.2), card_w, card_h, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(b1_c)
    ax.text(b1_x + card_w/2, 15.8, "PatchTST", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b1_x + 1, b1_x + card_w - 1], [14.4, 14.4], color="#CCCCCC", linewidth=0.4)
    ax.text(b1_x + card_w/2, 8.8, 
            "• Sub-series Patching\n• Multi-Head Self-Attn\n• Direct Projection to H\n• Local Semantic Pattern", 
            fontsize=6.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Baseline 2: DLinear
    b2_x = 27.5
    b2_c = patches.FancyBboxPatch((b2_x, 3.2), card_w, card_h, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(b2_c)
    ax.text(b2_x + card_w/2, 15.8, "DLinear", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b2_x + 1, b2_x + card_w - 1], [14.4, 14.4], color="#CCCCCC", linewidth=0.4)
    ax.text(b2_x + card_w/2, 8.8, 
            "• Trend/Season Decomp\n• 2 Linear Projections\n• Minimalist O(L) Cost\n• Underfits Shock Jumps", 
            fontsize=6.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Baseline 3: LSTM / GRU-Attention
    b3_x = 51.0
    b3_c = patches.FancyBboxPatch((b3_x, 3.2), card_w, card_h, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(b3_c)
    ax.text(b3_x + card_w/2, 15.8, "GRU-Attention", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b3_x + 1, b3_x + card_w - 1], [14.4, 14.4], color="#CCCCCC", linewidth=0.4)
    ax.text(b3_x + card_w/2, 8.8, 
            r"• Hidden State ($h_t$)" + "\n" + r"• Temporal Attention" + "\n" + r"• Macro Trend Sequences" + "\n" + r"• Gradient Dissipation", 
            fontsize=6.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Baseline 4: XGBoost MultiOutput
    b4_x = 74.5
    b4_c = patches.FancyBboxPatch((b4_x, 3.2), card_w, card_h, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(b4_c)
    ax.text(b4_x + card_w/2, 15.8, "XGBoost", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b4_x + 1, b4_x + card_w - 1], [14.4, 14.4], color="#CCCCCC", linewidth=0.4)
    ax.text(b4_x + card_w/2, 8.8, 
            "• Boosted Tree Ensemble\n• Multi-Target Regressors\n• Tabular Feature Splits\n• Static Non-Temporal", 
            fontsize=6.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated FLAWLESS, ZERO-OVERLAP architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_flawless_ieee_architecture('scratch/images/image1.png')
