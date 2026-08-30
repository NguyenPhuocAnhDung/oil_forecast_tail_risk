import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs('paper_figures', exist_ok=True)

# ==============================================================================
# FIGURE 1: SYSTEM ARCHITECTURE & EVALUATION PIPELINE (PURE WHITE / BLACK TEXT)
# ==============================================================================
def render_white_fig1():
    fig, ax = plt.subplots(figsize=(16.5, 7.5), dpi=300)
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    # Main Title Header Banner (Pure White Box, Crisp Black Border, Black Text)
    title_box = patches.FancyBboxPatch((0.2, 6.72), 16.1, 0.62, boxstyle='round,pad=0.02,rounding_size=0.03',
                                       facecolor='#FFFFFF', edgecolor='#000000', linewidth=2.0)
    ax.add_patch(title_box)
    ax.text(8.25, 7.03, 'SYSTEM ARCHITECTURE & EVALUATION PIPELINE', 
            ha='center', va='center', fontsize=13.5, fontweight='bold', color='#000000')

    stages = [
        {
            'num': 'STAGE 1', 'title': 'DATA INGESTION\n& FREEZING',
            'boxes': [
                ('Primary Spot Series', ['Platts MG95 & MG92', 'Platts DO 0.05%, DO 0.001%', 'Kerosene & Naphtha Spot']),
                ('Global Drivers', ['WTI & Brent Crude Futures', 'DXY & USD/VND Exchange', 'Geopolitical Risk (GPR)']),
                ('Freeze Verification', ['2008-11-03 to 2026-04-30', 'Frozen: End of April 2026', 'N = 4,512 Business Days'])
            ]
        },
        {
            'num': 'STAGE 2', 'title': 'LEAKAGE AUDIT\n& INTEGRITY',
            'boxes': [
                ('Missing Protocol', ['Strict Forward-Fill ($P_t = P_{t-1}$)', 'Holiday Alignments', 'No Backward Interpolation']),
                ('Decoupled Scaling', ['StandardScaler on Train Only', 'Zero Val Contamination', 'Zero Test Information Leak']),
                ('Causal Verification', ['Strict Temporal Ordering', 'No Look-Ahead Leakage', 'ADF Unit-Root Check'])
            ]
        },
        {
            'num': 'STAGE 3', 'title': 'FEATURE & TARGET\nENGINEERING',
            'boxes': [
                ('Input Partitioning', ['Price Spot: $x^{\\mathrm{CNN}} \\in \\mathbb{R}^{D_1}$', 'Macro/GPR: $x^{\\mathrm{GRU}} \\in \\mathbb{R}^{D_2}$', 'Ratios/Vol: $x^{\\mathrm{KAN}} \\in \\mathbb{R}^{D_3}$']),
                ('Sliding Window', ['Look-back Length: $L=30$', 'Batch: $X \\in \\mathbb{R}^{B \\times L \\times D}$', 'Context Stats: $[\\mu_X, \\sigma_X]$']),
                ('Cumulative Target', ['Log-Return Target:', '$R_{t \\to t+h} = \\ln(P_{t+h}/P_t)$', '$h \\in \\{1, 3, 5, 7, 10, 20, 60\\}$'])
            ]
        },
        {
            'num': 'STAGE 4', 'title': 'EVALUATION\nPROTOCOLS',
            'boxes': [
                ('Expanding Window', ['Walk-Forward Protocol', 'Simulated Daily Retraining', 'Real Deployment Mode']),
                ('Data Partitioning', ['Train: 2008-2022 (70%)', 'Val: 2022-2024 (10%)', 'Test: 2024-2026 (20%)']),
                ('Multi-Horizon Grid', ['Short: $H \\in \\{1, 3\\}$', 'Policy: $H \\in \\{5, 7, 10\\}$', 'Long: $H \\in \\{20, 60\\}$'])
            ]
        },
        {
            'num': 'STAGE 5', 'title': 'UNIFIED MODEL\nTRAINING',
            'boxes': [
                ('GUMNetHet Core', ['3 Heterogeneous Experts', 'Dynamic Context Router', 'Residual Quantile Heads']),
                ('Benchmark Suite', ['Linear: DLinear, LTSF', 'Transformers: PatchTST, iTrans', 'SSM & Found: BiMamba, Chronos']),
                ('Loss Optimization', ['Pinball Quantile Loss ($q \\in \\mathcal{Q}$)', 'Load Balance Regularization', 'AdamW + Plateau Decay'])
            ]
        },
        {
            'num': 'STAGE 6', 'title': 'EVALUATION\nDATABASE',
            'boxes': [
                ('Unified Single Store', ['Full Output JSON Repository', 'Predictions: $\\hat{R}_{t \\to t+h}, \\hat{P}_{t+h}$', 'Residual Error Arrays']),
                ('Multi-Metric Storage', ['Point: MAE, RMSE, MAPE, $R^2$', 'Directional: DA (\\%)', 'Tail: CRPS, PICP, PINAW']),
                ('Parity & Traceability', ['5 Seeds $\\times$ 4 Protocols', '47 Models $\\times$ 7 Horizons', '2 Fuel Target Datasets'])
            ]
        },
        {
            'num': 'STAGE 7', 'title': 'STATISTICAL TESTS\n& DEPLOYMENT',
            'boxes': [
                ('Significance Tests', ['Diebold-Mariano (DM Tests)', 'Two-Tailed $p$-Values', 'Friedman & Nemenyi Ranks']),
                ('Tail Risk Audit', ['Quantile Coverage Reliability', 'Downside Tail Loss', 'BOG Policy Calibration']),
                ('Deployment Ready', ['Inference Latency: 1.42 ms', 'Lightweight VRAM: 420 MB', 'Commercial Hedging Value'])
            ]
        }
    ]

    col_w = 2.16
    col_gap = 0.13
    start_x = 0.25

    for i, s in enumerate(stages):
        x = start_x + i * (col_w + col_gap)
        # Column Outline Box
        col_box = patches.FancyBboxPatch((x, 0.15), col_w, 6.42, boxstyle='round,pad=0.02,rounding_size=0.03',
                                         facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
        ax.add_patch(col_box)

        # Stage Header Box
        hdr_box = patches.FancyBboxPatch((x + 0.06, 5.58), col_w - 0.12, 0.88, boxstyle='round,pad=0.02,rounding_size=0.02',
                                         facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.4)
        ax.add_patch(hdr_box)
        ax.text(x + col_w/2, 6.22, s['num'], ha='center', va='center',
                fontsize=9.2, fontweight='bold', color='#000000')
        ax.text(x + col_w/2, 5.86, s['title'], ha='center', va='center',
                fontsize=8.6, fontweight='bold', color='#000000', multialignment='center')

        # 3 Inner Sub-Boxes
        box_y_positions = [3.80, 2.00, 0.22]
        box_h = 1.68
        for b_idx, (box_title, items) in enumerate(s['boxes']):
            by = box_y_positions[b_idx]
            sub_box = patches.FancyBboxPatch((x + 0.06, by), col_w - 0.12, box_h, boxstyle='round,pad=0.02,rounding_size=0.02',
                                             facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.0)
            ax.add_patch(sub_box)
            
            # Sub-box title
            ax.text(x + col_w/2, by + box_h - 0.22, box_title, ha='center', va='center',
                    fontsize=9.8, fontweight='bold', color='#000000')
            
            # Divider line inside sub-box
            ax.plot([x + 0.14, x + col_w - 0.14], [by + box_h - 0.38, by + box_h - 0.38], color='#000000', lw=0.6)

            # Bullet points
            item_y = by + box_h - 0.62
            for item in items:
                ax.text(x + 0.12, item_y, f"• {item}", ha='left', va='center',
                        fontsize=8.5, color='#000000', fontweight='normal')
                item_y -= 0.36

        # Flow Arrow to next stage
        if i < len(stages) - 1:
            arr_x = x + col_w + 0.01
            ax.annotate('', xy=(arr_x + col_gap - 0.02, 3.25), xytext=(arr_x, 3.25),
                        arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.6, mutation_scale=12))

    plt.tight_layout(pad=0.1)
    fig.savefig('paper_figures/fig1_system_framework.png', dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close(fig)
    print("Successfully rendered clean fig1_system_framework.png!")


# ==============================================================================
# FIGURE 2: GUMNETHET & BASELINES ARCHITECTURE (PURE WHITE / BLACK TEXT ONLY)
# ==============================================================================
def render_white_fig2():
    fig, ax = plt.subplots(figsize=(16.5, 10.8), dpi=300)
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, 10.8)
    ax.axis('off')

    # Master Header Banner (Pure White Box, Black Border, Black Text)
    master_box = patches.FancyBboxPatch((0.2, 10.15), 16.1, 0.55, boxstyle='round,pad=0.02,rounding_size=0.03',
                                        facecolor='#FFFFFF', edgecolor='#000000', linewidth=2.0)
    ax.add_patch(master_box)
    ax.text(8.25, 10.42, 'NEURAL NETWORK ARCHITECTURE OF GUMNetHet & BASELINE PARADIGMS',
            ha='center', va='center', fontsize=13.5, fontweight='bold', color='#000000')

    # =========================================================================
    # PANEL A: GUMNetHet Core Architecture (Pure White Frame, Black Text)
    # =========================================================================
    panel_a_box = patches.FancyBboxPatch((0.2, 3.25), 16.1, 6.65, boxstyle='round,pad=0.02,rounding_size=0.03',
                                         facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(panel_a_box)

    # Panel A Sub-header
    subhdr_a = patches.FancyBboxPatch((0.35, 9.38), 8.8, 0.42, boxstyle='round,pad=0.02,rounding_size=0.02',
                                      facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.2)
    ax.add_patch(subhdr_a)
    ax.text(4.75, 9.59, '(A) GUMNetHet: Heterogeneous Mixture of Local-Global Experts',
            ha='center', va='center', fontsize=11.2, fontweight='bold', color='#000000')

    # Column 1: Input Sequence Tensor (x in [0.4, 2.7])
    inp_outer = patches.FancyBboxPatch((0.4, 3.45), 2.3, 5.75, boxstyle='round,pad=0.02,rounding_size=0.02',
                                       facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.2)
    ax.add_patch(inp_outer)
    ax.text(1.55, 8.95, 'Input Sequence Tensor', ha='center', va='center', fontsize=11.0, fontweight='bold', color='#000000')
    ax.text(1.55, 8.65, '$X \\in \\mathbb{R}^{B \\times L \\times D}$  ($L = 30$)', ha='center', va='center', fontsize=10.0, color='#000000', fontweight='bold')

    inp_sub = [
        ('Spot Price Features', '$x^{\\mathrm{CNN}} \\in \\mathbb{R}^{B \\times L \\times D_1}$', ['MG95, MG92, MG97', 'DO 0.001%, DO 0.05%', 'WTI, Brent, Naphtha'], 6.95),
        ('Macro & GPR Risk', '$x^{\\mathrm{GRU}} \\in \\mathbb{R}^{B \\times L \\times D_2}$', ['Geopolitical Risk (GPR)', 'USD Index (DXY)', 'GPR_MA30, DXY_MA30'], 5.20),
        ('Ratios & Volatility', '$x^{\\mathrm{KAN}} \\in \\mathbb{R}^{B \\times L \\times D_3}$', ['Crack Spread Ratios', 'Realized Vol (10d, 30d)', 'Day_sin, Day_cos'], 3.55)
    ]
    for stitle, seqn, sitems, sy in inp_sub:
        sb = patches.FancyBboxPatch((0.5, sy), 2.1, 1.55, boxstyle='round,pad=0.02,rounding_size=0.02',
                                    facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.0)
        ax.add_patch(sb)
        ax.text(1.55, sy + 1.35, stitle, ha='center', va='center', fontsize=10.0, fontweight='bold', color='#000000')
        ax.text(1.55, sy + 1.10, seqn, ha='center', va='center', fontsize=9.2, fontweight='bold', color='#000000')
        ax.plot([0.65, 2.45], [sy + 0.95, sy + 0.95], color='#000000', lw=0.6)
        iy = sy + 0.75
        for item in sitems:
            ax.text(0.65, iy, f"• {item}", ha='left', va='center', fontsize=8.8, color='#000000', fontweight='normal')
            iy -= 0.28

    # Column 2: 3 Heterogeneous Experts (x in [3.1, 6.3])
    experts = [
        ('Expert 1: Multi-Scale 1D-CNN', 7.45, 1.75,
         ['• Multi-Resolution Inception: $k \\in \\{3, 7, 15\\}$',
          '• Temporal Convolution + LayerNorm',
          '• Softmax Temporal Attention Pooling',
          '• Output: $f_{\\mathrm{cnn}} \\in \\mathbb{R}^{B \\times d}$']),
        ('Expert 2: Stacked GRU-Attention', 5.50, 1.75,
         ['• 2-Layer Stacked Recurrent GRU (dim $d$)',
          '• Temporal Multi-Head Attention Alignment',
          '• Captures Low-Frequency Macro Trends',
          '• Output: $f_{\\mathrm{gru}} \\in \\mathbb{R}^{B \\times d}$']),
        ('Expert 3: Wavelet-KAN Shock Block', 3.45, 1.85,
         ['• Mexican Hat Wavelet: $\\psi(z) = (1 - z^2)e^{-0.5z^2}$',
          '• Learnable Non-linear Spline Projections',
          '• Dampens Geopolitical Tail Risk Spikes',
          '• Output: $f_{\\mathrm{kan}} \\in \\mathbb{R}^{B \\times d}$'])
    ]
    for etitle, ey, eh, ebullets in experts:
        eb = patches.FancyBboxPatch((3.1, ey), 3.2, eh, boxstyle='round,pad=0.02,rounding_size=0.02',
                                    facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.2)
        ax.add_patch(eb)
        ax.text(4.7, ey + eh - 0.25, etitle, ha='center', va='center', fontsize=10.8, fontweight='bold', color='#000000')
        ax.plot([3.25, 6.15], [ey + eh - 0.45, ey + eh - 0.45], color='#000000', lw=0.6)
        by = ey + eh - 0.68
        for b in ebullets:
            ax.text(3.3, by, b, ha='left', va='center', fontsize=9.2, color='#000000', fontweight='normal')
            by -= 0.32

    # Column 3: Step 2 Dynamic Router (x in [6.7, 10.9])
    router_box = patches.FancyBboxPatch((6.7, 3.45), 4.2, 5.75, boxstyle='round,pad=0.02,rounding_size=0.02',
                                        facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(router_box)
    ax.text(8.8, 8.95, 'Step 2: Horizon-Aware Dynamic Router', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000')
    ax.plot([6.9, 10.7], [8.68, 8.68], color='#000000', lw=0.8)

    # Feature Concat Section
    ax.text(7.6, 8.35, 'Feature Concat', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000')
    ax.text(7.6, 7.70, '$f_{\\mathrm{cnn}} \\in \\mathbb{R}^{d}$', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#000000')
    ax.text(7.6, 7.15, '$f_{\\mathrm{gru}} \\in \\mathbb{R}^{d}$', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#000000')
    ax.text(7.6, 6.60, '$f_{\\mathrm{kan}} \\in \\mathbb{R}^{d}$', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#000000')
    ax.text(7.6, 5.95, 'Pos Emb $\\mathrm{Pos}_h$', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#000000')
    ax.text(7.6, 5.35, 'Context $[\\mu_X, \\sigma_X]$', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#000000')

    # MLP Gate Box
    mlp_gate = patches.FancyBboxPatch((8.4, 4.90), 1.25, 3.25, boxstyle='round,pad=0.02,rounding_size=0.02',
                                      facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.2)
    ax.add_patch(mlp_gate)
    ax.text(9.02, 7.65, 'MLP Gate', ha='center', va='center', fontsize=10.8, fontweight='bold', color='#000000')
    ax.text(9.02, 7.00, '(128 units)\n+\nGELU', ha='center', va='center', fontsize=9.2, fontweight='bold', color='#000000', multialignment='center')
    ax.text(9.02, 5.50, '+\nSoftmax\nLayer', ha='center', va='center', fontsize=9.2, fontweight='bold', color='#000000', multialignment='center')

    # Router Weights
    ax.text(10.15, 8.35, 'Router Weights', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#000000')
    ax.text(10.15, 7.45, '$w_1$ (CNN)\n$w_2$ (GRU)\n$w_3$ (KAN)', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#000000', multialignment='center')
    ax.text(10.15, 6.45, '$\\sum_{j=1}^3 w_j = 1$', ha='center', va='center', fontsize=10.0, fontweight='bold', color='#000000')

    # Fused Output Box
    fused_box = patches.FancyBboxPatch((9.75, 4.80), 0.95, 1.20, boxstyle='round,pad=0.02,rounding_size=0.02',
                                       facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.0)
    ax.add_patch(fused_box)
    ax.text(10.22, 5.65, 'Fused:', ha='center', va='center', fontsize=9.0, fontweight='bold', color='#000000')
    ax.text(10.22, 5.30, '$f_{\\mathrm{fused}} = \\sum w_j f_j$', ha='center', va='center', fontsize=8.2, fontweight='bold', color='#000000')
    ax.text(10.22, 4.98, '$\\in \\mathbb{R}^{B \\times d}$', ha='center', va='center', fontsize=8.2, fontweight='bold', color='#000000')

    # Internal Router Arrows
    ax.annotate('', xy=(8.35, 6.5), xytext=(7.95, 6.5), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.5))
    ax.annotate('', xy=(9.75, 6.5), xytext=(9.68, 6.5), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.5))

    # Column 4: Step 3 Horizon Heads & Residual Scaling
    hheads_box = patches.FancyBboxPatch((11.3, 3.45), 4.8, 5.75, boxstyle='round,pad=0.02,rounding_size=0.02',
                                        facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(hheads_box)
    ax.text(13.7, 8.95, 'Step 3: Horizon Heads & Residual Scaling', ha='center', va='center', fontsize=11.5, fontweight='bold', color='#000000')
    ax.plot([11.5, 15.9], [8.68, 8.68], color='#000000', lw=0.8)

    heads = [
        ('Short Head: $h \\in \\{1, 3\\}$', 7.05, 1.50,
         ['• Direct Linear Projection',
          '• Preserves Short Momentum',
          '• Fast $O(1)$ Latency Execution']),
        ('Medium Head: $h \\in \\{5, 7, 10\\}$', 5.30, 1.55,
         ['• 2-Layer MLP + GELU Act',
          '• Regulatory Cycle Calibration',
          '• Non-linear Policy Mapping']),
        ('Long Head: $h \\in \\{20, 60\\}$', 3.55, 1.55,
         ['• Deep 3-Layer MLP + Norm',
          '• Extrapolation Drift Bounding',
          '• Strategic Term Forecast'])
    ]
    for htitle, hy, hh, hbullets in heads:
        hb = patches.FancyBboxPatch((11.45, hy), 2.3, hh, boxstyle='round,pad=0.02,rounding_size=0.02',
                                    facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.0)
        ax.add_patch(hb)
        ax.text(12.6, hy + hh - 0.22, htitle, ha='center', va='center', fontsize=10.0, fontweight='bold', color='#000000')
        ax.plot([11.55, 13.65], [hy + hh - 0.38, hy + hh - 0.38], color='#000000', lw=0.5)
        by = hy + hh - 0.58
        for b in hbullets:
            ax.text(11.55, by, b, ha='left', va='center', fontsize=8.8, color='#000000', fontweight='normal')
            by -= 0.30

    # Calibrated Tail Risk Card
    tail_card = patches.FancyBboxPatch((13.9, 3.55), 2.05, 5.00, boxstyle='round,pad=0.02,rounding_size=0.02',
                                       facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.2)
    ax.add_patch(tail_card)
    ax.text(14.92, 8.25, 'Calibrated Tail Risk', ha='center', va='center', fontsize=10.8, fontweight='bold', color='#000000')
    ax.plot([14.05, 15.80], [7.98, 7.98], color='#000000', lw=0.6)

    ax.text(14.92, 7.45, 'Quantile Formulation:\n$\\hat{y}_{t+h}^{(q)} = \\mathrm{Head}_h(f_{\\mathrm{fused}})$\n$+ \\gamma_h \\cdot x_t^{\\mathrm{target}}$',
            ha='center', va='center', fontsize=9.0, fontweight='bold', color='#000000', multialignment='center')

    ax.text(14.92, 6.20, 'Quantile Grid:\n$q \\in \\{0.1, 0.5, 0.9\\}$\n(80% Prediction Bounds)',
            ha='center', va='center', fontsize=9.0, fontweight='bold', color='#000000', multialignment='center')

    ax.text(14.92, 4.95, 'Inverse Mapping:\n$\\hat{P}_{t+h} = P_t \\cdot e^{\\hat{R}_{t \\to t+h}}$',
            ha='center', va='center', fontsize=9.0, fontweight='bold', color='#000000', multialignment='center')

    ax.text(14.92, 3.95, 'Output Tensor Shape:\n$(B, C \\times |\\mathcal{Q}|)$',
            ha='center', va='center', fontsize=9.0, fontweight='bold', color='#000000', multialignment='center')

    # Black Connecting Arrows in Panel A
    ax.annotate('', xy=(3.05, 8.35), xytext=(2.72, 7.75), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.6))
    ax.annotate('', xy=(3.05, 6.40), xytext=(2.72, 5.95), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.6))
    ax.annotate('', xy=(3.05, 4.35), xytext=(2.72, 4.35), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.6))

    ax.annotate('', xy=(6.65, 7.00), xytext=(6.35, 8.30), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.6))
    ax.annotate('', xy=(6.65, 6.35), xytext=(6.35, 6.35), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.6))
    ax.annotate('', xy=(6.65, 5.70), xytext=(6.35, 4.40), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.6))

    ax.annotate('', xy=(11.25, 7.80), xytext=(10.95, 6.35), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.6))
    ax.annotate('', xy=(11.25, 6.10), xytext=(10.95, 5.60), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.6))
    ax.annotate('', xy=(11.25, 4.35), xytext=(10.95, 4.80), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.6))

    ax.annotate('', xy=(13.85, 6.10), xytext=(13.78, 6.10), arrowprops=dict(arrowstyle="-|>", color='#000000', lw=1.5))

    # =========================================================================
    # PANEL B: Architectural Paradigms of Competitive Baselines (Pure White / Black Text)
    # =========================================================================
    panel_b_box = patches.FancyBboxPatch((0.2, 0.20), 16.1, 2.75, boxstyle='round,pad=0.02,rounding_size=0.03',
                                         facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.5)
    ax.add_patch(panel_b_box)

    # Panel B Sub-header
    subhdr_b = patches.FancyBboxPatch((0.35, 2.62), 7.5, 0.30, boxstyle='round,pad=0.02,rounding_size=0.02',
                                      facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.2)
    ax.add_patch(subhdr_b)
    ax.text(4.10, 2.77, '(B) Architectural Paradigms of Competitive Baselines',
            ha='center', va='center', fontsize=11.0, fontweight='bold', color='#000000')

    baselines = [
        ('PatchTST (Transformer)', 0.40,
         ['• Channel-Independent Sub-series Patching',
          '• Multi-Head Self-Attention Across Patches',
          '• Direct Linear Projection to Horizon $H$',
          '• Captures Local Semantic Temporal Patterns',
          '• High Memory & Long-Horizon Drift at H60']),
        ('DLinear (Decomposition)', 4.30,
         ['• Moving Average Series Trend Extraction',
          '• Residual Seasonal Component Extraction',
          '• Two Independent 1-Layer Linear Projections',
          '• Minimalist Architecture with $O(L)$ Cost',
          '• Underfits Non-linear Geopolitical Shocks']),
        ('LSTM / GRU-Attention', 8.20,
         ['• Sequential Hidden State Recursion ($h_t$)',
          '• Temporal Multi-Head Attention Alignment',
          '• Hidden Aggregation for Point Forecasts',
          '• Effective for Macro Trend Sequences',
          '• Gradient Dissipation on Long Multi-Step']),
        ('XGBoost MultiOutput', 12.10,
         ['• Gradient Boosted Decision Tree Ensembles',
          '• Direct Multi-Horizon Target Regressors',
          '• Tabular Feature Splitting & Regularization',
          '• Competitive Static Tabular Baseline',
          '• Lacks Temporal Latent Dynamics Modeling'])
    ]

    for bname, bx, bbullets in baselines:
        bcard = patches.FancyBboxPatch((bx, 0.32), 3.75, 2.15, boxstyle='round,pad=0.02,rounding_size=0.02',
                                       facecolor='#FFFFFF', edgecolor='#000000', linewidth=1.2)
        ax.add_patch(bcard)
        ax.text(bx + 1.87, 2.22, bname, ha='center', va='center', fontsize=10.8, fontweight='bold', color='#000000')
        ax.plot([bx + 0.15, bx + 3.60], [2.04, 2.04], color='#000000', lw=0.6)
        
        by = 1.82
        for b in bbullets:
            ax.text(bx + 0.18, by, b, ha='left', va='center', fontsize=9.0, color='#000000', fontweight='normal')
            by -= 0.32

    plt.tight_layout(pad=0.1)
    fig.savefig('paper_figures/fig2_gumnethet_architecture.png', dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close(fig)
    print("Successfully rendered clean fig2_gumnethet_architecture.png!")

if __name__ == '__main__':
    render_white_fig1()
    render_white_fig2()
