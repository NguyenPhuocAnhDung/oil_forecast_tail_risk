import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_large_twopanel_ieee_architecture(out_path='scratch/images/image1.png'):
    # Canvas size: 12.0 x 9.8 inches at 300 DPI
    fig, ax = plt.subplots(figsize=(12.0, 9.8), dpi=300)
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['mathtext.fontset'] = 'dejavusans'
    
    # -------------------------------------------------------------------------
    # MAIN HEADER BANNER (Y: 94.0 to 98.5) - FONT SIZE +4
    # -------------------------------------------------------------------------
    main_title_box = patches.FancyBboxPatch((2, 94.0), 116, 4.5, boxstyle="square,pad=0",
                                           facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(main_title_box)
    ax.text(60, 96.25, "NEURAL NETWORK ARCHITECTURE OF GUMNetHet & BASELINE PARADIGMS", 
            color="#000000", fontsize=12.5, fontweight='normal', ha='center', va='center')

    # =========================================================================
    # PANEL (A): GUMNetHet: Heterogeneous Mixture of Local-Global Experts (Y: 28 to 92.5)
    # =========================================================================
    panel_a = patches.FancyBboxPatch((2, 28.0), 116, 64.5, boxstyle="square,pad=0",
                                    facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(panel_a)
    
    # Panel A Title - FONT SIZE +4
    ax.text(4, 90.2, "(A) GUMNetHet: Heterogeneous Mixture of Local-Global Experts", 
            fontsize=11.5, fontweight='normal', color="#000000", ha='left', va='center')
    ax.plot([4, 116], [88.5, 88.5], color="#000000", linewidth=0.6)

    # -------------------------------------------------------------------------
    # (A) Column 1: Input Sequence Tensor (X: 3.5 to 22.5, Y: 30 to 87)
    # -------------------------------------------------------------------------
    col1_box = patches.FancyBboxPatch((3.5, 30.0), 19.0, 57.0, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(col1_box)
    ax.text(13.0, 85.0, "Input Sequence", fontsize=10.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(13.0, 82.8, r"$X \in \mathbb{R}^{B \times L \times D}\ (L=30)$", fontsize=9.5, fontweight='normal', color="#333333", ha='center', va='center')
    ax.plot([4.2, 21.8], [81.2, 81.2], color="#CCCCCC", linewidth=0.5)

    # Sub-box 1.1: Spot Prices
    sb1 = patches.FancyBboxPatch((4.2, 65.0), 17.6, 15.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(sb1)
    ax.text(13.0, 77.8, "Spot Prices", fontsize=10.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(13.0, 75.8, r"$X^{\mathrm{CNN}} \in \mathbb{R}^{B \times L \times D_1}$", fontsize=9.0, fontweight='normal', color="#444444", ha='center', va='center')
    ax.plot([5.0, 21.0], [74.2, 74.2], color="#EEEEEE", linewidth=0.5)
    ax.text(13.0, 69.5, "• MG95, MG92\n• Gasoil 0.001%\n• WTI, Brent", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 1.2: Macro & GPR
    sb2 = patches.FancyBboxPatch((4.2, 48.0), 17.6, 15.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(sb2)
    ax.text(13.0, 61.2, "Macro & GPR", fontsize=10.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(13.0, 59.2, r"$X^{\mathrm{GRU}} \in \mathbb{R}^{B \times L \times D_2}$", fontsize=9.0, fontweight='normal', color="#444444", ha='center', va='center')
    ax.plot([5.0, 21.0], [57.6, 57.6], color="#EEEEEE", linewidth=0.5)
    ax.text(13.0, 52.8, "• GPR Index\n• DXY Index\n• MA30 Trends", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 1.3: Ratios & Volatility
    sb3 = patches.FancyBboxPatch((4.2, 31.0), 17.6, 15.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(sb3)
    ax.text(13.0, 44.2, "Crack & Vol", fontsize=10.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(13.0, 42.2, r"$X^{\mathrm{KAN}} \in \mathbb{R}^{B \times L \times D_3}$", fontsize=9.0, fontweight='normal', color="#444444", ha='center', va='center')
    ax.plot([5.0, 21.0], [40.6, 40.6], color="#EEEEEE", linewidth=0.5)
    ax.text(13.0, 35.8, r"• Crack Ratios" + "\n" + r"• $\mathrm{Vol}_{10\mathrm{d}}, \mathrm{Vol}_{30\mathrm{d}}$" + "\n" + r"• Day/Month", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Arrows from Col 1 to Col 2
    ax.annotate('', xy=(25.5, 73.0), xytext=(22.5, 72.5), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(25.5, 55.5), xytext=(22.5, 55.5), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(25.5, 38.0), xytext=(22.5, 38.5), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))

    # -------------------------------------------------------------------------
    # (A) Column 2: 3 Heterogeneous Experts (X: 25.5 to 50.0, Y: 30 to 87)
    # -------------------------------------------------------------------------
    # Expert 1: 1D-CNN
    e1_box = patches.FancyBboxPatch((25.5, 68.5), 24.5, 18.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(e1_box)
    ax.text(37.75, 84.8, "Expert 1: 1D-CNN", fontsize=10.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([26.5, 49.0], [83.0, 83.0], color="#CCCCCC", linewidth=0.5)
    ax.text(37.75, 75.8, 
            r"• Inception: $k \in \{3, 7, 15\}$" + "\n"
            r"• Temporal Convolutions" + "\n"
            r"• LayerNorm + Dropout" + "\n"
            r"• Output: $f_{\mathrm{cnn}} \in \mathbb{R}^d$", 
            fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Expert 2: Stacked GRU-Attention
    e2_box = patches.FancyBboxPatch((25.5, 49.5), 24.5, 17.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(e2_box)
    ax.text(37.75, 64.8, "Expert 2: GRU-Attn", fontsize=10.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([26.5, 49.0], [63.0, 63.0], color="#CCCCCC", linewidth=0.5)
    ax.text(37.75, 56.2, 
            r"• 2-Layer Stacked GRU" + "\n"
            r"• Multi-Head Attention" + "\n"
            r"• Macro Trend Alignment" + "\n"
            r"• Output: $f_{\mathrm{gru}} \in \mathbb{R}^d$", 
            fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Expert 3: Wavelet-KAN Shock Block
    e3_box = patches.FancyBboxPatch((25.5, 30.0), 24.5, 18.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(e3_box)
    ax.text(37.75, 45.8, "Expert 3: Wav-KAN", fontsize=10.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([26.5, 49.0], [44.0, 44.0], color="#CCCCCC", linewidth=0.5)
    ax.text(37.75, 37.0, 
            r"• Mexican Hat Basis:" + "\n"
            r"  $\psi(z) = (1 - z^2)e^{-0.5 z^2}$" + "\n"
            r"• Non-linear Splines" + "\n"
            r"• Output: $f_{\mathrm{kan}} \in \mathbb{R}^d$", 
            fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.25)

    # Arrows from Col 2 to Col 3 (Router)
    ax.annotate('', xy=(53.0, 71.0), xytext=(50.0, 77.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(53.0, 58.5), xytext=(50.0, 58.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(53.0, 46.0), xytext=(50.0, 39.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))

    # -------------------------------------------------------------------------
    # (A) Column 3: Horizon-Aware Dynamic Router (X: 53.0 to 82.0, Y: 30 to 87)
    # -------------------------------------------------------------------------
    col3_box = patches.FancyBboxPatch((53.0, 30.0), 29.0, 57.0, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(col3_box)
    ax.text(67.5, 84.8, "Step 2: Dynamic Router", fontsize=10.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([54.0, 81.0], [83.0, 83.0], color="#CCCCCC", linewidth=0.5)

    # Feature Concat labels
    ax.text(59.5, 80.0, "Inputs", fontsize=9.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(59.5, 72.5, r"$f_{\mathrm{cnn}} \in \mathbb{R}^d$", fontsize=9.0, fontweight='normal', color="#333333", ha='center', va='center')
    ax.text(59.5, 63.5, r"$f_{\mathrm{gru}} \in \mathbb{R}^d$", fontsize=9.0, fontweight='normal', color="#333333", ha='center', va='center')
    ax.text(59.5, 54.5, r"$f_{\mathrm{kan}} \in \mathbb{R}^d$", fontsize=9.0, fontweight='normal', color="#333333", ha='center', va='center')
    ax.text(59.5, 45.5, r"$\mathrm{Pos}_h$", fontsize=9.0, fontweight='normal', color="#333333", ha='center', va='center')
    ax.text(59.5, 36.5, r"$[\mu_x, \sigma_x]$", fontsize=9.0, fontweight='normal', color="#333333", ha='center', va='center')

    # Arrows going into MLP Gate
    for yy in [72.5, 63.5, 54.5, 45.5, 36.5]:
        ax.annotate('', xy=(66.0, yy), xytext=(63.5, yy), arrowprops=dict(arrowstyle="->", color="#000000", lw=0.9, mutation_scale=8))

    # MLP Gating Box in center
    mlp_box = patches.FancyBboxPatch((66.0, 42.0), 9.0, 34.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(mlp_box)
    ax.text(70.5, 71.0, "MLP Gate", fontsize=9.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(70.5, 63.0, "(128 units)\nGELU", fontsize=8.2, fontweight='normal', color="#444444", ha='center', va='center', linespacing=1.2)
    ax.text(70.5, 49.0, "+ Softmax\nLayer", fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.1)

    # Router Weights / Fused Output
    ax.text(78.0, 80.0, "Weights", fontsize=9.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(78.0, 70.5, r"$w_1\ (\mathrm{CNN})$" + "\n" + r"$w_2\ (\mathrm{GRU})$" + "\n" + r"$w_3\ (\mathrm{KAN})$", fontsize=8.0, fontweight='normal', color="#333333", ha='center', va='center', linespacing=1.15)
    ax.text(78.0, 60.5, r"$\sum w_j = 1$", fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.annotate('', xy=(75.0, 70.5), xytext=(77.5, 70.5), arrowprops=dict(arrowstyle="<-", color="#000000", lw=0.9, mutation_scale=8))

    # Fused Box
    fused_box = patches.FancyBboxPatch((75.5, 34.0), 5.8, 16.0, boxstyle="square,pad=0", facecolor="#F8FAFC", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(fused_box)
    ax.text(78.4, 46.5, "Fused:", fontsize=8.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(78.4, 39.5, r"$f_{\mathrm{fused}} = \sum w_j f_j$" + "\n" + r"$\in \mathbb{R}^{B \times d}$", fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Arrows from Router to Col 4 (Heads)
    ax.annotate('', xy=(85.0, 72.0), xytext=(82.0, 52.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(85.0, 54.0), xytext=(82.0, 44.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(85.0, 36.0), xytext=(82.0, 36.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))

    # -------------------------------------------------------------------------
    # (A) Column 4: Horizon Heads & Residual Scaling (X: 85.0 to 116.5, Y: 30 to 87)
    # -------------------------------------------------------------------------
    col4_box = patches.FancyBboxPatch((85.0, 30.0), 31.5, 57.0, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(col4_box)
    ax.text(100.75, 84.8, "Step 3: Horizon Heads & Quantiles", fontsize=10.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([86.0, 115.5], [83.0, 83.0], color="#CCCCCC", linewidth=0.5)

    # Left sub-column of Step 3: Horizon Heads
    # Short Head
    h1_box = patches.FancyBboxPatch((86.0, 67.5), 15.5, 15.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(h1_box)
    ax.text(93.75, 79.8, r"Short: $h \in \{1, 3\}$", fontsize=9.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([86.8, 100.8], [78.2, 78.2], color="#EEEEEE", linewidth=0.5)
    ax.text(93.75, 72.8, "• Linear Proj\n• Spot Momentum\n• Fast O(1) Time", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Medium Head
    h2_box = patches.FancyBboxPatch((86.0, 49.0), 15.5, 16.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(h2_box)
    ax.text(93.75, 62.8, r"Med: $h \in \{5, 7, 10\}$", fontsize=9.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([86.8, 100.8], [61.2, 61.2], color="#EEEEEE", linewidth=0.5)
    ax.text(93.75, 55.0, "• 2-Layer MLP\n• 7-Day Cycle\n• Non-linear Shift", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Long Head
    h3_box = patches.FancyBboxPatch((86.0, 31.0), 15.5, 16.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(h3_box)
    ax.text(93.75, 44.5, r"Long: $h \in \{20, 60\}$", fontsize=9.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([86.8, 100.8], [42.8, 42.8], color="#EEEEEE", linewidth=0.5)
    ax.text(93.75, 37.0, r"• 3-Layer MLP" + "\n" + r"• Residual $\gamma_h$" + "\n" + r"• Bound Drift", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Right sub-column of Step 3: Calibrated Tail Risk
    tail_box = patches.FancyBboxPatch((102.5, 31.0), 13.0, 51.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.8)
    ax.add_patch(tail_box)
    ax.text(109.0, 79.8, "Tail Risk Bounds", fontsize=9.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([103.5, 114.5], [78.2, 78.2], color="#CCCCCC", linewidth=0.5)
    
    ax.text(109.0, 72.8, r"$\hat{y}^{(q)} = \mathrm{Head}(f)$" + "\n" + r"$+ \gamma_h \cdot x_t^{\mathrm{target}}$", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)
    ax.plot([103.5, 114.5], [66.5, 66.5], color="#EEEEEE", linewidth=0.5)
    
    ax.text(109.0, 60.5, r"Quantile Grid:" + "\n" + r"$q \in \{0.1, 0.5, 0.9\}$" + "\n" + r"(80% Bounds)", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)
    ax.plot([103.5, 114.5], [53.5, 53.5], color="#EEEEEE", linewidth=0.5)
    
    ax.text(109.0, 47.5, r"Inverse Map:" + "\n" + r"$\hat{P}_{t+h} = P_t e^{\hat{r}_{t+h}}$", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)
    ax.plot([103.5, 114.5], [41.0, 41.0], color="#EEEEEE", linewidth=0.5)
    
    ax.text(109.0, 36.0, r"$\mathrm{PICP} = 82.4\%$" + "\n" + r"$\mathrm{PINAW} = 0.142$", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Arrow from Heads to Tail Risk
    ax.annotate('', xy=(102.5, 55.0), xytext=(101.5, 55.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=9))

    # =========================================================================
    # PANEL (B): Architectural Paradigms of Competitive Baselines (Y: 2.5 to 26.0) - FONT SIZE +4
    # =========================================================================
    panel_b = patches.FancyBboxPatch((2, 2.5), 116, 23.5, boxstyle="square,pad=0",
                                    facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(panel_b)
    
    # Panel B Title
    ax.text(4, 23.8, "(B) Architectural Paradigms of Competitive Baselines", 
            fontsize=11.5, fontweight='normal', color="#000000", ha='left', va='center')
    ax.plot([4, 116], [22.4, 22.4], color="#000000", linewidth=0.6)

    # 4 Baseline Cards
    card_w = 26.8
    gap = 1.6
    
    # Baseline 1: PatchTST
    b1_x = 3.5
    b1_c = patches.FancyBboxPatch((b1_x, 3.8), card_w, 17.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(b1_c)
    ax.text(b1_x + card_w/2, 18.8, "PatchTST (Transformer)", fontsize=9.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b1_x + 1, b1_x + card_w - 1], [17.4, 17.4], color="#CCCCCC", linewidth=0.5)
    ax.text(b1_x + card_w/2, 10.5, 
            "• Sub-series Patching (CI)\n"
            "• Multi-Head Attention\n"
            "• Direct Linear to Horizon H\n"
            "• Captures Local Patterns\n"
            "• High Memory Drift at H60", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Baseline 2: DLinear
    b2_x = b1_x + card_w + gap
    b2_c = patches.FancyBboxPatch((b2_x, 3.8), card_w, 17.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(b2_c)
    ax.text(b2_x + card_w/2, 18.8, "DLinear (Decomposition)", fontsize=9.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b2_x + 1, b2_x + card_w - 1], [17.4, 17.4], color="#CCCCCC", linewidth=0.5)
    ax.text(b2_x + card_w/2, 10.5, 
            "• Moving Average Trend\n"
            "• Residual Seasonal Part\n"
            "• 2 Linear Projections\n"
            "• Minimalist O(L) Cost\n"
            "• Underfits Non-linear Shocks", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Baseline 3: LSTM / GRU-Attention
    b3_x = b2_x + card_w + gap
    b3_c = patches.FancyBboxPatch((b3_x, 3.8), card_w, 17.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(b3_c)
    ax.text(b3_x + card_w/2, 18.8, "LSTM / GRU-Attention", fontsize=9.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b3_x + 1, b3_x + card_w - 1], [17.4, 17.4], color="#CCCCCC", linewidth=0.5)
    ax.text(b3_x + card_w/2, 10.5, 
            r"• Hidden Recursion ($h_t$)" + "\n"
            r"• Temporal Multi-Head Attn" + "\n"
            r"• Hidden Aggregation" + "\n"
            r"• Effective for Macro Trends" + "\n"
            r"• Gradient Dissipation at H60", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Baseline 4: XGBoost MultiOutput
    b4_x = b3_x + card_w + gap
    b4_c = patches.FancyBboxPatch((b4_x, 3.8), card_w, 17.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(b4_c)
    ax.text(b4_x + card_w/2, 18.8, "XGBoost MultiOutput", fontsize=9.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b4_x + 1, b4_x + card_w - 1], [17.4, 17.4], color="#CCCCCC", linewidth=0.5)
    ax.text(b4_x + card_w/2, 10.5, 
            "• Boosted Decision Trees\n"
            "• Multi-Horizon Regressors\n"
            "• Tabular Feature Splitting\n"
            "• Static Tabular Baseline\n"
            "• Lacks Temporal Dynamics", 
            fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated 4-SIZE LARGER 2-panel architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_large_twopanel_ieee_architecture('scratch/images/image1.png')
