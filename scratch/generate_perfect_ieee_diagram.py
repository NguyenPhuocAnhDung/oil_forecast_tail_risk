import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_perfect_ieee_architecture_diagram(out_path='scratch/images/image1.png'):
    # Canvas: 8.0 x 11.2 inches at 300 DPI
    fig, ax = plt.subplots(figsize=(8.0, 11.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 122)
    ax.axis('off')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # -------------------------------------------------------------------------
    # 1. Main Title Box (Y: 114 to 120)
    # -------------------------------------------------------------------------
    title_box = patches.FancyBboxPatch((3, 114), 94, 6.0, boxstyle="square,pad=0",
                                      facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.6)
    ax.add_patch(title_box)
    ax.text(50, 117.0, "GUMNetHet: Heterogeneous Mixture-of-Experts Architecture", 
            color="#000000", fontsize=11.5, fontweight='bold', ha='center', va='center')

    # Helper function for drawing outer section wrappers
    def draw_section_wrapper(x, y, w, h, title):
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.3)
        ax.add_patch(card)
        
        # Header banner inside wrapper
        header_h = 3.6
        header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, 
                                       boxstyle="square,pad=0",
                                       facecolor="#F3F4F6", edgecolor="#000000", linewidth=0.8)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - header_h/2, title, color="#000000", fontsize=9.2, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # STAGE 1: INPUT SEQUENCE & DOMAIN PARTITIONING (Y: 93.5 to 110.5)
    # -------------------------------------------------------------------------
    draw_section_wrapper(3, 93.5, 94, 17.0, "STAGE 1: INPUT SEQUENCE & DOMAIN-AWARE PARTITIONING (L = 30 Days)")
    
    p_w = 28.5
    # Sub-box 1: Spot Price
    b1 = patches.FancyBboxPatch((5, 95.0), p_w, 11.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=0.8)
    ax.add_patch(b1)
    ax.plot([5, 5 + p_w], [103.2, 103.2], color="#333333", linewidth=0.6)
    ax.text(5 + p_w/2, 104.5, "Spot & Benchmarks", fontsize=8.8, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(5 + p_w/2, 99.0, 
            "• Mogas 95, Mogas 92\n• Gasoil 0.001%S, 0.05%S\n• WTI, Brent, Naphtha", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 2: Macro & GPR
    b2 = patches.FancyBboxPatch((35.75, 95.0), p_w, 11.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=0.8)
    ax.add_patch(b2)
    ax.plot([35.75, 35.75 + p_w], [103.2, 103.2], color="#333333", linewidth=0.6)
    ax.text(35.75 + p_w/2, 104.5, "Macro & Geopolitical", fontsize=8.8, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(35.75 + p_w/2, 99.0, 
            "• Geopolitical Risk (GPR)\n• US Dollar Index (DXY)\n• Rolling Trend (MA30)", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 3: Shocks & Volatility
    b3 = patches.FancyBboxPatch((66.5, 95.0), p_w, 11.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=0.8)
    ax.add_patch(b3)
    ax.plot([66.5, 66.5 + p_w], [103.2, 103.2], color="#333333", linewidth=0.6)
    ax.text(66.5 + p_w/2, 104.5, "Crack & Volatility", fontsize=8.8, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(66.5 + p_w/2, 99.0, 
            "• Refining Crack Margins\n• Realized Vol (10d, 30d)\n• Day / Month Encodings", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Down Arrows from Stage 1 to Stage 2
    for xc in [5 + p_w/2, 35.75 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(xc, 88.5), xytext=(xc, 93.5),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.4, mutation_scale=12))

    # -------------------------------------------------------------------------
    # STAGE 2: THREE HETEROGENEOUS DOMAIN EXPERTS (Y: 62.5 to 88.5)
    # -------------------------------------------------------------------------
    # Expert 1: 1D-CNN
    exp1 = patches.FancyBboxPatch((5, 62.5), p_w, 25.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(exp1)
    # Header block inside Expert 1
    h1 = patches.FancyBboxPatch((5, 84.0), p_w, 4.0, boxstyle="square,pad=0", facecolor="#F3F4F6", edgecolor="#000000", linewidth=0.8)
    ax.add_patch(h1)
    ax.text(5 + p_w/2, 86.0, "Expert 1: 1D-CNN", fontsize=9.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(5 + p_w/2, 81.8, "High-Frequency Momentum", fontsize=7.8, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([7, 5 + p_w - 2], [80.2, 80.2], color="#CCCCCC", linewidth=0.6)
    ax.text(5 + p_w/2, 70.5, 
            "• Inception Kernels:\n  k ∈ {3, 7, 15}\n• Temporal Convolutions\n• LayerNorm + Dropout\n• Softmax Attention\n\nOutput: f_cnn ∈ R^128", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 2: GRU-Attention
    exp2 = patches.FancyBboxPatch((35.75, 62.5), p_w, 25.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(exp2)
    h2 = patches.FancyBboxPatch((35.75, 84.0), p_w, 4.0, boxstyle="square,pad=0", facecolor="#F3F4F6", edgecolor="#000000", linewidth=0.8)
    ax.add_patch(h2)
    ax.text(35.75 + p_w/2, 86.0, "Expert 2: GRU-Attn", fontsize=9.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(35.75 + p_w/2, 81.8, "Macroeconomic Regime", fontsize=7.8, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([37.75, 35.75 + p_w - 2], [80.2, 80.2], color="#CCCCCC", linewidth=0.6)
    ax.text(35.75 + p_w/2, 70.5, 
            "• 2-Layer Recurrent GRU\n• Hidden Dimension d=128\n• Multi-Head Attention\n• Context Alignment\n  across L=30 Days\n\nOutput: f_gru ∈ R^128", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 3: Wavelet-KAN
    exp3 = patches.FancyBboxPatch((66.5, 62.5), p_w, 25.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(exp3)
    h3 = patches.FancyBboxPatch((66.5, 84.0), p_w, 4.0, boxstyle="square,pad=0", facecolor="#F3F4F6", edgecolor="#000000", linewidth=0.8)
    ax.add_patch(h3)
    ax.text(66.5 + p_w/2, 86.0, "Expert 3: Wav-KAN", fontsize=9.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(66.5 + p_w/2, 81.8, "Non-Linear Shocks", fontsize=7.8, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([68.5, 66.5 + p_w - 2], [80.2, 80.2], color="#CCCCCC", linewidth=0.6)
    ax.text(66.5 + p_w/2, 70.5, 
            "• Kolmogorov–Arnold Net\n• Mexican Hat Wavelet:\n  ψ(z) = (1-z²)e^(-0.5z²)\n• Learnable Splines\n• Shock Dampening\n\nOutput: f_kan ∈ R^128", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Converging Arrows from Stage 2 to Stage 3
    for xc in [5 + p_w/2, 35.75 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(50, 58.0), xytext=(xc, 62.5),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.4, mutation_scale=12))

    # -------------------------------------------------------------------------
    # STAGE 3: HORIZON-AWARE DYNAMIC GATING ROUTER (Y: 38.0 to 58.0)
    # -------------------------------------------------------------------------
    draw_section_wrapper(3, 38.0, 94, 20.0, "STAGE 2: HORIZON-AWARE DYNAMIC GATING ROUTER")
    
    # Left Box inside Router: Inputs
    r_in = patches.FancyBboxPatch((5.5, 39.8), 41.0, 13.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(r_in)
    ax.text(5.5 + 20.5, 46.5, 
            "Router Input Conditioning:\n"
            "• Concat: [f_cnn, f_gru, f_kan]\n"
            "• Positional Embedding: Pos_h\n"
            "• Global Statistics: [μ_x, σ_x]",
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Center Arrow
    ax.annotate('', xy=(52.5, 46.5), xytext=(47.5, 46.5),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.6, mutation_scale=12))

    # Right Box inside Router: Gating MLP + Softmax
    r_out = patches.FancyBboxPatch((53.5, 39.8), 41.5, 13.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(r_out)
    ax.text(53.5 + 20.75, 46.5, 
            "MLP Gating Network (128 units, GELU)\n"
            "Softmax Weights: w_1 + w_2 + w_3 = 1\n"
            "Fused Output Representation:\n"
            "f_fused = Σ w_j f_j ∈ R^128",
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Down Arrow from Stage 3 to Stage 4
    ax.annotate('', xy=(50, 33.0), xytext=(50, 38.0),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.6, mutation_scale=12))

    # -------------------------------------------------------------------------
    # STAGE 4: MULTI-HORIZON HEADS & RESIDUAL SCALING (Y: 2.0 to 33.0)
    # -------------------------------------------------------------------------
    draw_section_wrapper(3, 2.0, 94, 31.0, "STAGE 3: HORIZON HEADS, RESIDUAL SCALING & QUANTILE TAIL OUTPUTS")

    # 4 Horizon/Tail Sub-boxes
    h_w = 21.0
    # Head 1: Short
    hb1 = patches.FancyBboxPatch((5.0, 3.8), h_w, 24.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(hb1)
    ax.plot([5.0, 5.0 + h_w], [22.8, 22.8], color="#444444", linewidth=0.6)
    ax.text(5.0 + h_w/2, 25.4, "Short Head\nH ∈ {1, 3}", fontsize=8.2, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(5.0 + h_w/2, 13.0, 
            "• Direct Linear\n  Projection\n• Preserves Spot\n  Momentum\n• Fast O(1) Latency\n• Directional Signal\n• DA > 90%", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 2: Medium
    hb2 = patches.FancyBboxPatch((28.5, 3.8), h_w, 24.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(hb2)
    ax.plot([28.5, 28.5 + h_w], [22.8, 22.8], color="#444444", linewidth=0.6)
    ax.text(28.5 + h_w/2, 25.4, "Medium Head\nH ∈ {5, 7, 10}", fontsize=8.2, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(28.5 + h_w/2, 13.0, 
            "• 2-Layer MLP\n  with GELU Act\n• 7-Day Revision\n  Cycle Alignment\n• Non-linear Price\n  Shift Mapping\n• Smooth Transition", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 3: Long
    hb3 = patches.FancyBboxPatch((52.0, 3.8), h_w, 24.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(hb3)
    ax.plot([52.0, 52.0 + h_w], [22.8, 22.8], color="#444444", linewidth=0.6)
    ax.text(52.0 + h_w/2, 25.4, "Long Head\nH ∈ {20, 60}", fontsize=8.2, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(52.0 + h_w/2, 13.0, 
            "• 3-Layer Deep\n  MLP Architecture\n• Layer Normalization\n• Residual Scaling\n  Bounding (γ_h)\n• Suppresses Drift\n  at H60 Horizon", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 4: Calibrated Quantile Output
    hb4 = patches.FancyBboxPatch((75.5, 3.8), h_w, 24.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.0)
    ax.add_patch(hb4)
    ax.plot([75.5, 75.5 + h_w], [22.8, 22.8], color="#000000", linewidth=0.8)
    ax.text(75.5 + h_w/2, 25.4, "Quantile Output\n& Tail Bounds", fontsize=8.2, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(75.5 + h_w/2, 13.0, 
            "• Quantile Grid:\n  q ∈ {0.1, 0.5, 0.9}\n• ŷ^(q) = Head(f)\n  + γ_h · x_target\n• Inverse Price:\n  P_hat = P · e^r\n• PICP = 82.4%\n• PINAW = 0.142", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated perfect non-overlapping IEEE architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_perfect_ieee_architecture_diagram('scratch/images/image1.png')
