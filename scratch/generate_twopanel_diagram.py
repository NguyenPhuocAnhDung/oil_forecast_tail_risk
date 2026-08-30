import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_full_twopanel_ieee_architecture(out_path='scratch/images/image1.png'):
    # Canvas size: 14.0 x 9.5 inches at 300 DPI (Wide landscape modular layout)
    fig, ax = plt.subplots(figsize=(14.0, 9.5), dpi=300)
    ax.set_xlim(0, 140)
    ax.set_ylim(0, 95)
    ax.axis('off')
    
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['mathtext.fontset'] = 'dejavusans'
    
    # -------------------------------------------------------------------------
    # MAIN HEADER BANNER (Y: 89.5 to 93.5)
    # -------------------------------------------------------------------------
    main_title_box = patches.FancyBboxPatch((2, 89.5), 136, 4.0, boxstyle="square,pad=0",
                                           facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(main_title_box)
    ax.text(70, 91.5, "NEURAL NETWORK ARCHITECTURE OF GUMNetHet & BASELINE PARADIGMS", 
            color="#000000", fontsize=11.0, fontweight='normal', ha='center', va='center')

    # =========================================================================
    # PANEL (A): GUMNetHet: Heterogeneous Mixture of Local-Global Experts (Y: 27 to 88)
    # =========================================================================
    panel_a = patches.FancyBboxPatch((2, 27.0), 136, 61.0, boxstyle="square,pad=0",
                                    facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(panel_a)
    
    # Panel A Title
    ax.text(5, 86.0, "(A) GUMNetHet: Heterogeneous Mixture of Local-Global Experts", 
            fontsize=10.0, fontweight='normal', color="#000000", ha='left', va='center')
    ax.plot([5, 134], [84.5, 84.5], color="#000000", linewidth=0.6)

    # -------------------------------------------------------------------------
    # (A) Column 1: Input Sequence Tensor (X: 4 to 26, Y: 29 to 83)
    # -------------------------------------------------------------------------
    col1_box = patches.FancyBboxPatch((4, 29.0), 22, 54.0, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(col1_box)
    ax.text(15, 81.2, "Input Sequence Tensor", fontsize=8.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(15, 79.2, r"$X \in \mathbb{R}^{B \times L \times D} \ (L = 30)$", fontsize=7.8, fontweight='normal', color="#333333", ha='center', va='center')
    ax.plot([4.8, 25.2], [77.8, 77.8], color="#CCCCCC", linewidth=0.5)

    # Sub-box 1.1: Spot Prices
    sb1 = patches.FancyBboxPatch((4.8, 62.0), 20.4, 14.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(sb1)
    ax.text(15, 74.2, "Spot Price Features", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(15, 72.4, r"$X^{\mathrm{CNN}} \in \mathbb{R}^{B \times L \times D_1}$", fontsize=7.2, fontweight='normal', color="#444444", ha='center', va='center')
    ax.plot([5.5, 24.5], [71.0, 71.0], color="#EEEEEE", linewidth=0.5)
    ax.text(15, 66.2, "• MG95, MG92, MG97\n• DO 0.001%, DO 0.05%\n• WTI, Brent, Naphtha", fontsize=7.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 1.2: Macro & GPR
    sb2 = patches.FancyBboxPatch((4.8, 46.0), 20.4, 14.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(sb2)
    ax.text(15, 58.2, "Macro & GPR Risk", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(15, 56.4, r"$X^{\mathrm{GRU}} \in \mathbb{R}^{B \times L \times D_2}$", fontsize=7.2, fontweight='normal', color="#444444", ha='center', va='center')
    ax.plot([5.5, 24.5], [55.0, 55.0], color="#EEEEEE", linewidth=0.5)
    ax.text(15, 50.2, "• Geopolitical Risk (GPR)\n• USD Index (DXY)\n• GPR_MA30, DXY_MA30", fontsize=7.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Sub-box 1.3: Ratios & Volatility
    sb3 = patches.FancyBboxPatch((4.8, 30.0), 20.4, 14.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(sb3)
    ax.text(15, 42.2, "Ratios & Volatility", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(15, 40.4, r"$X^{\mathrm{KAN}} \in \mathbb{R}^{B \times L \times D_3}$", fontsize=7.2, fontweight='normal', color="#444444", ha='center', va='center')
    ax.plot([5.5, 24.5], [39.0, 39.0], color="#EEEEEE", linewidth=0.5)
    ax.text(15, 34.2, r"• Crack Spread Ratios" + "\n" + r"• $\mathrm{Realized\ Vol\ (10d, 30d)}$" + "\n" + r"• $\mathrm{Day\_sin, Day\_cos}$", fontsize=7.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Arrows from Col 1 to Col 2
    ax.annotate('', xy=(29.5, 70.0), xytext=(25.2, 69.2), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(29.5, 53.0), xytext=(25.2, 53.2), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(29.5, 36.5), xytext=(25.2, 37.2), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))

    # -------------------------------------------------------------------------
    # (A) Column 2: 3 Heterogeneous Experts (X: 29.5 to 57.5, Y: 29 to 83)
    # -------------------------------------------------------------------------
    # Expert 1: 1D-CNN
    e1_box = patches.FancyBboxPatch((29.5, 65.5), 28.0, 17.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(e1_box)
    ax.text(43.5, 80.8, "Expert 1: Multi-Scale 1D-CNN", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([30.5, 56.5], [79.2, 79.2], color="#CCCCCC", linewidth=0.5)
    ax.text(43.5, 72.2, 
            r"• Multi-Resolution Inception: $k \in \{3, 7, 15\}$" + "\n"
            r"• Temporal Convolution + LayerNorm" + "\n"
            r"• Softmax Temporal Attention Pooling" + "\n"
            r"• Output: $f_{\mathrm{cnn}} \in \mathbb{R}^d$", 
            fontsize=7.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 2: Stacked GRU-Attention
    e2_box = patches.FancyBboxPatch((29.5, 47.0), 28.0, 17.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(e2_box)
    ax.text(43.5, 61.8, "Expert 2: Stacked GRU-Attention", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([30.5, 56.5], [60.2, 60.2], color="#CCCCCC", linewidth=0.5)
    ax.text(43.5, 53.4, 
            r"• 2-Layer Stacked Recurrent GRU ($\dim d$)" + "\n"
            r"• Temporal Multi-Head Attention Alignment" + "\n"
            r"• Captures Low-Frequency Macro Trends" + "\n"
            r"• Output: $f_{\mathrm{gru}} \in \mathbb{R}^d$", 
            fontsize=7.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Expert 3: Wavelet-KAN Shock Block
    e3_box = patches.FancyBboxPatch((29.5, 29.0), 28.0, 16.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(e3_box)
    ax.text(43.5, 43.2, "Expert 3: Wavelet-KAN Shock Block", fontsize=8.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([30.5, 56.5], [41.6, 41.6], color="#CCCCCC", linewidth=0.5)
    ax.text(43.5, 35.0, 
            r"• Mexican Hat Wavelet: $\psi(z) = (1 - z^2)e^{-0.5 z^2}$" + "\n"
            r"• Learnable Non-linear Spline Projections" + "\n"
            r"• Dampens Geopolitical Tail Risk Spikes" + "\n"
            r"• Output: $f_{\mathrm{kan}} \in \mathbb{R}^d$", 
            fontsize=7.0, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Arrows from Col 2 to Col 3 (Router)
    ax.annotate('', xy=(61.0, 68.0), xytext=(57.5, 74.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(61.0, 56.0), xytext=(57.5, 55.5), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(61.0, 44.0), xytext=(57.5, 37.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))

    # -------------------------------------------------------------------------
    # (A) Column 3: Horizon-Aware Dynamic Router (X: 61.0 to 95.0, Y: 29 to 83)
    # -------------------------------------------------------------------------
    col3_box = patches.FancyBboxPatch((61.0, 29.0), 34.0, 54.0, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(col3_box)
    ax.text(78.0, 81.0, "Step 2: Horizon-Aware Dynamic Router", fontsize=8.6, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([62.0, 94.0], [79.2, 79.2], color="#CCCCCC", linewidth=0.5)

    # Feature Concat labels (Left side of Router)
    ax.text(68.0, 76.5, "Feature Concat", fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(68.0, 69.5, r"$f_{\mathrm{cnn}} \in \mathbb{R}^d$", fontsize=7.2, fontweight='normal', color="#333333", ha='center', va='center')
    ax.text(68.0, 61.5, r"$f_{\mathrm{gru}} \in \mathbb{R}^d$", fontsize=7.2, fontweight='normal', color="#333333", ha='center', va='center')
    ax.text(68.0, 53.5, r"$f_{\mathrm{kan}} \in \mathbb{R}^d$", fontsize=7.2, fontweight='normal', color="#333333", ha='center', va='center')
    ax.text(68.0, 45.0, r"$\mathrm{Pos\ Emb\ Pos}_h$", fontsize=7.2, fontweight='normal', color="#333333", ha='center', va='center')
    ax.text(68.0, 37.0, r"$\mathrm{Context}\ [\mu_x, \sigma_x]$", fontsize=7.2, fontweight='normal', color="#333333", ha='center', va='center')

    # Arrows going into MLP Gate
    for yy in [69.5, 61.5, 53.5, 45.0, 37.0]:
        ax.annotate('', xy=(75.5, yy), xytext=(72.5, yy), arrowprops=dict(arrowstyle="->", color="#000000", lw=0.9, mutation_scale=8))

    # MLP Gating Box in center
    mlp_box = patches.FancyBboxPatch((75.5, 42.0), 10.5, 32.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(mlp_box)
    ax.text(80.75, 69.0, "MLP Gate", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(80.75, 62.0, "(128 units)\nGELU", fontsize=7.0, fontweight='normal', color="#444444", ha='center', va='center', linespacing=1.2)
    ax.text(80.75, 49.0, "+ Softmax\nLayer", fontsize=7.2, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.1)

    # Router Weights / Fused (Right side of Router)
    ax.text(90.0, 76.5, "Router Weights", fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(90.0, 68.0, r"$w_1\ (\mathrm{CNN})$" + "\n" + r"$w_2\ (\mathrm{GRU})$" + "\n" + r"$w_3\ (\mathrm{KAN})$", fontsize=6.8, fontweight='normal', color="#333333", ha='center', va='center', linespacing=1.1)
    ax.text(90.0, 58.5, r"$\sum_{j=1}^3 w_j = 1$", fontsize=7.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.annotate('', xy=(86.0, 68.0), xytext=(89.5, 68.0), arrowprops=dict(arrowstyle="<-", color="#000000", lw=0.9, mutation_scale=8))

    # Fused Output Box
    fused_box = patches.FancyBboxPatch((86.8, 33.5), 7.2, 14.0, boxstyle="square,pad=0", facecolor="#F8FAFC", edgecolor="#444444", linewidth=0.7)
    ax.add_patch(fused_box)
    ax.text(90.4, 44.5, "Fused:", fontsize=7.2, fontweight='normal', color="#000000", ha='center', va='center')
    ax.text(90.4, 38.0, r"$f_{\mathrm{fused}} = \sum w_j f_j$" + "\n" + r"$\in \mathbb{R}^{B \times d}$", fontsize=6.8, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Arrows from Router to Col 4 (Heads)
    ax.annotate('', xy=(98.5, 69.0), xytext=(95.0, 50.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(98.5, 52.0), xytext=(95.0, 42.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))
    ax.annotate('', xy=(98.5, 35.0), xytext=(95.0, 36.0), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=10))

    # -------------------------------------------------------------------------
    # (A) Column 4: Horizon Heads & Residual Scaling (X: 98.5 to 135.0, Y: 29 to 83)
    # -------------------------------------------------------------------------
    col4_box = patches.FancyBboxPatch((98.5, 29.0), 36.5, 54.0, boxstyle="square,pad=0",
                                     facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.9)
    ax.add_patch(col4_box)
    ax.text(116.75, 81.0, "Step 3: Horizon Heads & Residual Scaling", fontsize=8.6, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([99.5, 134.0], [79.2, 79.2], color="#CCCCCC", linewidth=0.5)

    # Left sub-column of Step 3: Horizon Heads
    # Short Head
    h1_box = patches.FancyBboxPatch((99.5, 63.0), 18.0, 14.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(h1_box)
    ax.text(108.5, 75.0, r"Short Head: $h \in \{1, 3\}$", fontsize=7.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([100.2, 116.8], [73.5, 73.5], color="#EEEEEE", linewidth=0.5)
    ax.text(108.5, 67.5, "• Direct Linear Projection\n• Preserves Short Momentum\n• Fast O(1) Latency Execution", fontsize=6.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Medium Head
    h2_box = patches.FancyBboxPatch((99.5, 46.5), 18.0, 15.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(h2_box)
    ax.text(108.5, 58.8, r"Medium Head: $h \in \{5, 7, 10\}$", fontsize=7.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([100.2, 116.8], [57.2, 57.2], color="#EEEEEE", linewidth=0.5)
    ax.text(108.5, 51.5, "• 2-Layer MLP + GELU Act\n• Regulatory Cycle Calibration\n• Non-linear Policy Mapping", fontsize=6.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Long Head
    h3_box = patches.FancyBboxPatch((99.5, 30.0), 18.0, 15.0, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#555555", linewidth=0.7)
    ax.add_patch(h3_box)
    ax.text(108.5, 42.2, r"Long Head: $h \in \{20, 60\}$", fontsize=7.5, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([100.2, 116.8], [40.6, 40.6], color="#EEEEEE", linewidth=0.5)
    ax.text(108.5, 35.0, "• Deep 3-Layer MLP + Norm\n• Extrapolation Drift Bounding\n• Strategic Term Forecast", fontsize=6.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Right sub-column of Step 3: Calibrated Tail Risk
    tail_box = patches.FancyBboxPatch((119.0, 30.0), 15.0, 47.5, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#000000", linewidth=0.8)
    ax.add_patch(tail_box)
    ax.text(126.5, 74.8, "Calibrated Tail Risk", fontsize=7.8, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([120.0, 133.0], [73.2, 73.2], color="#CCCCCC", linewidth=0.5)
    
    ax.text(126.5, 68.5, r"Quantile Formulation:" + "\n" + r"$\hat{y}^{(q)} = \mathrm{Head}(f_{\mathrm{fused}})$" + "\n" + r"$+ \gamma_h \cdot x_t^{\mathrm{target}}$", fontsize=6.6, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.15)
    ax.plot([120.5, 132.5], [62.0, 62.0], color="#EEEEEE", linewidth=0.5)
    
    ax.text(126.5, 56.5, r"Quantile Grid:" + "\n" + r"$q \in \{0.1, 0.5, 0.9\}$" + "\n" + r"(80% Prediction Bounds)", fontsize=6.6, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.15)
    ax.plot([120.5, 132.5], [49.5, 49.5], color="#EEEEEE", linewidth=0.5)
    
    ax.text(126.5, 44.5, r"Inverse Mapping:" + "\n" + r"$\hat{P}_{t+h} = P_t \cdot e^{\hat{r}_{t+h}}$", fontsize=6.6, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.15)
    ax.plot([120.5, 132.5], [38.5, 38.5], color="#EEEEEE", linewidth=0.5)
    
    ax.text(126.5, 34.0, r"Output Tensor Shape:" + "\n" + r"$(B, C \times |Q|)$", fontsize=6.6, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.15)

    # Arrow from Heads to Tail Risk
    ax.annotate('', xy=(119.0, 53.5), xytext=(117.5, 53.5), arrowprops=dict(arrowstyle="->", color="#000000", lw=1.1, mutation_scale=9))

    # =========================================================================
    # PANEL (B): Architectural Paradigms of Competitive Baselines (Y: 2.5 to 25.0)
    # =========================================================================
    panel_b = patches.FancyBboxPatch((2, 2.5), 136, 22.5, boxstyle="square,pad=0",
                                    facecolor="#FFFFFF", edgecolor="#000000", linewidth=1.2)
    ax.add_patch(panel_b)
    
    # Panel B Title
    ax.text(5, 22.8, "(B) Architectural Paradigms of Competitive Baselines", 
            fontsize=10.0, fontweight='normal', color="#000000", ha='left', va='center')
    ax.plot([5, 134], [21.5, 21.5], color="#000000", linewidth=0.6)

    # 4 Baseline Cards
    card_w = 31.5
    gap = 2.0
    
    # Baseline 1: PatchTST
    b1_x = 4.0
    b1_c = patches.FancyBboxPatch((b1_x, 3.8), card_w, 16.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(b1_c)
    ax.text(b1_x + card_w/2, 18.0, "PatchTST (Transformer)", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b1_x + 1, b1_x + card_w - 1], [16.8, 16.8], color="#CCCCCC", linewidth=0.5)
    ax.text(b1_x + card_w/2, 10.2, 
            "• Channel-Independent Sub-series Patching\n"
            "• Multi-Head Self-Attention Across Patches\n"
            "• Direct Linear Projection to Horizon H\n"
            "• Captures Local Semantic Temporal Patterns\n"
            "• High Memory & Long-Horizon Drift at H60", 
            fontsize=6.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Baseline 2: DLinear
    b2_x = b1_x + card_w + gap
    b2_c = patches.FancyBboxPatch((b2_x, 3.8), card_w, 16.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(b2_c)
    ax.text(b2_x + card_w/2, 18.0, "DLinear (Decomposition)", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b2_x + 1, b2_x + card_w - 1], [16.8, 16.8], color="#CCCCCC", linewidth=0.5)
    ax.text(b2_x + card_w/2, 10.2, 
            "• Moving Average Series Trend Extraction\n"
            "• Residual Seasonal Component Extraction\n"
            "• Two Independent 1-Layer Linear Projections\n"
            "• Minimalist Architecture with O(L) Cost\n"
            "• Underfits Non-linear Geopolitical Shocks", 
            fontsize=6.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Baseline 3: LSTM / GRU-Attention
    b3_x = b2_x + card_w + gap
    b3_c = patches.FancyBboxPatch((b3_x, 3.8), card_w, 16.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(b3_c)
    ax.text(b3_x + card_w/2, 18.0, "LSTM / GRU-Attention", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b3_x + 1, b3_x + card_w - 1], [16.8, 16.8], color="#CCCCCC", linewidth=0.5)
    ax.text(b3_x + card_w/2, 10.2, 
            r"• Sequential Hidden State Recursion ($h_t$)" + "\n"
            r"• Temporal Multi-Head Attention Alignment" + "\n"
            r"• Hidden Aggregation for Point Forecasts" + "\n"
            r"• Effective for Macro Trend Sequences" + "\n"
            r"• Gradient Dissipation on Long Multi-Step", 
            fontsize=6.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    # Baseline 4: XGBoost MultiOutput
    b4_x = b3_x + card_w + gap
    b4_c = patches.FancyBboxPatch((b4_x, 3.8), card_w, 16.2, boxstyle="square,pad=0", facecolor="#FFFFFF", edgecolor="#444444", linewidth=0.8)
    ax.add_patch(b4_c)
    ax.text(b4_x + card_w/2, 18.0, "XGBoost MultiOutput", fontsize=8.0, fontweight='normal', color="#000000", ha='center', va='center')
    ax.plot([b4_x + 1, b4_x + card_w - 1], [16.8, 16.8], color="#CCCCCC", linewidth=0.5)
    ax.text(b4_x + card_w/2, 10.2, 
            "• Gradient Boosted Decision Tree Ensembles\n"
            "• Direct Multi-Horizon Target Regressors\n"
            "• Tabular Feature Splitting & Regularization\n"
            "• Competitive Static Tabular Baseline\n"
            "• Lacks Temporal Latent Dynamics Modeling", 
            fontsize=6.5, fontweight='normal', color="#000000", ha='center', va='center', linespacing=1.2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated FULL TWO-PANEL (A + B) IEEE architecture diagram: {out_path}!")

if __name__ == '__main__':
    generate_full_twopanel_ieee_architecture('scratch/images/image1.png')
