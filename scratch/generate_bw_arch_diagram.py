import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_bw_clean_architecture_diagram(out_path='scratch/images/image1.png'):
    # Figure size: 10 inches wide by 13 inches tall, 300 DPI
    fig, ax = plt.subplots(figsize=(10, 13), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 130)
    ax.axis('off')
    
    # Clean background
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # 1. Main Title Box
    title_box = patches.FancyBboxPatch((3, 122), 94, 6.5, boxstyle="square,pad=0",
                                      facecolor="#FFFFFF", edgecolor="#000000", linewidth=2.0)
    ax.add_patch(title_box)
    ax.text(50, 125.2, "GUMNetHet: Heterogeneous Mixture-of-Experts Architecture", 
            color="#000000", fontsize=12.5, fontweight='bold', ha='center', va='center')

    # Helper function for drawing classic IEEE style boxes
    def draw_ieee_card(x, y, w, h, title, subtitle=None):
        # Outer box: pure white with black border
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.5)
        ax.add_patch(card)
        
        # Header banner inside card
        header_h = 4.2
        header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, 
                                       boxstyle="square,pad=0",
                                       facecolor="#F8FAFC", edgecolor="#000000", linewidth=1.0)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - header_h/2, title, color="#000000", fontsize=10.0, fontweight='bold', ha='center', va='center')
        
        if subtitle:
            ax.text(x + w/2, y + h - header_h - 2.0, subtitle, color="#333333", fontsize=8.5, fontstyle='italic', ha='center', va='center')

    # =========================================================================
    # SECTION 1: INPUT SEQUENCE & DOMAIN PARTITIONING (Y: 98 to 119)
    # =========================================================================
    draw_ieee_card(3, 98, 94, 21, "STAGE 1: INPUT SEQUENCE & DOMAIN FEATURE PARTITIONING (L = 30 Days)")
    
    p_w = 28.6
    # Sub-box 1: Spot Price
    b1 = patches.FancyBboxPatch((5, 100), p_w, 14.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=1.0)
    ax.add_patch(b1)
    # Header line
    ax.plot([5, 5 + p_w], [111, 111], color="#333333", linewidth=0.8)
    ax.text(5 + p_w/2, 112.5, "Spot & Benchmark Prices", fontsize=9.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(5 + p_w/2, 105.5, 
            "• Mogas 95, Mogas 92\n• Gasoil 0.001%S, 0.05%S\n• WTI, Brent, Naphtha\n• Direct Cumulative Return", 
            fontsize=8.2, color="#000000", ha='center', va='center', linespacing=1.3)

    # Sub-box 2: Macro & GPR
    b2 = patches.FancyBboxPatch((35.7, 100), p_w, 14.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=1.0)
    ax.add_patch(b2)
    ax.plot([35.7, 35.7 + p_w], [111, 111], color="#333333", linewidth=0.8)
    ax.text(35.7 + p_w/2, 112.5, "Macro & Geopolitical Risk", fontsize=9.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(35.7 + p_w/2, 105.5, 
            "• Geopolitical Risk (GPR)\n• US Dollar Index (DXY)\n• Global Oil Supply Series\n• Trend Averages (MA30)", 
            fontsize=8.2, color="#000000", ha='center', va='center', linespacing=1.3)

    # Sub-box 3: Shocks & Volatility
    b3 = patches.FancyBboxPatch((66.4, 100), p_w, 14.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=1.0)
    ax.add_patch(b3)
    ax.plot([66.4, 66.4 + p_w], [111, 111], color="#333333", linewidth=0.8)
    ax.text(66.4 + p_w/2, 112.5, "Crack-Spread & Volatility", fontsize=9.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(66.4 + p_w/2, 105.5, 
            "• Refining Margins (Crack)\n• Realized Vol (10d, 30d)\n• Day-of-Week Encoding\n• Month-of-Year Encoding", 
            fontsize=8.2, color="#000000", ha='center', va='center', linespacing=1.3)

    # Down Arrows from Stage 1 to Stage 2
    for xc in [5 + p_w/2, 35.7 + p_w/2, 66.4 + p_w/2]:
        ax.annotate('', xy=(xc, 93), xytext=(xc, 98),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.8, mutation_scale=14))

    # =========================================================================
    # SECTION 2: THREE HETEROGENEOUS DOMAIN EXPERTS (Y: 64 to 93)
    # =========================================================================
    # Expert 1: 1D-CNN
    draw_ieee_card(5, 65, p_w, 28, "EXPERT 1: Multi-Scale 1D-CNN", "Inductive Bias: High-Frequency Momentum")
    ax.text(5 + p_w/2, 74.5, 
            "• Parallel Inception Convolutions\n  Kernel sizes: k ∈ {3, 7, 15}\n• Temporal Feature Extraction\n• Layer Normalization\n• Softmax Attention Pooling\n\nOutput: f_cnn ∈ R^128", 
            fontsize=8.2, color="#000000", ha='center', va='center', linespacing=1.3)

    # Expert 2: GRU-Attention
    draw_ieee_card(35.7, 65, p_w, 28, "EXPERT 2: Stacked GRU-Attn", "Inductive Bias: Low-Frequency Regime")
    ax.text(35.7 + p_w/2, 74.5, 
            "• 2-Layer Recurrent GRU\n• Hidden Dimension: d = 128\n• Dropout Rate: 0.1\n• Temporal Multi-Head Attention\n• Context Alignment across L=30\n\nOutput: f_gru ∈ R^128", 
            fontsize=8.2, color="#000000", ha='center', va='center', linespacing=1.3)

    # Expert 3: Wavelet-KAN
    draw_ieee_card(66.4, 65, p_w, 28, "EXPERT 3: Wavelet-KAN Shock", "Inductive Bias: Fat-Tail & Non-Linear")
    ax.text(66.4 + p_w/2, 74.5, 
            "• Kolmogorov–Arnold Network\n• Mexican Hat Wavelet Basis:\n  ψ(z) = (1 - z²) exp(-0.5 z²)\n• Learnable Translation / Dilation\n• Non-linear Shock Absorption\n\nOutput: f_kan ∈ R^128", 
            fontsize=8.2, color="#000000", ha='center', va='center', linespacing=1.3)

    # Converging Arrows from Stage 2 to Stage 3
    for xc in [5 + p_w/2, 35.7 + p_w/2, 66.4 + p_w/2]:
        ax.annotate('', xy=(50, 59.5), xytext=(xc, 65),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.8, mutation_scale=14))

    # =========================================================================
    # SECTION 3: HORIZON-AWARE DYNAMIC ROUTER (Y: 37 to 59.5)
    # =========================================================================
    draw_ieee_card(8, 38, 84, 21.5, "STAGE 2: HORIZON-AWARE DYNAMIC GATING ROUTER")
    
    # Left Box inside Router: Inputs
    r_in = patches.FancyBboxPatch((10.5, 39.5), 35, 15, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#666666", linewidth=1.0)
    ax.add_patch(r_in)
    ax.text(10.5 + 17.5, 47, 
            "Router Input Conditioning:\n"
            "• Concat: [f_cnn, f_gru, f_kan]\n"
            "• Positional Embedding: Pos_h\n"
            "• Global Context: [μ_x, σ_x]",
            fontsize=8.2, color="#000000", ha='center', va='center', linespacing=1.25)

    # Center Arrow
    ax.annotate('', xy=(51, 47), xytext=(46.5, 47),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=2.0, mutation_scale=15))

    # Right Box inside Router: Gating MLP + Softmax
    r_out = patches.FancyBboxPatch((52, 39.5), 38, 15, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#666666", linewidth=1.0)
    ax.add_patch(r_out)
    ax.text(52 + 19, 47, 
            "MLP Gating Network (128 units, GELU)\n"
            "Softmax Weights: w_1 + w_2 + w_3 = 1\n"
            "Dynamically Fused Representation:\n"
            "f_fused = Σ w_j f_j ∈ R^128",
            fontsize=8.2, fontweight='bold', color="#000000", ha='center', va='center', linespacing=1.25)

    # Down Arrow from Stage 3 to Stage 4
    ax.annotate('', xy=(50, 32.5), xytext=(50, 38),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=2.0, mutation_scale=15))

    # =========================================================================
    # SECTION 4: MULTI-HORIZON PROBABILISTIC HEADS & RESIDUAL SCALING (Y: 2 to 32.5)
    # =========================================================================
    draw_ieee_card(3, 2.5, 94, 30, "STAGE 3: HORIZON HEADS, RESIDUAL SCALING & PROBABILISTIC TAIL QUANTIFICATION")

    # 4 Horizon/Tail Sub-boxes
    h_w = 21.2
    # Head 1: Short
    hb1 = patches.FancyBboxPatch((5, 4.5), h_w, 22.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=1.0)
    ax.add_patch(hb1)
    ax.plot([5, 5 + h_w], [22.5, 22.5], color="#444444", linewidth=0.8)
    ax.text(5 + h_w/2, 24.5, "Short Head\nH ∈ {1, 3}", fontsize=8.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(5 + h_w/2, 13.5, 
            "• Direct Linear\n  Projection Layer\n• Preserves Spot\n  Momentum\n• Ultra-Fast O(1)\n  Inference\n• DA > 90%", 
            fontsize=8.0, color="#000000", ha='center', va='center', linespacing=1.25)

    # Head 2: Medium
    hb2 = patches.FancyBboxPatch((28.2, 4.5), h_w, 22.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=1.0)
    ax.add_patch(hb2)
    ax.plot([28.2, 28.2 + h_w], [22.5, 22.5], color="#444444", linewidth=0.8)
    ax.text(28.2 + h_w/2, 24.5, "Medium Head\nH ∈ {5, 7, 10}", fontsize=8.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(28.2 + h_w/2, 13.5, 
            "• 2-Layer MLP\n  with GELU Act\n• Regulatory Cycle\n  Calibration (7d)\n• Smooth Transition\n  Dynamics", 
            fontsize=8.0, color="#000000", ha='center', va='center', linespacing=1.25)

    # Head 3: Long
    hb3 = patches.FancyBboxPatch((51.4, 4.5), h_w, 22.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=1.0)
    ax.add_patch(hb3)
    ax.plot([51.4, 51.4 + h_w], [22.5, 22.5], color="#444444", linewidth=0.8)
    ax.text(51.4 + h_w/2, 24.5, "Long Head\nH ∈ {20, 60}", fontsize=8.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(51.4 + h_w/2, 13.5, 
            "• 3-Layer Deep MLP\n  + LayerNorm\n• Residual Scaling\n  Bounding (γ_h)\n• Extrapolation Drift\n  Suppression", 
            fontsize=8.0, color="#000000", ha='center', va='center', linespacing=1.25)

    # Head 4: Calibrated Quantile Output
    hb4 = patches.FancyBboxPatch((74.6, 4.5), 20.4, 22.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.4)
    ax.add_patch(hb4)
    ax.plot([74.6, 74.6 + 20.4], [22.5, 22.5], color="#000000", linewidth=1.0)
    ax.text(74.6 + 10.2, 24.5, "Quantile Output\n& Tail Bounds", fontsize=8.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(74.6 + 10.2, 13.5, 
            "• Quantile Grid:\n  q ∈ {0.1, 0.5, 0.9}\n• ŷ^(q) = Head(f)\n  + γ_h · x_target\n• Inverse Price:\n  P_hat = P · exp(r)\n• PICP = 82.4%", 
            fontsize=7.8, fontweight='bold', color="#000000", ha='center', va='center', linespacing=1.25)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated B&W clean architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_bw_clean_architecture_diagram('scratch/images/image1.png')
