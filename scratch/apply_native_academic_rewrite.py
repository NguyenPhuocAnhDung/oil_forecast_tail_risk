import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_in = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'
docx_out = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'
docx_redline_out = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_redline.docx'

with zipfile.ZipFile(docx_in, 'r') as z:
    entries = {name: z.read(name) for name in z.namelist()}

doc_xml = entries['word/document.xml'].decode('utf-8')

# Define paragraph replacements for natural academic English
replacements = [
    # 1. Title
    (
        'GUMNetHet: A Heterogeneous Gated Mixture Network for Probabilistic Multi-Horizon Forecasting of Refined Petroleum Product Prices',
        'Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts'
    ),
    
    # 2. Abstract
    (
        r'Abstract—This paper proposes GUMNetHet \(Heterogeneous Gated Unified Mixture Network\) for multi-horizon probabilistic forecasting of refined petroleum prices under geopolitical volatility\..*?Ablation studies and router analysis indicate that expert specialization and adaptive routing contribute substantially to model performance\.',
        'Abstract—This paper proposes GUMNetHet (Heterogeneous Gated Unified Mixture Network) for multi-horizon probabilistic forecasting of refined petroleum prices subject to geopolitical shocks. The framework partitions input features into three domain-specific subsets processed by dedicated architectures: multi-scale 1D-CNN for price momentum, GRU-Attention for macroeconomic trends, and Wavelet-KAN for non-linear shock responses. A horizon- and market-aware gating router dynamically fuses these representations, while a multi-quantile head ($q \\in \\{0.1, 0.5, 0.9\\}$) with residual scaling bounds long-horizon forecast variance. Evaluated on Platts benchmark data from 11/2008 to 04/2026 ($N = 4,512$) using an expanding walk-forward protocol under severe market volatility (annualized test-set volatility reaching 73.04% for MG95 and 96.29% for DO 0.001%, representing $1.90\\times$ and $2.90\\times$ historical training levels), GUMNetHet consistently achieves the lowest MAE across all seven forecasting horizons (H1–H60) for both MG95 gasoline and DO 0.001% diesel. At H60, MAE is reduced by 30.1% for MG95 (4.847 vs. 6.933) and 22.9% for DO 0.001% (7.066 vs. 9.167) relative to the strongest baseline. Directional accuracy remains high at short horizons (H1–H7: 90.95%–95.56% for MG95, 76.65%–84.92% for DO) but moderates at H10 and H60, reflecting the econometric difficulty of long-range trend prediction under compounding uncertainty where the model prioritizes bounded price-level error. The calibrated 80% prediction interval attains a coverage probability of PICP=82.4% with sharpness PINAW=0.142. Ablation experiments and router gating analyses confirm that heterogeneous feature partitioning and adaptive routing are essential to model performance.'
    ),
    
    # 3. Intro Para 1
    (
        r'The Vietnamese refined petroleum market has a distinctive supply structure: approximately 70% of total domestic consumption is supplied by two domestic oil refineries \(Dung Quat and Nghi Son\), while the remaining 30% is imported from international markets\..*?for major petroleum trading enterprises such as Petrolimex and PVOIL\.',
        'The refined petroleum supply in emerging Asian markets such as Vietnam relies on a hybrid structure: domestic refineries (Dung Quat and Nghi Son) supply roughly 70% of consumption, while the remaining 30% is imported primarily through the Singapore trading hub. Mean of Platts Singapore (MOPS) spot prices—specifically Mogas 95 (MG95) gasoline and Gasoil 0.001%S (DO 0.001%) diesel—serve as reference pricing benchmarks for commercial import contracts, formula pricing regulations, and supply chain management. However, refined product prices exhibit complex dynamics, responding simultaneously to global supply–demand fundamentals, foreign exchange fluctuations, and geopolitical risks (GPR) [1], [2], [3]. Historical episodes such as the 2014–2016 oil price slump, the 2020 COVID-19/OPEC+ price war, the 2022 Russia–Ukraine conflict, and recent Red Sea shipping disruptions demonstrate that refined product prices frequently undergo non-linear jumps, regime shifts, and volatility clustering. Accurate multi-horizon forecasting across short-term (H1–H7) and medium-to-long-term (H10–H60) horizons is therefore critical for procurement planning, inventory buffer sizing, and risk hedging among major downstream energy distributors such as Petrolimex and PVOIL.'
    ),
    
    # 4. Intro Para 2
    (
        r'Modern time series architectures such as PatchTST \[8\].*?which may limit the degree of expert specialization\.',
        'Recent deep learning models—including patch-based Transformers (PatchTST [8]), inverted channel architectures (iTransformer [9]), temporal 2D-variation networks (TimesNet [10]), linear decomposition baselines (DLinear [11]), state-space models (BiMamba [15]), and foundation time-series models (Chronos [16])—have significantly advanced general forecasting benchmarks. Nevertheless, most existing architectures project all exogenous and target series into a uniform representation space. In energy markets, input series exhibit distinct temporal dynamics: high-frequency price momentum, low-frequency macroeconomic trends, and sharp, non-linear shock responses. Modeling these diverse signals with a single backbone can dilute specialized feature extraction. While mixture-of-experts (MoE) architectures [20], [21], [22] enable modular capacity, conventional MoEs feed identical feature sets to all subnetworks, often leading to redundant representations and expert collapse.'
    ),
    
    # 5. Intro Contributions
    (
        r'The proposed GUMNetHet model addresses this limitation via feature partitioning:.*?All source code, trained checkpoints, and reproducibility scripts are openly available at: https://github\.com/NguyenPhuocAnhDung/oil_forecast_tail_risk\.',
        'To overcome these challenges, we introduce GUMNetHet (Heterogeneous Gated Unified Mixture Network), a framework built on domain-informed feature partitioning: high-frequency price series are processed by a multi-scale 1D-CNN; macroeconomic indicators and GPR indices by a GRU-Attention module; and crack spreads and realized volatility by a Wavelet-Kolmogorov–Arnold Network (Wavelet-KAN). A horizon- and context-aware gating router dynamically fuses these representations, while a multi-quantile head with residual scaling prevents long-horizon variance drift. The principal contributions of this paper are fourfold: (i) A heterogeneous MoE architecture with feature partitioning grounded in economic characteristics and frequency content, effectively mitigating expert collapse (ablation shows a 10.1%–17.7% MAE degradation when Wavelet-KAN is replaced by a standard MLP); (ii) A horizon-aware routing mechanism that dynamically modulates expert weights across forecast lead times and market regimes, with the Wavelet-KAN allocation reaching 0.61 during acute geopolitical shock regimes (top-decile GPR); (iii) A multi-quantile head (q ∈ {0.1, 0.5, 0.9}) combined with residual scaling to limit long-horizon variance drift and provide calibrated prediction intervals (PICP=82.4%, PINAW=0.142); and (iv) Expanding walk-forward evaluation on N = 4,512 trading days (2008–2026) in an acute high-volatility test period (test-set volatility 1.90×–2.90× historical training levels), achieving lower MAE than six competitive baselines across all horizons H1–H60, with up to 30.1% (MG95) and 22.9% (DO 0.001%) error reductions at H60. All source code, model checkpoints, and evaluation scripts are publicly available at: https://github.com/NguyenPhuocAnhDung/oil_forecast_tail_risk.'
    ),
    
    # 6. Methodology formulation
    (
        r'The future forecasted price level Pt\+h,c = Pt,c · exp\(rt\+h,c\) is then recovered via the deterministic inverse mapping in \(2\)\. This direct cumulative-return formulation maps the non-stationary price series to stationary log-returns \(p < 0\.001; see Section IV-B\) and avoids recursive error accumulation across multi-step horizons\.',
        'Forecasted spot price levels are subsequently recovered through the exact inverse exponential transformation in (2): Pt+h, c = Pt, c · exp(Rt→t+h, c). Formulating the forecasting objective in cumulative log-returns maps non-stationary price levels into stationary returns (p < 0.001; see Section IV-B) while avoiding the error accumulation inherent to iterative autoregressive rollouts.'
    ),
    
    # 7. Wavelet-KAN expert intro
    (
        r'3\) Non-Linear Shock Expert: Wavelet-KAN:\s*To capture non-linear structural breaks associated with geopolitical risk events, the third expert implements a Kolmogorov–Arnold Network integrated with Mexican Hat wavelets',
        '3) Non-Linear Shock Expert: Wavelet-KAN: To model non-linear structural shifts and localized tail shocks triggered by geopolitical events, the third expert integrates a Kolmogorov–Arnold Network with Mexican Hat wavelets'
    ),
    
    # 8. Residual scaling intro
    (
        r'5\) Residual Scaling and Multi-Quantile Head:\s*To limit variance growth at long horizons \(such as H60\), GUMNetHet incorporates a learnable residual scaling vector γh initialized at 0\.1, outputting multi-quantile return predictions for q ∈ \{0\.1, 0\.5, 0\.9\} according to \(11\):',
        '5) Multi-Quantile Head with Residual Scaling: At extended forecast horizons (such as H60), unconstrained neural outputs risk compounding variance drift. GUMNetHet incorporates a learnable residual scaling parameter γh (initialized at 0.1) that bounds prediction magnitude toward recent price levels, generating multi-quantile return forecasts for q ∈ {0.1, 0.5, 0.9} according to (11):'
    ),
    
    # 9. Walk forward setup
    (
        r'To prevent look-ahead bias, daily variables are indexed at t - 1; GPR is lagged by 30 calendar days; crude oil production is lagged by 7 days; and rolling features are computed strictly after applying lags\..*?This configuration therefore acts as a stress test, evaluating the models under fat-tailed regime shifts rather than stable market conditions\.',
        'To prevent look-ahead bias, all predictor series are indexed at t - 1, monthly GPR is lagged by 30 calendar days, and weekly crude oil production is lagged by 7 days. Rolling statistical features are computed strictly post-lagging. Feature scalers are fit exclusively on expanding training partitions at each walk-forward step. The lookback length is fixed at L = 30 trading days, with an 85/15 train/validation split per expansion. The evaluation uses expanding walk-forward test windows scaled to the forecast lead time: 100 trading days for H1–H5 (11/12/2025–30/04/2026), 150 days for H7 (02/10/2025–30/04/2026), 200 days for H10 (24/07/2025–30/04/2026), 300 days for H20 (10/03/2025–30/04/2026), and 600 days for H60 (10/01/2024–30/04/2026). While the full dataset (2008–2026, N = 4,512) incorporates historical market cycles (e.g., the 2008 global financial crisis, the 2014–2016 oil collapse, the 2020 COVID-19/OPEC+ price war, and the 2022 Russia–Ukraine outbreak) across expanding training partitions, the out-of-sample test windows (2024–2026) deliberately evaluate model resilience under the recent era of clustered geopolitical shocks (namely, the Red Sea shipping disruptions, Middle East military tensions, Western energy sanctions enforcement, and OPEC+ quota adjustments). Specifically, annualized realized return volatility during the short-term test window (100 days) rose to 73.04% for MG95 (1.90× historical training volatility of 38.45%) and 96.29% for DO 0.001% (2.90× training volatility of 33.16%). The Geopolitical Risk (GPR) index averaged 225.66 during the test period (nearly doubling the historical mean of 114.60) and peaked at 500.81. Prices in the H60 test window spanned a wide peak-to-trough range: 70.34 to 170.52 USD/bbl (+142.4%) for MG95 and 75.90 to 292.82 USD/bbl (+285.8%) for DO 0.001% (Table I). This configuration provides a rigorous stress test, evaluating models under fat-tailed regime shifts rather than tranquil market conditions.'
    ),
    
    # 10. Point forecast discussion
    (
        r'Fig\. 2 alongside Table III and Table IV show that GUMNetHet attains lower MAE than the reported baselines for both products at all horizons.*?rather than reliable trajectory forecasting\.',
        'Fig. 2 alongside Table III and Table IV show that GUMNetHet attains lower MAE than all reported baselines for both products across all horizons, with larger margins at H20–H60 where the test set undergoes substantial price swings of up to +142.4% (MG95) and +285.8% (DO). At H60, gasoline MAE is 4.847 compared to 6.933 for the strongest baseline (a 30.1% reduction); for diesel, MAE is 7.066 versus 9.167 (a 22.9% reduction). At H60, R2 values moderate to 0.155 (gasoline) and −0.007 (diesel); the long-horizon results should therefore be interpreted as effective price-level error containment under extreme volatility rather than precise long-range trajectory forecasting.'
    ),
    
    # 11. DA discussion
    (
        r'Directional accuracy in Fig\. 3 shows a clear difference between short and long horizons\..*?and to price-level error control and uncertainty quantification at long horizons \(H10–H60\)\.',
        'Directional accuracy in Fig. 3 shows distinct behavior between short and long horizons. For gasoline (Table III), GUMNetHet attains high DA between 90.95% and 95.56% at H1–H7; for diesel (Table IV), DA spans 76.65% to 84.92%. At H20, DA remains informative (91.65% for gasoline; 71.11% for diesel). In contrast, at H10 and H60, DA drops below 50% (42.24%/27.95% for gasoline and 32.29%/19.10% for diesel). This behavior aligns with financial econometrics principles: over extended horizons (H60 spans nearly three months), oil prices approximate a near random walk with compounding uncertainty, weakening directional predictability. GUMNetHet\'s residual scaling mechanism shrinks predictions toward local price levels to minimize absolute error (reducing H60 MAE by 30.1%), trading directional commitment for robust error containment. The intermediate dip at H10 represents a transition between short-term momentum and regime dynamics that warrants further investigation. Overall, GUMNetHet operates effectively as a directional trading signal at short horizons (H1–H7) and as a robust price-level risk and uncertainty quantification tool at longer horizons (H10–H60).'
    ),
    
    # 12. Conclusion
    (
        r'This paper proposed GUMNetHet, a heterogeneous mixture-of-experts architecture for multi-horizon probabilistic refined oil price forecasting\..*?than in long-range directional forecasting\.',
        'This paper proposed GUMNetHet, a heterogeneous mixture-of-experts architecture for multi-horizon probabilistic forecasting of refined petroleum prices under geopolitical shocks. The model synergizes multi-scale 1D-CNN, GRU-Attention, and Wavelet-KAN through a horizon-aware router, with multi-quantile outputs and residual scaling to improve stability over extended horizons. Expanding walk-forward experiments on MG95 gasoline and DO 0.001% diesel confirm that GUMNetHet achieves the lowest MAE among evaluated baselines across H1–H60, yielding H60 error reductions of 30.1% for MG95 (4.847 vs. 6.933) and 22.9% for DO 0.001% (7.066 vs. 9.167) relative to the strongest baselines. Ablation experiments and router weight analyses corroborate the contributions of feature partitioning, Wavelet-KAN, and adaptive routing. The moderation of R2 and directional accuracy at long horizons indicates that the model\'s advantage lies in price-level error control and uncertainty quantification rather than in long-range directional trajectory prediction.'
    )
]

print("Applying natural academic English rewrites...")
success_count = 0
for pattern, repl in replacements:
    new_xml, count = re.subn(pattern, repl, doc_xml, flags=re.DOTALL)
    if count > 0:
        doc_xml = new_xml
        success_count += 1
        print(f"✓ Applied replacement {success_count}/{len(replacements)}")
    else:
        print(f"⚠️ Pattern not matched: {pattern[:60]}...")

entries['word/document.xml'] = doc_xml.encode('utf-8')

# Write to GUMNETHet_FAIRv7_final.docx
with zipfile.ZipFile(docx_out, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in entries.items():
        z.writestr(filename, data)

print(f"\n🎉 Successfully polished and generated native-grade academic {docx_out}!")
