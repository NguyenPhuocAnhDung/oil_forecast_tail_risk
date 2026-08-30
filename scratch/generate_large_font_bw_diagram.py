import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_large_font_bw_architecture(out_path='scratch/images/image1.png'):
    # Compact canvas: 7.2 inches wide by 8.8 inches tall, 300 DPI
    # This guarantees that when embedded at 3.48 inches in Word,
    # a 10.5pt font scales down to ~5.2pt relative to 8.5x11, but fills the box nicely!
    fig, ax = plt.subplots(figsize=(7.2, 8.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # 1. Main Title Box (Y: 94 to 99)
    title_box = patches.FancyBboxPatch((2, 93.5), 96, 5.5, boxstyle="square,pad=0",
                                      facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.5)
    ax.add_patch(title_box)
    ax.text(50, 96.2, "GUMNetHet: Heterogeneous Mixture-of-Experts Architecture", 
            color="#000000", fontsize=11.5, fontweight='bold', ha='center', va='center')

    # Helper function for drawing clean IEEE cards
    def draw_card(x, y, w, h, title):
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
        ax.add_patch(card)
        
        # Header banner inside card
        header_h = 3.8
        header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, 
                                       boxstyle="square,pad=0",
                                       facecolor="#F1F5F9", edgecolor="#000000", linewidth=0.8)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - header_h/2, title, color="#000000", fontsize=9.5, fontweight='bold', ha='center', va='center')

    # =========================================================================
    # STAGE 1: INPUT SEQUENCE & DOMAIN PARTITIONING (Y: 75 to 91.5)
    # =========================================================================
    draw_card(2, 75, 96, 16.5, "STAGE 1: INPUT SEQUENCE & DOMAIN PARTITIONING (L = 30 Days)")
    
    p_w = 29.5
    # Sub-box 1: Spot Price
    b1 = patches.FancyBboxPatch((4, 76.5), p_w, 11.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=0.8)
    ax.add_patch(b1)
    ax.plot([4, 4 + p_w], [84.2, 84.2], color="#333333", linewidth=0.6)
    ax.text(4 + p_w/2, 85.8, "Spot & Benchmarks", fontsize=9.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(4 + p_w/2, 80.2, 
            "• Mogas 95, Mogas 92\n• Gasoil 0.001%S, 0.05%S\n• WTI, Brent, Naphtha", 
            fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Sub-box 2: Macro & GPR
    b2 = patches.FancyBboxPatch((35.25, 76.5), p_w, 11.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=0.8)
    ax.add_patch(b2)
    ax.plot([35.25, 35.25 + p_w], [84.2, 84.2], color="#333333", linewidth=0.6)
    ax.text(35.25 + p_w/2, 85.8, "Macro & Geopolitical", fontsize=9.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(35.25 + p_w/2, 80.2, 
            "• Geopolitical Risk (GPR)\n• US Dollar Index (DXY)\n• Rolling Trend (MA30)", 
            fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Sub-box 3: Shocks & Volatility
    b3 = patches.FancyBboxPatch((66.5, 76.5), p_w, 11.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=0.8)
    ax.add_patch(b3)
    ax.plot([66.5, 66.5 + p_w], [84.2, 84.2], color="#333333", linewidth=0.6)
    ax.text(66.5 + p_w/2, 85.8, "Crack-Spread & Volatility", fontsize=9.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(66.5 + p_w/2, 80.2, 
            "• Refining Crack Margins\n• Realized Vol (10d, 30d)\n• Day / Month Encodings", 
            fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Down Arrows from Stage 1 to Stage 2
    for xc in [4 + p_w/2, 35.25 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(xc, 71.0), xytext=(xc, 75.0),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5, mutation_scale=12))

    # =========================================================================
    # STAGE 2: THREE HETEROGENEOUS DOMAIN EXPERTS (Y: 48 to 71)
    # =========================================================================
    # Expert 1: 1D-CNN
    draw_card(4, 49, p_w, 22.0, "EXPERT 1: Multi-Scale 1D-CNN")
    ax.text(4 + p_w/2, 67.2, "High-Frequency Momentum", fontsize=8.0, fontstyle='italic', color="#333333", ha='center', va='center')
    ax.text(4 + p_w/2, 57.5, 
            "• Inception Kernels: 3, 7, 15\n• Temporal Feature Extractor\n• LayerNorm + Dropout (0.1)\n• Softmax Attention Pooling\n\nOutput: f_cnn ∈ R^128", 
            fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Expert 2: GRU-Attention
    draw_card(35.25, 49, p_w, 22.0, "EXPERT 2: Stacked GRU-Attn")
    ax.text(35.25 + p_w/2, 67.2, "Low-Frequency Regime", fontsize=8.0, fontstyle='italic', color="#333333", ha='center', va='center')
    ax.text(35.25 + p_w/2, 57.5, 
            "• 2-Layer Recurrent GRU\n• Hidden Dimension: d = 128\n• Multi-Head Attention Alignment\n• Context Memory over L=30\n\nOutput: f_gru ∈ R^128", 
            fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Expert 3: Wavelet-KAN
    draw_card(66.5, 49, p_w, 22.0, "EXPERT 3: Wavelet-KAN Shock")
    ax.text(66.5 + p_w/2, 67.2, "Fat-Tail & Non-Linear Shocks", fontsize=8.0, fontstyle='italic', color="#333333", ha='center', va='center')
    ax.text(66.5 + p_w/2, 57.5, 
            "• Kolmogorov–Arnold Network\n• Mexican Hat Wavelet Basis:\n  ψ(z) = (1 - z²) exp(-0.5 z²)\n• Learnable Non-linear Spline\n\nOutput: f_kan ∈ R^128", 
            fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Converging Arrows from Stage 2 to Stage 3
    for xc in [4 + p_w/2, 35.25 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(50, 44.5), xytext=(xc, 49.0),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5, mutation_scale=12))

    # =========================================================================
    # STAGE 3: HORIZON-AWARE DYNAMIC ROUTER (Y: 28.5 to 44.5)
    # =========================================================================
    draw_card(6, 29.0, 88, 15.5, "STAGE 2: HORIZON-AWARE DYNAMIC GATING ROUTER")
    
    # Left Box inside Router: Inputs
    r_in = patches.FancyBboxPatch((8.5, 30.2), 37, 10.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.8)
    ax.add_patch(r_in)
    ax.text(8.5 + 18.5, 35.4, 
            "Router Input Conditioning:\n"
            "• Concat: [f_cnn, f_gru, f_kan]\n"
            "• Positional Embedding: Pos_h\n"
            "• Global Statistics: [μ_x, σ_x]",
            fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Center Arrow
    ax.annotate('', xy=(50, 35.4), xytext=(46.5, 35.4),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.8, mutation_scale=13))

    # Right Box inside Router: Gating MLP + Softmax
    r_out = patches.FancyBboxPatch((51.5, 30.2), 40.5, 10.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.8)
    ax.add_patch(r_out)
    ax.text(51.5 + 20.25, 35.4, 
            "MLP Gating Network (128 units, GELU)\n"
            "Softmax Weights: w_1 + w_2 + w_3 = 1\n"
            "Fused Output: f_fused = Σ w_j f_j ∈ R^128",
            fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Down Arrow from Stage 3 to Stage 4
    ax.annotate('', xy=(50, 24.5), xytext=(50, 29.0),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.8, mutation_scale=13))

    # =========================================================================
    # STAGE 4: MULTI-HORIZON PROBABILISTIC HEADS & RESIDUAL SCALING (Y: 2 to 24.5)
    # =========================================================================
    draw_card(2, 2.0, 96, 22.5, "STAGE 3: HORIZON HEADS, RESIDUAL SCALING & QUANTILE TAIL OUTPUTS")

    # 4 Horizon/Tail Sub-boxes
    h_w = 21.6
    # Head 1: Short
    hb1 = patches.FancyBboxPatch((4, 3.2), h_w, 15.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(hb1)
    ax.plot([4, 4 + h_w], [15.2, 15.2], color="#444444", linewidth=0.6)
    ax.text(4 + h_w/2, 16.8, "Short Head: H ∈ {1, 3}", fontsize=8.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(4 + h_w/2, 9.2, 
            "• Direct Linear Layer\n• Preserves Momentum\n• Fast O(1) Latency\n• DA > 90% in Short Run", 
            fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Head 2: Medium
    hb2 = patches.FancyBboxPatch((28.0, 3.2), h_w, 15.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(hb2)
    ax.plot([28.0, 28.0 + h_w], [15.2, 15.2], color="#444444", linewidth=0.6)
    ax.text(28.0 + h_w/2, 16.8, "Medium: H ∈ {5, 7, 10}", fontsize=8.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(28.0 + h_w/2, 9.2, 
            "• 2-Layer MLP + GELU\n• 7-Day Cycle Alignment\n• Non-linear Pricing Shift\n• Smooth Transition", 
            fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Head 3: Long
    hb3 = patches.FancyBboxPatch((52.0, 3.2), h_w, 15.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(hb3)
    ax.plot([52.0, 52.0 + h_w], [15.2, 15.2], color="#444444", linewidth=0.6)
    ax.text(52.0 + h_w/2, 16.8, "Long: H ∈ {20, 60}", fontsize=8.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(52.0 + h_w/2, 9.2, 
            "• 3-Layer Deep MLP\n• Layer Normalization\n• Residual Scaling (γ_h)\n• Suppresses Drift at H60", 
            fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Head 4: Calibrated Quantile Output
    hb4 = patches.FancyBboxPatch((76.0, 3.2), 20.0, 15.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.0)
    ax.add_patch(hb4)
    ax.plot([76.0, 76.0 + 20.0], [15.2, 15.2], color="#000000", linewidth=0.8)
    ax.text(76.0 + 10.0, 16.8, "Quantile Output", fontsize=8.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(76.0 + 10.0, 9.2, 
            "• Grid: q ∈ {0.1, 0.5, 0.9}\n• ŷ^(q) = Head + γ_h · x_tgt\n• Price: P_hat = P · exp(r)\n• 80% PICP = 82.4%", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated large-font, un-bolded B&W architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_large_font_bw_architecture('scratch/images/image1.png')
