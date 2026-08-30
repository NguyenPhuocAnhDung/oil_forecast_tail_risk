import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_clean_nobold_architecture(out_path='scratch/images/image1.png'):
    # Canvas size: 7.2 x 9.6 inches at 300 DPI
    fig, ax = plt.subplots(figsize=(7.2, 9.6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # -------------------------------------------------------------------------
    # TOP TITLE (Pure Normal Weight, Clean Outline)
    # -------------------------------------------------------------------------
    title_box = patches.FancyBboxPatch((4, 94.0), 92, 5.0, boxstyle="square,pad=0",
                                      facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(title_box)
    ax.text(50, 96.5, "GUMNetHet Architecture Overview", 
            color="#000000", fontsize=11.0, fontweight='normal', ha='center', va='center')

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
        ax.text(x + w/2, y + h - header_h/2, title, color="#000000", fontsize=9.0, fontweight='normal', ha='center', va='center')

    # -------------------------------------------------------------------------
    # STAGE 1: INPUT SEQUENCE & DOMAIN PARTITIONING (Y: 77.0 to 91.5)
    # -------------------------------------------------------------------------
    draw_section_box(4, 77.0, 92, 14.5, "Stage 1: Input Sequence & Feature Partitioning (L = 30 Days)")
    
    p_w = 28.0
    # Sub-box 1: Spot Price
    b1 = patches.FancyBboxPatch((6, 78.2), p_w, 9.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b1)
    ax.plot([6, 6 + p_w], [84.5, 84.5], color="#444444", linewidth=0.5)
    ax.text(6 + p_w/2, 85.8, "Spot Prices", fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(6 + p_w/2, 81.3, "• MG95, MG92\n• Gasoil, WTI, Brent", fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 2: Macro & GPR
    b2 = patches.FancyBboxPatch((36.0, 78.2), p_w, 9.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b2)
    ax.plot([36.0, 36.0 + p_w], [84.5, 84.5], color="#444444", linewidth=0.5)
    ax.text(36.0 + p_w/2, 85.8, "Macro & GPR", fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(36.0 + p_w/2, 81.3, "• GPR Risk Index\n• DXY Index, MA30", fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 3: Shocks & Volatility
    b3 = patches.FancyBboxPatch((66.0, 78.2), p_w, 9.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(b3)
    ax.plot([66.0, 66.0 + p_w], [84.5, 84.5], color="#444444", linewidth=0.5)
    ax.text(66.0 + p_w/2, 85.8, "Crack & Volatility", fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(66.0 + p_w/2, 81.3, "• Crack Margins\n• Vol (10d, 30d)", fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Down Arrows from Stage 1 to Stage 2
    for xc in [6 + p_w/2, 36.0 + p_w/2, 66.0 + p_w/2]:
        ax.annotate('', xy=(xc, 73.0), xytext=(xc, 77.0),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.2, mutation_scale=10))

    # -------------------------------------------------------------------------
    # STAGE 2: THREE HETEROGENEOUS DOMAIN EXPERTS (Y: 49.5 to 73.0)
    # -------------------------------------------------------------------------
    # Expert 1: 1D-CNN
    exp1 = patches.FancyBboxPatch((6, 50.0), p_w, 23.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.0)
    ax.add_patch(exp1)
    h1 = patches.FancyBboxPatch((6, 69.2), p_w, 3.8, boxstyle="square,pad=0", facecolor="#F8FAFC", edgecolor="#000000", linewidth=0.7)
    ax.add_patch(h1)
    ax.text(6 + p_w/2, 71.1, "Expert 1: 1D-CNN", fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(6 + p_w/2, 66.8, "Price Momentum", fontsize=7.5, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([7.5, 6 + p_w - 1.5], [65.2, 65.2], color="#DDDDDD", linewidth=0.5)
    ax.text(6 + p_w/2, 57.0, 
            "• Kernels: 3, 7, 15\n• Temporal Convs\n• LayerNorm + Dropout\n• Attention Pooling\n\nOutput: f_cnn ∈ R^128", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 2: GRU-Attention
    exp2 = patches.FancyBboxPatch((36.0, 50.0), p_w, 23.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.0)
    ax.add_patch(exp2)
    h2 = patches.FancyBboxPatch((36.0, 69.2), p_w, 3.8, boxstyle="square,pad=0", facecolor="#F8FAFC", edgecolor="#000000", linewidth=0.7)
    ax.add_patch(h2)
    ax.text(36.0 + p_w/2, 71.1, "Expert 2: GRU-Attn", fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(36.0 + p_w/2, 66.8, "Macro Regime", fontsize=7.5, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([37.5, 36.0 + p_w - 1.5], [65.2, 65.2], color="#DDDDDD", linewidth=0.5)
    ax.text(36.0 + p_w/2, 57.0, 
            "• 2-Layer Stacked GRU\n• Hidden: d = 128\n• Multi-Head Attention\n• Context Memory L=30\n\nOutput: f_gru ∈ R^128", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 3: Wavelet-KAN
    exp3 = patches.FancyBboxPatch((66.0, 50.0), p_w, 23.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.0)
    ax.add_patch(exp3)
    h3 = patches.FancyBboxPatch((66.0, 69.2), p_w, 3.8, boxstyle="square,pad=0", facecolor="#F8FAFC", edgecolor="#000000", linewidth=0.7)
    ax.add_patch(h3)
    ax.text(66.0 + p_w/2, 71.1, "Expert 3: Wav-KAN", fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(66.0 + p_w/2, 66.8, "Non-Linear Shocks", fontsize=7.5, fontstyle='italic', color="#444444", ha='center', va='center')
    ax.plot([67.5, 66.0 + p_w - 1.5], [65.2, 65.2], color="#DDDDDD", linewidth=0.5)
    ax.text(66.0 + p_w/2, 57.0, 
            "• Kolmogorov–Arnold Net\n• Mexican Hat Wavelet:\n  ψ(z)=(1-z²)e^(-0.5z²)\n• Shock Dampening\n\nOutput: f_kan ∈ R^128", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Converging Arrows from Stage 2 to Stage 3
    for xc in [6 + p_w/2, 36.0 + p_w/2, 66.0 + p_w/2]:
        ax.annotate('', xy=(50, 45.5), xytext=(xc, 50.0),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=1.2, mutation_scale=10))

    # -------------------------------------------------------------------------
    # STAGE 3: HORIZON-AWARE DYNAMIC GATING ROUTER (Y: 28.0 to 45.5)
    # -------------------------------------------------------------------------
    draw_section_box(4, 28.0, 92, 17.5, "Stage 2: Horizon-Aware Dynamic Gating Router")
    
    # Left Box inside Router: Inputs
    r_in = patches.FancyBboxPatch((6.0, 29.5), 40.0, 11.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(r_in)
    ax.text(6.0 + 20.0, 35.2, 
            "Router Inputs:\n• Concat: [f_cnn, f_gru, f_kan]\n• Positional Encoding: Pos_h\n• Market Stats: [μ_x, σ_x]", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Center Arrow
    ax.annotate('', xy=(52.0, 35.2), xytext=(47.5, 35.2),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.4, mutation_scale=11))

    # Right Box inside Router: Gating MLP + Softmax
    r_out = patches.FancyBboxPatch((53.5, 29.5), 40.5, 11.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(r_out)
    ax.text(53.5 + 20.25, 35.2, 
            "MLP Gating (128 units)\nSoftmax: w_1 + w_2 + w_3 = 1\nFused: f_fused = Σ w_j f_j ∈ R^128", 
            fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Down Arrow from Stage 3 to Stage 4
    ax.annotate('', xy=(50, 23.5), xytext=(50, 28.0),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=1.4, mutation_scale=11))

    # -------------------------------------------------------------------------
    # STAGE 4: MULTI-HORIZON HEADS & QUANTILE OUTPUTS (Y: 1.5 to 23.5)
    # -------------------------------------------------------------------------
    draw_section_box(4, 1.5, 92, 22.0, "Stage 3: Multi-Horizon Heads & Calibrated Quantile Outputs")

    # 4 Horizon/Tail Sub-boxes
    h_w = 20.2
    # Head 1: Short
    hb1 = patches.FancyBboxPatch((6.0, 2.8), h_w, 15.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(hb1)
    ax.plot([6.0, 6.0 + h_w], [14.2, 14.2], color="#444444", linewidth=0.5)
    ax.text(6.0 + h_w/2, 15.8, "Short Head\nH ∈ {1, 3}", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(6.0 + h_w/2, 8.4, "• Linear Proj\n• Spot Momentum\n• Fast O(1) Time\n• DA > 90%", fontsize=7.4, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 2: Medium
    hb2 = patches.FancyBboxPatch((28.0, 2.8), h_w, 15.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(hb2)
    ax.plot([28.0, 28.0 + h_w], [14.2, 14.2], color="#444444", linewidth=0.5)
    ax.text(28.0 + h_w/2, 15.8, "Medium Head\nH ∈ {5, 7, 10}", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(28.0 + h_w/2, 8.4, "• 2-Layer MLP\n• 7-Day Cycle\n• Non-linear Shift\n• Smooth Transition", fontsize=7.4, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 3: Long
    hb3 = patches.FancyBboxPatch((50.0, 2.8), h_w, 15.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(hb3)
    ax.plot([50.0, 50.0 + h_w], [14.2, 14.2], color="#444444", linewidth=0.5)
    ax.text(50.0 + h_w/2, 15.8, "Long Head\nH ∈ {20, 60}", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(50.0 + h_w/2, 8.4, "• 3-Layer MLP\n• LayerNorm\n• Residual γ_h\n• Bound Drift", fontsize=7.4, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Head 4: Calibrated Quantile Output
    hb4 = patches.FancyBboxPatch((72.0, 2.8), 22.0, 15.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(hb4)
    ax.plot([72.0, 72.0 + 22.0], [14.2, 14.2], color="#000000", linewidth=0.6)
    ax.text(72.0 + 11.0, 15.8, "Quantile Output\n& Tail Bounds", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(72.0 + 11.0, 8.4, "• q ∈ {0.1, 0.5, 0.9}\n• ŷ^(q) = Head + γ_h·x\n• P_hat = P · e^r\n• PICP = 82.4%", fontsize=7.4, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated clean NO-BOLD architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_clean_nobold_architecture('scratch/images/image1.png')
