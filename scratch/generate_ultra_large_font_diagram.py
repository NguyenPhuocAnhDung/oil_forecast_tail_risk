import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_ultra_large_font_bw_architecture(out_path='scratch/images/image1.png'):
    # Compact canvas: 5.2 x 7.4 inches at 300 DPI
    # When displayed at 3.48 inches in Word, scaling ratio is 3.48/5.2 = 0.67
    # So a 11.5pt font appears as 7.7pt (matches 8pt document table font!),
    # and a 14pt font appears as 9.4pt (matches document body text!).
    fig, ax = plt.subplots(figsize=(5.2, 7.4), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # -------------------------------------------------------------------------
    # 1. Main Title Box (Y: 93.5 to 99.0)
    # -------------------------------------------------------------------------
    title_box = patches.FancyBboxPatch((2, 93.5), 96, 5.5, boxstyle="square,pad=0",
                                      facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.5)
    ax.add_patch(title_box)
    ax.text(50, 96.2, "GUMNetHet Architecture Overview", 
            color="#000000", fontsize=12.5, fontweight='bold', ha='center', va='center')

    # Helper function for drawing outer section wrappers
    def draw_section_wrapper(x, y, w, h, title):
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.3)
        ax.add_patch(card)
        
        # Header banner inside wrapper
        header_h = 4.0
        header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, 
                                       boxstyle="square,pad=0",
                                       facecolor="#F1F5F9", edgecolor="#000000", linewidth=0.8)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - header_h/2, title, color="#000000", fontsize=10.0, fontweight='bold', ha='center', va='center')

    # -------------------------------------------------------------------------
    # STAGE 1: INPUT SEQUENCE & DOMAIN PARTITIONING (Y: 76.5 to 91.5)
    # -------------------------------------------------------------------------
    draw_section_wrapper(2, 76.5, 96, 15.0, "STAGE 1: INPUT PARTITIONING (L = 30 Days)")
    
    p_w = 29.5
    # Sub-box 1: Spot Price
    b1 = patches.FancyBboxPatch((4, 77.5), p_w, 9.8, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=0.8)
    ax.add_patch(b1)
    ax.plot([4, 4 + p_w], [84.2, 84.2], color="#333333", linewidth=0.6)
    ax.text(4 + p_w/2, 85.6, "Spot Prices", fontsize=9.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(4 + p_w/2, 80.8, "• MG95, MG92\n• Gasoil, WTI, Brent", fontsize=9.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 2: Macro & GPR
    b2 = patches.FancyBboxPatch((35.25, 77.5), p_w, 9.8, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=0.8)
    ax.add_patch(b2)
    ax.plot([35.25, 35.25 + p_w], [84.2, 84.2], color="#333333", linewidth=0.6)
    ax.text(35.25 + p_w/2, 85.6, "Macro & GPR", fontsize=9.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(35.25 + p_w/2, 80.8, "• GPR Risk Index\n• DXY Index, MA30", fontsize=9.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 3: Shocks & Volatility
    b3 = patches.FancyBboxPatch((66.5, 77.5), p_w, 9.8, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#333333", linewidth=0.8)
    ax.add_patch(b3)
    ax.plot([66.5, 66.5 + p_w], [84.2, 84.2], color="#333333", linewidth=0.6)
    ax.text(66.5 + p_w/2, 85.6, "Crack & Volatility", fontsize=9.5, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(66.5 + p_w/2, 80.8, "• Crack Margins\n• Vol (10d, 30d)", fontsize=9.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Down Arrows from Stage 1 to Stage 2
    for xc in [4 + p_w/2, 35.25 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(xc, 72.0), xytext=(xc, 76.5),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5, mutation_scale=11))

    # -------------------------------------------------------------------------
    # STAGE 2: THREE HETEROGENEOUS DOMAIN EXPERTS (Y: 49.0 to 72.0)
    # -------------------------------------------------------------------------
    # Expert 1: 1D-CNN
    exp1 = patches.FancyBboxPatch((4, 49.0), p_w, 23.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(exp1)
    h1 = patches.FancyBboxPatch((4, 68.0), p_w, 4.0, boxstyle="square,pad=0", facecolor="#F1F5F9", edgecolor="#000000", linewidth=0.8)
    ax.add_patch(h1)
    ax.text(4 + p_w/2, 70.0, "Expert 1: 1D-CNN", fontsize=10.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(4 + p_w/2, 65.5, "Price Momentum", fontsize=8.5, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([6, 4 + p_w - 2], [63.8, 63.8], color="#DDDDDD", linewidth=0.6)
    ax.text(4 + p_w/2, 55.5, 
            "• Kernels: 3, 7, 15\n• Temporal Convs\n• LayerNorm + Dropout\n• Attention Pooling\n\nOutput: f_cnn ∈ R^128", 
            fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 2: GRU-Attention
    exp2 = patches.FancyBboxPatch((35.25, 49.0), p_w, 23.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(exp2)
    h2 = patches.FancyBboxPatch((35.25, 68.0), p_w, 4.0, boxstyle="square,pad=0", facecolor="#F1F5F9", edgecolor="#000000", linewidth=0.8)
    ax.add_patch(h2)
    ax.text(35.25 + p_w/2, 70.0, "Expert 2: GRU-Attn", fontsize=10.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(35.25 + p_w/2, 65.5, "Macro Regime", fontsize=8.5, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([37.25, 35.25 + p_w - 2], [63.8, 63.8], color="#DDDDDD", linewidth=0.6)
    ax.text(35.25 + p_w/2, 55.5, 
            "• 2-Layer Stacked GRU\n• Hidden: d = 128\n• Multi-Head Attention\n• Context Memory L=30\n\nOutput: f_gru ∈ R^128", 
            fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 3: Wavelet-KAN
    exp3 = patches.FancyBboxPatch((66.5, 49.0), p_w, 23.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(exp3)
    h3 = patches.FancyBboxPatch((66.5, 68.0), p_w, 4.0, boxstyle="square,pad=0", facecolor="#F1F5F9", edgecolor="#000000", linewidth=0.8)
    ax.add_patch(h3)
    ax.text(66.5 + p_w/2, 70.0, "Expert 3: Wav-KAN", fontsize=10.0, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(66.5 + p_w/2, 65.5, "Non-Linear Shocks", fontsize=8.5, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([68.5, 66.5 + p_w - 2], [63.8, 63.8], color="#DDDDDD", linewidth=0.6)
    ax.text(66.5 + p_w/2, 55.5, 
            "• Kolmogorov–Arnold Net\n• Mexican Hat Wavelet:\n  ψ(z)=(1-z²)e^(-0.5z²)\n• Shock Dampening\n\nOutput: f_kan ∈ R^128", 
            fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Converging Arrows from Stage 2 to Stage 3
    for xc in [4 + p_w/2, 35.25 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(50, 44.5), xytext=(xc, 49.0),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.5, mutation_scale=11))

    # -------------------------------------------------------------------------
    # STAGE 3: HORIZON-AWARE DYNAMIC GATING ROUTER (Y: 27.5 to 44.5)
    # -------------------------------------------------------------------------
    draw_section_wrapper(2, 27.5, 96, 17.0, "STAGE 2: HORIZON-AWARE DYNAMIC GATING ROUTER")
    
    # Left Box inside Router: Inputs
    r_in = patches.FancyBboxPatch((4.5, 29.0), 42.0, 11.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(r_in)
    ax.text(4.5 + 21.0, 34.6, 
            "Router Inputs:\n• Concat: [f_cnn, f_gru, f_kan]\n• Positional Encoding: Pos_h\n• Market Stats: [μ_x, σ_x]", 
            fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Center Arrow
    ax.annotate('', xy=(52.5, 34.6), xytext=(47.5, 34.6),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.6, mutation_scale=12))

    # Right Box inside Router: Gating MLP + Softmax
    r_out = patches.FancyBboxPatch((53.5, 29.0), 42.5, 11.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(r_out)
    ax.text(53.5 + 21.25, 34.6, 
            "MLP Gating Network (128 units)\nSoftmax Weights: w_1 + w_2 + w_3 = 1\nFused: f_fused = Σ w_j f_j ∈ R^128", 
            fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Down Arrow from Stage 3 to Stage 4
    ax.annotate('', xy=(50, 23.0), xytext=(50, 27.5),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.6, mutation_scale=12))

    # -------------------------------------------------------------------------
    # STAGE 4: MULTI-HORIZON HEADS & QUANTILE OUTPUTS (Y: 1.5 to 23.0)
    # -------------------------------------------------------------------------
    draw_section_wrapper(2, 1.5, 96, 21.5, "STAGE 3: HORIZON HEADS & CALIBRATED QUANTILE OUTPUTS")

    # 4 Horizon/Tail Sub-boxes
    h_w = 21.5
    # Head 1: Short
    hb1 = patches.FancyBboxPatch((4.0, 2.8), h_w, 15.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(hb1)
    ax.plot([4.0, 4.0 + h_w], [14.0, 14.0], color="#444444", linewidth=0.6)
    ax.text(4.0 + h_w/2, 15.5, "Short Head\nH ∈ {1, 3}", fontsize=8.8, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(4.0 + h_w/2, 8.4, "• Linear Proj\n• Spot Momentum\n• Fast O(1) Time\n• DA > 90%", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 2: Medium
    hb2 = patches.FancyBboxPatch((28.0, 2.8), h_w, 15.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(hb2)
    ax.plot([28.0, 28.0 + h_w], [14.0, 14.0], color="#444444", linewidth=0.6)
    ax.text(28.0 + h_w/2, 15.5, "Medium Head\nH ∈ {5, 7, 10}", fontsize=8.8, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(28.0 + h_w/2, 8.4, "• 2-Layer MLP\n• 7-Day Cycle\n• Non-linear Shift\n• Smooth Transition", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 3: Long
    hb3 = patches.FancyBboxPatch((52.0, 2.8), h_w, 15.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(hb3)
    ax.plot([52.0, 52.0 + h_w], [14.0, 14.0], color="#444444", linewidth=0.6)
    ax.text(52.0 + h_w/2, 15.5, "Long Head\nH ∈ {20, 60}", fontsize=8.8, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(52.0 + h_w/2, 8.4, "• 3-Layer Deep MLP\n• LayerNorm\n• Residual Scaling γ_h\n• Bound Drift", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 4: Calibrated Quantile Output
    hb4 = patches.FancyBboxPatch((76.0, 2.8), 20.0, 15.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.0)
    ax.add_patch(hb4)
    ax.plot([76.0, 76.0 + 20.0], [14.0, 14.0], color="#000000", linewidth=0.8)
    ax.text(76.0 + 10.0, 15.5, "Quantile Output\n& Tail Bounds", fontsize=8.6, fontweight='bold', color="#000000", ha='center', va='center')
    ax.text(76.0 + 10.0, 8.4, "• q ∈ {0.1, 0.5, 0.9}\n• ŷ^(q) = Head + γ_h·x\n• P_hat = P · e^r\n• PICP = 82.4%", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated ultra large-font, un-bolded B&W architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_ultra_large_font_bw_architecture('scratch/images/image1.png')
