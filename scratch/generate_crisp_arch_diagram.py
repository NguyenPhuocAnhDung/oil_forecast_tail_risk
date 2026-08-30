import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_crisp_architecture_diagram(out_path='scratch/images/image1.png'):
    # Set high DPI and canvas size optimized for IEEE column / page
    fig, ax = plt.subplots(figsize=(10, 11), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 110)
    ax.axis('off')
    
    # Background style
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # 1. Main Title Block
    title_box = patches.FancyBboxPatch((2, 102), 96, 7, boxstyle="round,pad=0.5,rounding_size=1.5",
                                      facecolor="#1E293B", edgecolor="#0F172A", linewidth=1.5)
    ax.add_patch(title_box)
    ax.text(50, 105.5, "GUMNetHet: Heterogeneous Mixture-of-Experts Architecture", 
            color="white", fontsize=13, fontweight='bold', ha='center', va='center')

    # Helper function for drawing cards
    def draw_card(x, y, w, h, bg_color, border_color, title, subtitle=None):
        card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.0",
                                     facecolor=bg_color, edgecolor=border_color, linewidth=1.8)
        ax.add_patch(card)
        
        # Header banner inside card
        header_h = 3.8
        header = patches.FancyBboxPatch((x, y + h - header_h), w, header_h, 
                                       boxstyle="round,pad=0.2,rounding_size=0.8",
                                       facecolor=border_color, edgecolor=border_color, linewidth=1)
        ax.add_patch(header)
        ax.text(x + w/2, y + h - header_h/2, title, color="white", fontsize=10, fontweight='bold', ha='center', va='center')
        
        if subtitle:
            ax.text(x + w/2, y + h - header_h - 1.8, subtitle, color="#334155", fontsize=8.5, fontstyle='italic', ha='center', va='center')

    # =========================================================================
    # ROW 1: INPUT SEQUENCE & DOMAIN PARTITIONING (Y: 82 to 99)
    # =========================================================================
    draw_card(2, 83, 96, 16, "#F8FAFC", "#475569", "INPUT SEQUENCE & DOMAIN-AWARE FEATURE PARTITIONING (L = 30 Days)")
    
    # 3 Input Partition Sub-boxes
    p_w = 29.5
    # Sub-box 1: Price
    box1 = patches.FancyBboxPatch((4, 84.5), p_w, 10.5, boxstyle="round,pad=0.3", facecolor="#E0F2FE", edgecolor="#0284C7", linewidth=1.2)
    ax.add_patch(box1)
    ax.text(4 + p_w/2, 93.2, "Spot & Benchmark Prices", fontsize=9.5, fontweight='bold', color="#0369A1", ha='center')
    ax.text(4 + p_w/2, 88.5, "• MG95, MG92, MG97\n• Gasoil 0.001%S, 0.05%S\n• WTI, Brent, Naphtha", 
            fontsize=8.5, color="#0F172A", ha='center', va='center')

    # Sub-box 2: Macro & GPR
    box2 = patches.FancyBboxPatch((35.25, 84.5), p_w, 10.5, boxstyle="round,pad=0.3", facecolor="#DCFCE7", edgecolor="#16A34A", linewidth=1.2)
    ax.add_patch(box2)
    ax.text(35.25 + p_w/2, 93.2, "Macro & Geopolitical Risk", fontsize=9.5, fontweight='bold', color="#15803D", ha='center')
    ax.text(35.25 + p_w/2, 88.5, "• Geopolitical Risk Index (GPR)\n• US Dollar Index (DXY)\n• Rolling Trend Averages (MA30)", 
            fontsize=8.5, color="#0F172A", ha='center', va='center')

    # Sub-box 3: Non-linear Shock Indicators
    box3 = patches.FancyBboxPatch((66.5, 84.5), p_w, 10.5, boxstyle="round,pad=0.3", facecolor="#F3E8FF", edgecolor="#9333EA", linewidth=1.2)
    ax.add_patch(box3)
    ax.text(66.5 + p_w/2, 93.2, "Crack-Spread & Volatility", fontsize=9.5, fontweight='bold', color="#7E22CE", ha='center')
    ax.text(66.5 + p_w/2, 88.5, "• Refining Margins (Crack Ratios)\n• Realized Volatility (10d, 30d)\n• Cyclical Calendar Encodings", 
            fontsize=8.5, color="#0F172A", ha='center', va='center')

    # Down Arrows from Input to Experts
    for xc in [4 + p_w/2, 35.25 + p_w/2, 66.5 + p_w/2]:
        ax.annotate('', xy=(xc, 78.5), xytext=(xc, 84.2),
                    arrowprops=dict(arrowstyle="->", color="#334155", lw=2, mutation_scale=15))

    # =========================================================================
    # ROW 2: THREE HETEROGENEOUS DOMAIN EXPERTS (Y: 53 to 78)
    # =========================================================================
    # Expert 1: 1D-CNN
    draw_card(4, 54, p_w, 24, "#F0F9FF", "#0284C7", "EXPERT 1: Multi-Scale 1D-CNN", "Inductive Bias: High-Frequency Momentum")
    ax.text(4 + p_w/2, 65, 
            "• Parallel Inception Convolutions\n  Kernels k ∈ {3, 7, 15}\n• Temporal Feature Extraction\n• LayerNorm + Dropout (0.1)\n• Softmax Attention Pooling\n\nOutput: f_cnn ∈ R^128", 
            fontsize=8.5, color="#0F172A", ha='center', va='center', linespacing=1.3)

    # Expert 2: GRU-Attention
    draw_card(35.25, 54, p_w, 24, "#F0FDF4", "#16A34A", "EXPERT 2: Stacked GRU-Attention", "Inductive Bias: Low-Frequency Regime")
    ax.text(35.25 + p_w/2, 65, 
            "• 2-Layer Stacked Recurrent GRU\n• Sequential Hidden State Update\n• Temporal Multi-Head Attention\n• Context Alignment over L=30\n\nOutput: f_gru ∈ R^128", 
            fontsize=8.5, color="#0F172A", ha='center', va='center', linespacing=1.3)

    # Expert 3: Wavelet-KAN
    draw_card(66.5, 54, p_w, 24, "#FAF5FF", "#9333EA", "EXPERT 3: Wavelet-KAN Shock", "Inductive Bias: Fat-Tail & Non-Linear")
    ax.text(66.5 + p_w/2, 65, 
            "• Kolmogorov–Arnold Network\n• Mexican Hat Wavelet Basis:\n  ψ(z) = (1 - z²) exp(-0.5 z²)\n• Learnable Translation & Dilation\n• Non-linear Extreme Shock Dampening\n\nOutput: f_kan ∈ R^128", 
            fontsize=8.5, color="#0F172A", ha='center', va='center', linespacing=1.3)

    # Converging Arrows from Experts to Router
    for xc, color in [(4 + p_w/2, "#0284C7"), (35.25 + p_w/2, "#16A34A"), (66.5 + p_w/2, "#9333EA")]:
        ax.annotate('', xy=(50, 48), xytext=(xc, 53.5),
                    arrowprops=dict(arrowstyle="->", color=color, lw=2.2, mutation_scale=15))

    # =========================================================================
    # ROW 3: HORIZON-AWARE DYNAMIC ROUTER (Y: 30 to 48)
    # =========================================================================
    draw_card(12, 31, 76, 17, "#FFFBEB", "#D97706", "STEP 2: HORIZON-AWARE DYNAMIC GATING ROUTER")
    
    # Left inputs inside router box
    ax.text(26, 38.5, 
            "Concatenated Expert Embeddings: [f_cnn, f_gru, f_kan]\n"
            "+ Horizon Positional Embedding (Pos_h)\n"
            "+ Market Summary Statistics: [μ_x, σ_x]",
            fontsize=8.5, fontweight='bold', color="#78350F", ha='center', va='center', linespacing=1.3)
    
    # Arrow to Gating MLP
    ax.annotate('', xy=(56, 38.5), xytext=(44, 38.5),
                arrowprops=dict(arrowstyle="->", color="#D97706", lw=2, mutation_scale=14))

    # Gating MLP + Softmax box
    g_box = patches.FancyBboxPatch((57, 32.5), 29, 11.5, boxstyle="round,pad=0.3", facecolor="#FEF3C7", edgecolor="#B45309", linewidth=1.2)
    ax.add_patch(g_box)
    ax.text(57 + 14.5, 41, "MLP Gating Network (128 units)", fontsize=8.5, fontweight='bold', color="#92400E", ha='center')
    ax.text(57 + 14.5, 36.5, "Softmax: w_1 + w_2 + w_3 = 1\nFused: f_fused = Σ w_j f_j ∈ R^128", 
            fontsize=8.5, color="#0F172A", ha='center', va='center', linespacing=1.2)

    # Down Arrow to Multi-Quantile Head
    ax.annotate('', xy=(50, 26.5), xytext=(50, 30.5),
                arrowprops=dict(arrowstyle="->", color="#D97706", lw=2.5, mutation_scale=16))

    # =========================================================================
    # ROW 4: HORIZON HEADS, RESIDUAL SCALING & PROBABILISTIC TAIL (Y: 3 to 26)
    # =========================================================================
    draw_card(2, 4, 96, 22.5, "#FFF1F2", "#E11D48", "STEP 3: MULTI-HORIZON PROBABILISTIC HEADS & RESIDUAL SCALING BOUNDING")

    # Head 1: Short
    h_w = 21.5
    h_box1 = patches.FancyBboxPatch((4, 5.5), h_w, 14.5, boxstyle="round,pad=0.3", facecolor="#FFFFFF", edgecolor="#FB7185", linewidth=1.2)
    ax.add_patch(h_box1)
    ax.text(4 + h_w/2, 17.5, "Short Head: H ∈ {1, 3}", fontsize=8.5, fontweight='bold', color="#BE123C", ha='center')
    ax.text(4 + h_w/2, 11.5, "• Direct Linear Projection\n• Preserves Spot Momentum\n• Low Latency Signal (DA > 90%)", 
            fontsize=8.0, color="#0F172A", ha='center', va='center', linespacing=1.2)

    # Head 2: Medium
    h_box2 = patches.FancyBboxPatch((27, 5.5), h_w, 14.5, boxstyle="round,pad=0.3", facecolor="#FFFFFF", edgecolor="#FB7185", linewidth=1.2)
    ax.add_patch(h_box2)
    ax.text(27 + h_w/2, 17.5, "Medium Head: H ∈ {5, 7, 10}", fontsize=8.5, fontweight='bold', color="#BE123C", ha='center')
    ax.text(27 + h_w/2, 11.5, "• 2-Layer MLP + GELU\n• Calibration to 7-Day Cycle\n• Non-linear Price Shift Mapping", 
            fontsize=8.0, color="#0F172A", ha='center', va='center', linespacing=1.2)

    # Head 3: Long
    h_box3 = patches.FancyBboxPatch((50, 5.5), h_w, 14.5, boxstyle="round,pad=0.3", facecolor="#FFFFFF", edgecolor="#FB7185", linewidth=1.2)
    ax.add_patch(h_box3)
    ax.text(50 + h_w/2, 17.5, "Long Head: H ∈ {20, 60}", fontsize=8.5, fontweight='bold', color="#BE123C", ha='center')
    ax.text(50 + h_w/2, 11.5, "• 3-Layer Deep MLP + Norm\n• Drift Suppression Bound\n• Strategic Term Forecast", 
            fontsize=8.0, color="#0F172A", ha='center', va='center', linespacing=1.2)

    # Head 4: Calibrated Tail Risk & Quantiles
    h_box4 = patches.FancyBboxPatch((73, 5.5), 23, 14.5, boxstyle="round,pad=0.3", facecolor="#FFE4E6", edgecolor="#E11D48", linewidth=1.4)
    ax.add_patch(h_box4)
    ax.text(73 + 11.5, 17.5, "Probabilistic Tail Output", fontsize=8.5, fontweight='bold', color="#9F1239", ha='center')
    ax.text(73 + 11.5, 11.5, 
            "Quantile Set q ∈ {0.1, 0.5, 0.9}\n"
            "ŷ^(q) = Head(f) + γ_h · x_target\n"
            "Inverse: P_hat = P_t · exp(r_hat)\n"
            "80% Interval (PICP = 82.4%)", 
            fontsize=8.0, fontweight='bold', color="#0F172A", ha='center', va='center', linespacing=1.2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated high-DPI architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_crisp_architecture_diagram('scratch/images/image1.png')
