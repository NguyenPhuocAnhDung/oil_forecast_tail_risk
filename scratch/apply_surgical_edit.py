import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_orig = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.backup_orig.docx'
target_docx = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'
white_fig1 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\paper_figures\fig1_gumnethet_white_regular.png'

# Load original docx zip entries
zip_entries = {}
with zipfile.ZipFile(backup_orig, 'r') as z:
    for item in z.infolist():
        zip_entries[item.filename] = z.read(item.filename)

print("Loaded zip entries:", len(zip_entries))

# 1. Update Figure 1
with open(white_fig1, 'rb') as f:
    zip_entries['word/media/image1.png'] = f.read()
print("✓ 1. Replaced word/media/image1.png")

doc_xml = zip_entries['word/document.xml'].decode('utf-8')

# 2. Title
t_old = '<w:t>Heterogeneous Mixture-of-Experts for Probabilistic Multi-Horizon Forecasting of Refined Petroleum Prices under Geopolitical Shocks</w:t>'
t_new = '<w:t>Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts</w:t>'
assert t_old in doc_xml, "Title match failed!"
doc_xml = doc_xml.replace(t_old, t_new, 1)
print("✓ 2. Title updated")

# 3. Figure 1 Caption
fig_cap_old = '<w:r><w:rPr><w:sz w:val="17"/></w:rPr><w:t xml:space="preserve"> Architectural overview of GUMNetHet: (A) Feature partitioning, three heterogeneous experts, horizon-aware router, and multi-quantile head; (B) Paradigms of competitive baselines.</w:t></w:r>'
fig_cap_new = '<w:r><w:rPr><w:sz w:val="17"/></w:rPr><w:t xml:space="preserve"> Neural network architecture of GUMNetHet: Feature partitioning into domain subsets, three specialized heterogeneous experts (Multi-Scale 1D-CNN, Stacked GRU-Attention, and Wavelet-KAN), horizon-aware dynamic gating router, and multi-quantile tail risk output head with residual scaling.</w:t></w:r>'
assert fig_cap_old in doc_xml, "Fig 1 caption match failed!"
doc_xml = doc_xml.replace(fig_cap_old, fig_cap_new, 1)
print("✓ 3. Fig 1 caption updated")

# 4. Abstract Paragraph
abs_idx = doc_xml.find('Abstract—')
abs_p_start = doc_xml.rfind('<w:p ', 0, abs_idx)
abs_p_end = doc_xml.find('</w:p>', abs_idx) + 6

abs_new_p = (
    '<w:p w14:paraId="666CFC29" w14:textId="791170BF" w:rsidR="00B952C0" w:rsidRDefault="00000000">'
    '<w:pPr><w:pStyle w:val="Abstract"/><w:spacing w:before="4pt" w:after="4pt" w:line="12.60pt" w:lineRule="auto"/></w:pPr>'
    '<w:r><w:rPr><w:i/></w:rPr><w:t>Abstract—</w:t></w:r>'
    '<w:r><w:t xml:space="preserve">This paper proposes GUMNetHet (Heterogeneous Gated Unified Mixture Network) for multi-horizon probabilistic forecasting of refined petroleum prices under geopolitical volatility. The framework partitions input features into three distinct subsets and processes them via specialized domain experts: multi-scale 1D-CNN for price momentum, GRU-Attention for macroeconomic regimes, and Wavelet-KAN for non-linear shock-sensitive dynamics. These representations are dynamically fused by a horizon-aware and market-context gating router; multi-quantile outputs </w:t></w:r>'
    '<m:oMath><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>q ∈ {0.1, 0.5, 0.9}</m:t></m:r></m:oMath>'
    '<w:r><w:t xml:space="preserve"> are optimized using pinball loss combined with residual scaling. On Platts data spanning 11/2008–04/2026 (</w:t></w:r>'
    '<m:oMath><m:r><m:rPr><m:sty m:val="bi"/></m:rPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>N = 4,512</m:t></m:r></m:oMath>'
    '<w:r><w:t xml:space="preserve"> observations) under an expanding walk-forward protocol during severe market turmoil (annualized test set volatility reaching 73.04% for MG95 and 96.29% for DO 0.001%, representing 1.90× and 2.90× historical training levels, respectively), GUMNetHet consistently achieves the lowest MAE across all reported baselines over all seven horizons H1–H60 for both MG95 gasoline and DO 0.001% diesel. At H60, MAE is reduced by 30.1% for MG95 (4.847 vs. 6.933) and 22.9% for DO 0.001% (7.066 vs. 9.167) relative to the strongest baseline. Directional accuracy remains high at short horizons (H1–H7: 90.95%–95.56% for MG95, 76.65%–84.92% for DO) but declines at H10 and H60, highlighting the structural dichotomy between price-level precision and long-term directional forecasting. The calibrated 80% prediction interval attains PICP=82.4% with sharpness PINAW=0.142. Ablation studies and router analysis confirm that expert specialization and adaptive routing contribute substantially to model robustness.</w:t></w:r>'
    '</w:p>'
)
doc_xml = doc_xml[:abs_p_start] + abs_new_p + doc_xml[abs_p_end:]
print("✓ 4. Abstract updated (Comment 0 resolved)")

# 5. Contributions Paragraph & GitHub Link
c_idx = doc_xml.find('The proposed GUMNetHet model resolves this bottleneck')
c_p_start = doc_xml.rfind('<w:p ', 0, c_idx)
c_p_end = doc_xml.find('</w:p>', c_idx) + 6

c_new_p = (
    '<w:p w14:paraId="0B342362" w14:textId="77777777" w:rsidR="00B952C0" w:rsidRDefault="00000000">'
    '<w:pPr><w:pStyle w:val="BodyText"/><w:spacing w:after="3pt" w:line="12.60pt" w:lineRule="auto"/></w:pPr>'
    '<w:r><w:t xml:space="preserve">The proposed GUMNetHet model resolves this bottleneck via feature partitioning: price and benchmark series are processed by multi-scale 1D-CNN; macroeconomic and GPR indices by GRU-Attention; and crack-spread ratios and realized volatility by Wavelet-KAN. These three representations are flexibly aggregated via a gating router conditioned on the forecasting horizon and market context. The principal contributions of this paper are fourfold: (i) A heterogeneous MoE architecture with feature partitioning grounded in economic principles and frequency domains, effectively preventing expert collapse (ablation reveals a 10.1%–17.7% MAE degradation when Wav-KAN is replaced by a standard MLP); (ii) A horizon-aware routing mechanism that dynamically modulates expert weights across forecast lead times and market regimes, with Wavelet-KAN allocation surging up to 0.61 during top-decile GPR shock regimes; (iii) A multi-quantile tail risk head (q ∈ {0.1, 0.5, 0.9}) combined with residual scaling to curtail long-horizon variance drift and deliver calibrated prediction intervals (PICP=82.4%, PINAW=0.142); and (iv) Extensive expanding walk-forward empirical evaluations on </w:t></w:r>'
    '<m:oMath><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>N = 4,512</m:t></m:r></m:oMath>'
    '<w:r><w:t xml:space="preserve"> trading days (2008–2026) directly within severe geopolitical turmoil (test set volatility 1.90×–2.90× historical training levels), demonstrating consistent MAE superiority across all horizons H1–H60 over six competitive state-of-the-art baselines with up to 30.1% (MG95) and 22.9% (DO 0.001%) error reductions at H60. All source code, trained checkpoints, and reproducibility scripts are openly available at: https://github.com/NguyenPhuocAnhDung/oil_forecast_tail_risk.</w:t></w:r>'
    '</w:p>'
)
doc_xml = doc_xml[:c_p_start] + c_new_p + doc_xml[c_p_end:]
print("✓ 5. Contributions updated with GitHub repo link (Comment 1 resolved)")

# 6. Equation (2) Hat Notation (Comment 4)
eq2_old = '<m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>P̂</m:t></m:r></m:e>'
eq2_new = '<m:e><m:acc><m:accPr><m:chr m:val="^"/></m:accPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>P</m:t></m:r></m:e></m:acc></m:e>'
doc_xml = doc_xml.replace(eq2_old, eq2_new)

eq2_rhat_old = '<m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>R̂</m:t></m:r></m:e>'
eq2_rhat_new = '<m:e><m:acc><m:accPr><m:chr m:val="^"/></m:accPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>R</m:t></m:r></m:e></m:acc></m:e>'
doc_xml = doc_xml.replace(eq2_rhat_old, eq2_rhat_new)

eq2_r_small_old = '<m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>r̂</m:t></m:r></m:e>'
eq2_r_small_new = '<m:e><m:acc><m:accPr><m:chr m:val="^"/></m:accPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>r</m:t></m:r></m:e></m:acc></m:e>'
doc_xml = doc_xml.replace(eq2_r_small_old, eq2_r_small_new)
print("✓ 6. Eq 2 Hat notations enhanced with clean OMML acc (Comment 4 resolved)")

# 7. Equation (4) Completion with \in R^d (Comment 8)
# Look at the exact string for Eq (4)
pos_eq4 = doc_xml.find('name="eq_4"')
tbl_start_4 = doc_xml.rfind('<w:tbl', 0, pos_eq4)
tbl_end_4 = doc_xml.find('</w:tbl>', pos_eq4) + 8
eq4_tbl_str = doc_xml[tbl_start_4:tbl_end_4]

# Replace )))) with )))) \in R^d inside this table
old_math_4 = '<m:t>))))</m:t></m:r></m:oMath>'
new_math_4 = '<m:t xml:space="preserve">)))) ∈ </m:t></m:r><m:sSup><m:sSupPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSupPr><m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>d</m:t></m:r></m:sup></m:sSup></m:oMath>'
assert old_math_4 in eq4_tbl_str, "Eq 4 old math not found!"
eq4_tbl_str_new = eq4_tbl_str.replace(old_math_4, new_math_4, 1)
doc_xml = doc_xml[:tbl_start_4] + eq4_tbl_str_new + doc_xml[tbl_end_4:]
print("✓ 7. Eq 4 completed with ∈ R^d (Comment 8 resolved)")

# 8. Equation (7) Parenthesis fix & \in R^d (Comment 12)
pos_eq7 = doc_xml.find('name="eq_7"')
tbl_start_7 = doc_xml.rfind('<w:tbl', 0, pos_eq7)
tbl_end_7 = doc_xml.find('</w:tbl>', pos_eq7) + 8
eq7_tbl_str = doc_xml[tbl_start_7:tbl_end_7]

old_math_7 = '<m:t>ψ(z))))))</m:t></m:r></m:oMath>'
new_math_7 = '<m:t xml:space="preserve">ψ(z)))) ∈ </m:t></m:r><m:sSup><m:sSupPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSupPr><m:e><m:r><m:rPr><m:scr m:val="double-struck"/></m:rPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>d</m:t></m:r></m:sup></m:sSup></m:oMath>'
assert old_math_7 in eq7_tbl_str, "Eq 7 old math not found!"
eq7_tbl_str_new = eq7_tbl_str.replace(old_math_7, new_math_7, 1)
doc_xml = doc_xml[:tbl_start_7] + eq7_tbl_str_new + doc_xml[tbl_end_7:]
print("✓ 8. Eq 7 fixed and completed with ∈ R^d (Comment 12 resolved)")

# 9. Walk-Forward Protocol (Comment 20)
wf_idx = doc_xml.find('To prevent look-ahead bias')
wf_p_start = doc_xml.rfind('<w:p ', 0, wf_idx)
wf_p_end = doc_xml.find('</w:p>', wf_idx) + 6

wf_new_p = (
    '<w:p w14:paraId="252B9A9A" w14:textId="77777777" w:rsidR="00B952C0" w:rsidRDefault="00000000">'
    '<w:pPr><w:pStyle w:val="BodyText"/><w:spacing w:after="3pt" w:line="12.60pt" w:lineRule="auto"/></w:pPr>'
    '<w:r><w:t xml:space="preserve">To prevent look-ahead bias, daily variables are indexed at </w:t></w:r>'
    '<m:oMath><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>t - 1</m:t></m:r></m:oMath>'
    '<w:r><w:t xml:space="preserve">; GPR is lagged by 30 calendar days; crude oil production is lagged by 7 days; and rolling features are computed strictly after applying lags. All scalers are fit exclusively on the training partition at each walk-forward step. Lookback length is </w:t></w:r>'
    '<m:oMath><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>L = 30</m:t></m:r></m:oMath>'
    '<w:r><w:t>; train/validation ratio is 85/15 per expansion. Expanding walk-forward test windows increase progressively with horizon: 100 trading days for H1–H5 (11/12/2025–30/04/2026), 150 days for H7 (02/10/2025–30/04/2026), 200 days for H10 (24/07/2025–30/04/2026), 300 days for H20 (10/03/2025–30/04/2026), and 600 days for H60 (10/01/2024–30/04/2026). While the full dataset (2008–2026, N = 4,512) incorporates historical market cycles (e.g., the 2008 global financial crisis, the 2014–2016 oil collapse, the 2020 COVID-19/OPEC+ price war, and the 2022 Russia–Ukraine outbreak) across expanding training partitions, the out-of-sample test windows (2024–2026) specifically stress-test model resilience under the recent era of clustered acute geopolitical shocks (namely, the Red Sea maritime shipping crisis, direct Middle East/Iran–Israel military escalations, Western energy sanctions enforcement, and OPEC+ supply quota interventions). Specifically, annualized realized return volatility during the short-term test window (100 days) surges to 73.04% for MG95 (1.90× historical training volatility of 38.45%) and 96.29% for DO 0.001% (2.90× training volatility of 33.16%). The Geopolitical Risk (GPR) index averages 225.66 during the test period (nearly doubling the historical mean of 114.60) and peaks at 500.81 (90th percentile at 376.48). Price swings in the H60 test window record extreme peak-to-trough variations: 70.34 to 170.52 USD/bbl (+142.4%) for MG95 and 75.90 to 292.82 USD/bbl (+285.8%) for DO 0.001%. Comprehensive train/test splits and volatility characteristics across horizons are summarized in </w:t></w:r>'
    '<w:hyperlink w:anchor="tbl_1" w:history="1"><w:r><w:rPr><w:color w:val="1A56DB"/></w:rPr><w:t>Table 1</w:t></w:r></w:hyperlink>'
    '<w:r><w:t>. This configuration serves as a rigorous stress-testing benchmark, ensuring models are evaluated on their capacity to adapt under fat-tailed regime shifts rather than static market conditions.</w:t></w:r>'
    '</w:p>'
)
doc_xml = doc_xml[:wf_p_start] + wf_new_p + doc_xml[wf_p_end:]
print("✓ 9. Walk-forward text updated (Comment 20 resolved)")

# 10. Conclusion Paragraph (Comment 29)
concl_idx = doc_xml.find('Expanding walk-forward experiments on MG95')
concl_p_start = doc_xml.rfind('<w:p ', 0, concl_idx)
concl_p_end = doc_xml.find('</w:p>', concl_idx) + 6

concl_new_p = (
    '<w:p w14:paraId="05D5DB02" w14:textId="77777777" w:rsidR="00B952C0" w:rsidRDefault="00000000">'
    '<w:pPr><w:pStyle w:val="BodyText"/><w:spacing w:after="3pt" w:line="12.60pt" w:lineRule="auto"/></w:pPr>'
    '<w:r><w:t xml:space="preserve">Expanding walk-forward experiments on MG95 and DO 0.001% demonstrate that GUMNetHet achieves the lowest MAE across all evaluated baselines throughout H1–H60, yielding MAE reductions at H60 of 30.1% for MG95 (4.847 vs. 6.933) and 22.9% for DO 0.001% (7.066 vs. 9.167) relative to the strongest baselines. Ablation experiments and router weight analyses corroborate the contributions of feature partitioning, Wavelet-KAN, and adaptive routing. However, the attenuation of </w:t></w:r>'
    '<m:oMath><m:sSup><m:sSupPr><m:ctrlPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr></m:ctrlPr></m:sSupPr><m:e><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>R</m:t></m:r></m:e><m:sup><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>2</m:t></m:r></m:sup></m:sSup></m:oMath>'
    '<w:r><w:t xml:space="preserve"> and directional accuracy at long horizons underscores that model superiority lies in price-level error containment and uncertainty quantification, rather than long-range directional forecasting.</w:t></w:r>'
    '</w:p>'
)
doc_xml = doc_xml[:concl_p_start] + concl_new_p + doc_xml[concl_p_end:]
print("✓ 10. Conclusion updated (Comment 29 resolved)")

# 11. Dedicated Data and Code Availability Section before REFERENCES
ref_old = '<w:p w14:paraId="388559A7" w14:textId="77777777" w:rsidR="00B952C0" w:rsidRDefault="00000000"><w:pPr><w:pStyle w:val="Heading5"/><w:keepNext/><w:spacing w:line="12.60pt" w:lineRule="auto"/></w:pPr><w:r><w:rPr><w:b/></w:rPr><w:t>REFERENCES</w:t></w:r></w:p>'
dca_p = (
    '<w:p w14:paraId="3DCA0001" w14:textId="77777777" w:rsidR="00B952C0" w:rsidRDefault="00000000">'
    '<w:pPr><w:pStyle w:val="BodyText"/><w:spacing w:before="6pt" w:after="4pt" w:line="12.60pt" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>'
    '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr><w:t xml:space="preserve">Data and Code Availability: </w:t></w:r>'
    '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr><w:t>All source code for model architectures, training pipelines, expanding walk-forward evaluation scripts, and benchmark dataset matrices are publicly available for full peer reproducibility at the project repository: https://github.com/NguyenPhuocAnhDung/oil_forecast_tail_risk.</w:t></w:r>'
    '</w:p>'
)
ref_new = dca_p + ref_old
assert ref_old in doc_xml, "REFERENCES match failed!"
doc_xml = doc_xml.replace(ref_old, ref_new, 1)
print("✓ 11. Dedicated Data and Code Availability section inserted before REFERENCES")

# Write back into zip
zip_entries['word/document.xml'] = doc_xml.encode('utf-8')

with zipfile.ZipFile(target_docx, 'w', zipfile.ZIP_DEFLATED) as z_out:
    for filename, data in zip_entries.items():
        z_out.writestr(filename, data)

print(f"\n🎉 Successfully performed surgical, in-place edit directly on {target_docx}!")
