import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_in = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'
docx_out = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'
docx_redline = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_redline.docx'

with zipfile.ZipFile(docx_in, 'r') as z:
    entries = {name: z.read(name) for name in z.namelist()}

root = ET.fromstring(entries['word/document.xml'])

W_NS = 'http://purl.oclc.org/ooxml/wordprocessingml/main'
M_NS = 'http://purl.oclc.org/ooxml/officeDocument/math'

def get_p_text(p):
    txts = []
    for t in p.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            txts.append(t.text)
    return ''.join(txts)

def set_p_text(p, new_text):
    # Find all <w:r> runs and keep the first one's formatting, remove others, update text in the first run
    runs = p.findall(f'{{{W_NS}}}r')
    if not runs:
        # Create a new run
        r = ET.SubElement(p, f'{{{W_NS}}}r')
        t = ET.SubElement(r, f'{{{W_NS}}}t')
        t.text = new_text
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        return
    
    first_r = runs[0]
    # Check if first run has rPr
    rPr = first_r.find(f'{{{W_NS}}}rPr')
    # Remove all children of first_r except rPr
    for child in list(first_r):
        if child.tag != f'{{{W_NS}}}rPr':
            first_r.remove(child)
    
    # Add single w:t with new_text
    t = ET.SubElement(first_r, f'{{{W_NS}}}t')
    t.text = new_text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    
    # Remove remaining runs
    for r in runs[1:]:
        p.remove(r)

# Mapping of search triggers to polished, natural, authentic academic text:
updates = [
    # 1. Abstract
    (
        'Abstract—This paper proposes GUMNetHet',
        'Abstract—This paper proposes GUMNetHet (Heterogeneous Gated Unified Mixture Network) for multi-horizon probabilistic forecasting of refined petroleum product prices subject to geopolitical shocks. The framework partitions input features into three domain-specific subsets processed by dedicated architectures: multi-scale 1D-CNN for price momentum, GRU-Attention for macroeconomic trends, and Wavelet-KAN for non-linear shock responses. A horizon- and market-aware gating router dynamically fuses these expert representations, while a multi-quantile head (q ∈ {0.1, 0.5, 0.9}) with residual scaling bounds long-horizon forecast variance. Evaluated on Platts Singapore benchmark data from 11/2008 to 04/2026 (N = 4,512) using an expanding walk-forward protocol under severe market volatility (annualized test-set volatility reaching 73.04% for MG95 and 96.29% for DO 0.001%, representing 1.90× and 2.90× historical training levels), GUMNetHet consistently achieves the lowest MAE across all seven forecasting horizons (H1–H60) for both MG95 gasoline and DO 0.001% diesel. At H60, MAE is reduced by 30.1% for MG95 (4.847 vs. 6.933) and 22.9% for DO 0.001% (7.066 vs. 9.167) relative to the strongest baseline. Directional accuracy remains high at short horizons (H1–H7: 90.95%–95.56% for MG95, 76.65%–84.92% for DO) but moderates at H10 and H60, reflecting the econometric difficulty of long-range trend prediction under compounding uncertainty where the model prioritizes bounded price-level error. The calibrated 80% prediction interval attains a coverage probability of PICP=82.4% with sharpness PINAW=0.142. Ablation experiments and router gating analyses confirm that heterogeneous feature partitioning and adaptive routing are essential to model performance.'
    ),
    
    # 2. Intro Para 1
    (
        'The Vietnamese refined petroleum market has a distinctive supply structure',
        'The refined petroleum supply in emerging Asian markets such as Vietnam relies on a hybrid structure: domestic refineries (Dung Quat and Nghi Son) supply roughly 70% of consumption, while the remaining 30% is imported primarily through the Singapore trading hub. Mean of Platts Singapore (MOPS) spot prices—specifically Mogas 95 (MG95) gasoline and Gasoil 0.001%S (DO 0.001%) diesel—serve as reference pricing benchmarks for commercial import contracts, formula pricing regulations, and supply chain management. However, refined product prices exhibit complex dynamics, responding simultaneously to global supply–demand fundamentals, foreign exchange fluctuations, and geopolitical risks (GPR) [1], [2], [3]. Historical episodes such as the 2014–2016 oil price slump, the 2020 COVID-19/OPEC+ price war, the 2022 Russia–Ukraine conflict, and recent Red Sea shipping disruptions demonstrate that refined product prices frequently undergo non-linear jumps, regime shifts, and volatility clustering. Accurate multi-horizon forecasting across short-term (H1–H7) and medium-to-long-term (H10–H60) horizons is therefore critical for procurement planning, inventory buffer sizing, and risk hedging among major downstream energy distributors such as Petrolimex and PVOIL.'
    ),
    
    # 3. Intro Para 2
    (
        'Modern time series architectures such as PatchTST',
        'Recent deep learning models—including patch-based Transformers (PatchTST [8]), inverted channel architectures (iTransformer [9]), temporal 2D-variation networks (TimesNet [10]), linear decomposition baselines (DLinear [11]), state-space models (BiMamba [15]), and foundation time-series models (Chronos [16])—have significantly advanced general forecasting benchmarks. Nevertheless, most existing architectures project all exogenous and target series into a uniform representation space. In energy markets, input series exhibit distinct temporal dynamics: high-frequency price momentum, low-frequency macroeconomic trends, and sharp, non-linear shock responses. Modeling these diverse signals with a single backbone can dilute specialized feature extraction. While mixture-of-experts (MoE) architectures [20], [21], [22] enable modular capacity, conventional MoEs feed identical feature sets to all subnetworks, often leading to redundant representations and expert collapse.'
    ),
    
    # 4. Intro Contributions
    (
        'The proposed GUMNetHet model addresses this limitation via feature partitioning',
        'To overcome these challenges, we introduce GUMNetHet (Heterogeneous Gated Unified Mixture Network), a framework built on domain-informed feature partitioning: high-frequency price series are processed by a multi-scale 1D-CNN; macroeconomic indicators and GPR indices by a GRU-Attention module; and crack spreads and realized volatility by a Wavelet-Kolmogorov–Arnold Network (Wavelet-KAN). A horizon- and context-aware gating router dynamically fuses these representations, while a multi-quantile head with residual scaling prevents long-horizon variance drift. The principal contributions of this paper are fourfold: (i) A heterogeneous MoE architecture with feature partitioning grounded in economic characteristics and frequency content, effectively mitigating expert collapse (ablation shows a 10.1%–17.7% MAE degradation when Wavelet-KAN is replaced by a standard MLP); (ii) A horizon-aware routing mechanism that dynamically modulates expert weights across forecast lead times and market regimes, with the Wavelet-KAN allocation reaching 0.61 during acute geopolitical shock regimes (top-decile GPR); (iii) A multi-quantile head (q ∈ {0.1, 0.5, 0.9}) combined with residual scaling to limit long-horizon variance drift and provide calibrated prediction intervals (PICP=82.4%, PINAW=0.142); and (iv) Expanding walk-forward evaluation on N = 4,512 trading days (2008–2026) in an acute high-volatility test period (test-set volatility 1.90×–2.90× historical training levels), achieving lower MAE than six competitive baselines across all horizons H1–H60, with up to 30.1% (MG95) and 22.9% (DO 0.001%) error reductions at H60. All source code, model checkpoints, and evaluation scripts are publicly available at: https://github.com/NguyenPhuocAnhDung/oil_forecast_tail_risk.'
    ),
    
    # 5. Method: Problem formulation
    (
        'The future forecasted price level Pt+h,c = Pt,c · exp(rt+h,c)',
        'Forecasted spot price levels are subsequently recovered through the exact inverse exponential transformation in (2): Pt+h, c = Pt, c · exp(Rt→t+h, c). Formulating the forecasting objective in cumulative log-returns maps non-stationary price levels into stationary returns (p < 0.001; see Section IV-B) while avoiding the error accumulation inherent to iterative autoregressive rollouts.'
    ),
    
    # 6. Method: Wavelet-KAN
    (
        'To capture non-linear structural breaks associated with geopolitical risk events',
        'To model non-linear structural shifts and localized tail shocks triggered by geopolitical events, the third expert integrates a Kolmogorov–Arnold Network (KAN) with Mexican Hat wavelets ψ(z) = (1 - z2) · e-0.5z² parameterized by learnable translation and dilation coefficients according to (6) and (7):'
    ),
    
    # 7. Method: Residual scaling
    (
        'To limit variance growth at long horizons (such as H60)',
        'At extended forecast horizons (such as H60), unconstrained neural outputs risk compounding variance drift. GUMNetHet incorporates a learnable residual scaling parameter γh (initialized at 0.1) that bounds prediction magnitude toward recent price levels, generating multi-quantile return forecasts for q ∈ {0.1, 0.5, 0.9} according to (11):'
    ),
    
    # 8. Experimental Setup: Walk-forward
    (
        'To prevent look-ahead bias, daily variables are indexed at t - 1',
        'To prevent look-ahead bias, all predictor series are indexed at t - 1, monthly GPR is lagged by 30 calendar days, and weekly crude oil production is lagged by 7 days. Rolling statistical features are computed strictly post-lagging. Feature scalers are fit exclusively on expanding training partitions at each walk-forward step. The lookback length is fixed at L = 30 trading days, with an 85/15 train/validation split per expansion. The evaluation uses expanding walk-forward test windows scaled to the forecast lead time: 100 trading days for H1–H5 (11/12/2025–30/04/2026), 150 days for H7 (02/10/2025–30/04/2026), 200 days for H10 (24/07/2025–30/04/2026), 300 days for H20 (10/03/2025–30/04/2026), and 600 days for H60 (10/01/2024–30/04/2026). While the full dataset (2008–2026, N = 4,512) incorporates historical market cycles (e.g., the 2008 global financial crisis, the 2014–2016 oil collapse, the 2020 COVID-19/OPEC+ price war, and the 2022 Russia–Ukraine outbreak) across expanding training partitions, the out-of-sample test windows (2024–2026) deliberately evaluate model resilience under the recent era of clustered geopolitical shocks (namely, the Red Sea shipping disruptions, Middle East military tensions, Western energy sanctions enforcement, and OPEC+ quota adjustments). Specifically, annualized realized return volatility during the short-term test window (100 days) rose to 73.04% for MG95 (1.90× historical training volatility of 38.45%) and 96.29% for DO 0.001% (2.90× training volatility of 33.16%). The Geopolitical Risk (GPR) index averaged 225.66 during the test period (nearly doubling the historical mean of 114.60) and peaked at 500.81. Prices in the H60 test window spanned a wide peak-to-trough range: 70.34 to 170.52 USD/bbl (+142.4%) for MG95 and 75.90 to 292.82 USD/bbl (+285.8%) for DO 0.001% (Table I). This configuration provides a rigorous stress test, evaluating models under fat-tailed regime shifts rather than tranquil market conditions.'
    ),
    
    # 9. Results: Point forecasting
    (
        'Fig. 2 alongside Table III and Table IV show that GUMNetHet attains lower MAE',
        'Fig. 2 alongside Table III and Table IV show that GUMNetHet attains lower MAE than all reported baselines for both products across all horizons, with larger margins at H20–H60 where the test set undergoes substantial price swings of up to +142.4% (MG95) and +285.8% (DO). At H60, gasoline MAE is 4.847 compared to 6.933 for the strongest baseline (a 30.1% reduction); for diesel, MAE is 7.066 versus 9.167 (a 22.9% reduction). At H60, R2 values moderate to 0.155 (gasoline) and −0.007 (diesel); the long-horizon results should therefore be interpreted as effective price-level error containment under extreme volatility rather than precise long-range trajectory forecasting.'
    ),
    
    # 10. Results: Directional accuracy
    (
        'Directional accuracy in Fig. 3 shows a clear difference between short and long horizons',
        'Directional accuracy in Fig. 3 shows distinct behavior between short and long horizons. For gasoline (Table III), GUMNetHet attains high DA between 90.95% and 95.56% at H1–H7; for diesel (Table IV), DA spans 76.65% to 84.92%. At H20, DA remains informative (91.65% for gasoline; 71.11% for diesel). In contrast, at H10 and H60, DA drops below 50% (42.24%/27.95% for gasoline and 32.29%/19.10% for diesel). This behavior aligns with financial econometrics principles: over extended horizons (H60 spans nearly three months), oil prices approximate a near random walk with compounding uncertainty, weakening directional predictability. GUMNetHet\'s residual scaling mechanism shrinks predictions toward local price levels to minimize absolute error (reducing H60 MAE by 30.1%), trading directional commitment for robust error containment. The intermediate dip at H10 represents a transition between short-term momentum and regime dynamics that warrants further investigation. Overall, GUMNetHet operates effectively as a directional trading signal at short horizons (H1–H7) and as a robust price-level risk and uncertainty quantification tool at longer horizons (H10–H60).'
    ),
    
    # 11. Results: Probabilistic forecasting
    (
        'The [q0.1, q0.9] prediction interval achieves an empirical coverage probability',
        'The [q0.1, q0.9] prediction interval achieves an empirical coverage probability of PICP=82.4% (exceeding nominal 80%) with a normalized average width of PINAW=0.142. This confirms that the model avoids under-coverage while maintaining sharp, well-calibrated bounds, providing actionable interval forecasts for fuel distributors (e.g., Petrolimex, PVOIL) in forward pricing, inventory buffer sizing, and hedging optimization. Fig. 4 illustrates how prediction intervals expand adaptively during periods of elevated market turbulence. Ablation results in Table V indicate that replacing Wavelet-KAN with a standard MLP yields the largest performance drop, while a uniform routing baseline also inflates MAE, validating the necessity of heterogeneous inductive biases and adaptive gating.'
    ),
    
    # 12. Conclusion
    (
        'This paper proposed GUMNetHet, a heterogeneous mixture-of-experts architecture for multi-horizon probabilistic refined oil price forecasting',
        'This paper proposed GUMNetHet, a heterogeneous mixture-of-experts architecture for multi-horizon probabilistic forecasting of refined petroleum product prices subject to geopolitical shocks. The model synergizes multi-scale 1D-CNN, GRU-Attention, and Wavelet-KAN through a horizon-aware router, with multi-quantile outputs and residual scaling to improve stability over extended horizons. Expanding walk-forward experiments on MG95 gasoline and DO 0.001% diesel confirm that GUMNetHet achieves the lowest MAE among evaluated baselines across H1–H60, yielding H60 error reductions of 30.1% for MG95 (4.847 vs. 6.933) and 22.9% for DO 0.001% (7.066 vs. 9.167) relative to the strongest baselines. Ablation experiments and router weight analyses corroborate the contributions of feature partitioning, Wavelet-KAN, and adaptive routing. The moderation of R2 and directional accuracy at long horizons indicates that the model\'s advantage lies in price-level error control and uncertainty quantification rather than in long-range directional trajectory prediction.'
    )
]

matched_count = 0
for p in root.iter(f'{{{W_NS}}}p'):
    p_text = get_p_text(p)
    for trigger, new_text in updates:
        if trigger in p_text:
            set_p_text(p, new_text)
            matched_count += 1
            print(f"✓ Updated paragraph matching: '{trigger[:45]}...'")
            break

print(f"\nTotal paragraphs updated: {matched_count}/{len(updates)}")

# Serialize back to XML
entries['word/document.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

with zipfile.ZipFile(docx_out, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in entries.items():
        z.writestr(filename, data)

# Also update redline
with zipfile.ZipFile(docx_redline, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in entries.items():
        z.writestr(filename, data)

print(f"🎉 Successfully updated and saved both {docx_out} and {docx_redline}!")
