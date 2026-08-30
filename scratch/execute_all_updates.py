import zipfile
import xml.etree.ElementTree as ET
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'
compact_fig1_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\paper_figures\fig1_gumnethet_compact.png'

# 1. Read the docx zip
zip_entries = {}
with zipfile.ZipFile(docx_path, 'r') as z_in:
    for item in z_in.infolist():
        zip_entries[item.filename] = z_in.read(item.filename)

print(f"Total entries in original docx zip: {len(zip_entries)}")

# 2. Replace image1.png with compact_fig1_path
if os.path.exists(compact_fig1_path):
    with open(compact_fig1_path, 'rb') as img_f:
        zip_entries['word/media/image1.png'] = img_f.read()
    print(f"✓ Replaced word/media/image1.png with {compact_fig1_path} ({len(zip_entries['word/media/image1.png'])} bytes)")
else:
    print(f"Error: {compact_fig1_path} not found!")

# 3. Parse and update word/document.xml
doc_xml = zip_entries['word/document.xml'].decode('utf-8')

# Helper function to remove comment markup from an element or string if needed
# But let's do surgical replacements on document.xml

# Let's inspect specific fragments and replace them cleanly

# --- (A) Title ---
old_title = "Heterogeneous Mixture-of-Experts for Probabilistic Multi-Horizon Forecasting of Refined Petroleum Prices under Geopolitical Shocks"
new_title = "Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts"
if old_title in doc_xml:
    doc_xml = doc_xml.replace(old_title, new_title, 1)
    print("✓ Updated Title")
else:
    print("Warning: Old title string not found directly in doc_xml!")

# --- (B) Abstract (Comment 0) ---
# Let's check abstract text in doc_xml
# In original doc_xml, the abstract paragraph text is:
# "Abstract—This paper proposes GUMNetHet (Heterogeneous Gated Unified Mixture Network) for multi-horizon probabilistic forecasting of refined oil prices under geopolitical volatility. The framework partitions input features into three distinct subsets and processes them via specialized domain experts: multi-scale 1D-CNN for price momentum, GRU-Attention for macroeconomic regimes, and Wavelet-KAN for non-linear shock-sensitive dynamics. These representations are dynamically fused by a horizon-aware and market-context gating router; multi-quantile outputs q ∈ {0.1, 0.5, 0.9} are optimized using pinball loss combined with residual scaling. On Platts data spanning 11/2008–04/2026 (N = 4.512 observations) under an expanding walk-forward protocol during severe market turmoil (annualized test set volatility reaching 73.04–96.29%, 1.9–2.9× historical training levels), GUMNetHet achieves the lowest MAE across all reported baselines over all seven horizons H1–H60 for both MG95 gasoline and DO 0.001% diesel. At H60, MAE is reduced by 30.1% and 22.9% relative to the strongest baseline, respectively. Directional accuracy remains high at H1–H7 but declines noticeably at H10 and H60, highlighting the structural dichotomy between price-level precision and long-term directional forecasting. The 80% prediction interval attains PICP=82.4% with PINAW=0.142. Ablation studies and router analysis confirm that expert specialization and adaptive routing contribute substantially to model performance."

old_abstract_part = "On Platts data spanning 11/2008–04/2026 (N = 4.512 observations) under an expanding walk-forward protocol during severe market turmoil (annualized test set volatility reaching 73.04–96.29%, 1.9–2.9× historical training levels), GUMNetHet achieves the lowest MAE across all reported baselines over all seven horizons H1–H60 for both MG95 gasoline and DO 0.001% diesel. At H60, MAE is reduced by 30.1% and 22.9% relative to the strongest baseline, respectively. Directional accuracy remains high at H1–H7 but declines noticeably at H10 and H60, highlighting the structural dichotomy between price-level precision and long-term directional forecasting. The 80% prediction interval attains PICP=82.4% with PINAW=0.142. Ablation studies and router analysis confirm that expert specialization and adaptive routing contribute substantially to model performance."
new_abstract_part = "On Platts data spanning 11/2008–04/2026 (N = 4,512 observations) under an expanding walk-forward protocol during severe market turmoil (annualized test set volatility reaching 73.04% for MG95 and 96.29% for DO 0.001%, representing 1.90× and 2.90× historical training levels, respectively), GUMNetHet consistently achieves the lowest MAE across all reported baselines over all seven horizons H1–H60 for both MG95 gasoline and DO 0.001% diesel. At H60, MAE is reduced by 30.1% for MG95 (4.847 vs. 6.933) and 22.9% for DO 0.001% (7.066 vs. 9.167) relative to the strongest baseline. Directional accuracy remains high at short horizons (H1–H7: 90.95%–95.56% for MG95, 76.65%–84.92% for DO) but declines at H10 and H60, highlighting the structural dichotomy between price-level precision and long-term directional forecasting. The calibrated 80% prediction interval attains PICP=82.4% with sharpness PINAW=0.142. Ablation studies and router analysis confirm that expert specialization and adaptive routing contribute substantially to model robustness."

if old_abstract_part in doc_xml:
    doc_xml = doc_xml.replace(old_abstract_part, new_abstract_part, 1)
    print("✓ Updated Abstract text")
else:
    print("Searching for abstract pieces in XML...")

# --- (C) Contributions & GitHub link (Comment 1 + GitHub) ---
old_contrib = "The proposed GUMNetHet model resolves this bottleneck via feature partitioning: price and benchmark series are processed by multi-scale 1D-CNN; macroeconomic and GPR indices by GRU-Attention; and crack-spread ratios and realized volatility by Wavelet-KAN. These three representations are flexibly aggregated via a gating router conditioned on the forecasting horizon and market context. The principal contributions of this paper are fourfold: (i) A heterogeneous MoE architecture with feature partitioning grounded in economic principles and frequency domains; (ii) A horizon-aware routing mechanism (horizon-aware routing); (iii) A multi-quantile output head (multi-quantile head) combined with residual scaling to mitigate variance drift; and (iv) Extensive expanding walk-forward empirical evaluations on N = 4.512 trading days directly within high geopolitical volatility regimes (test set volatility 1.9–2.9× training levels) with comprehensive reporting across MAE, RMSE, MAPE, R2, and DA% metrics."

new_contrib = "The proposed GUMNetHet model resolves this bottleneck via feature partitioning: price and benchmark series are processed by multi-scale 1D-CNN; macroeconomic and GPR indices by GRU-Attention; and crack-spread ratios and realized volatility by Wavelet-KAN. These three representations are flexibly aggregated via a gating router conditioned on the forecasting horizon and market context. The principal contributions of this paper are fourfold: (i) A heterogeneous MoE architecture with feature partitioning grounded in economic principles and frequency domains, effectively preventing expert collapse (ablation reveals a 10.1%–17.7% MAE degradation when Wav-KAN is replaced by a standard MLP); (ii) A horizon-aware routing mechanism that dynamically modulates expert weights across forecast lead times and market regimes, with Wavelet-KAN allocation surging up to 0.61 during top-decile GPR shock regimes; (iii) A multi-quantile tail risk head (q ∈ {0.1, 0.5, 0.9}) combined with residual scaling to curtail long-horizon variance drift and deliver calibrated prediction intervals (PICP=82.4%, PINAW=0.142); and (iv) Extensive expanding walk-forward empirical evaluations on N = 4,512 trading days (2008–2026) directly within severe geopolitical turmoil (test set volatility 1.90×–2.90× historical training levels), demonstrating consistent MAE superiority across all horizons H1–H60 over six competitive state-of-the-art baselines with up to 30.1% (MG95) and 22.9% (DO 0.001%) error reductions at H60. All source code, trained checkpoints, and reproducibility scripts are openly available at: https://github.com/NguyenPhuocAnhDung/oil_forecast_tail_risk."

if old_contrib in doc_xml:
    doc_xml = doc_xml.replace(old_contrib, new_contrib, 1)
    print("✓ Updated Contributions paragraph with quantitative evidence & GitHub link")
else:
    print("Warning: old_contrib not matched exactly, checking substring...")

# --- (D) Fig. 1 Caption (Fig 1 update) ---
old_fig1_cap = "Fig. 1. Architectural overview of GUMNetHet: (A) Feature partitioning, three heterogeneous experts, horizon-aware router, and multi-quantile head; (B) Paradigms of competitive baselines."
new_fig1_cap = "Fig. 1. Neural network architecture of GUMNetHet: Feature partitioning into domain subsets, three specialized heterogeneous experts (Multi-Scale 1D-CNN, Stacked GRU-Attention, and Wavelet-KAN), horizon-aware dynamic gating router, and multi-quantile tail risk output head with residual scaling."

if old_fig1_cap in doc_xml:
    doc_xml = doc_xml.replace(old_fig1_cap, new_fig1_cap, 1)
    print("✓ Updated Fig. 1 Caption")
else:
    print("Warning: old_fig1_cap not matched exactly!")

# --- (E) Walk-forward Protocol (Comment 20) ---
old_wf = "All test windows fall entirely within a period of clustered extreme energy shocks (Red Sea crisis, Middle East escalations, Russia–Ukraine war, and OPEC+ quota shifts). Specifically, annualized realized return volatility during the short-term test window (100 days) surges to 73.04% for MG95 (1.90× historical training volatility of 38.45%) and 96.29% for DO 0.001% (2.90× training volatility of 33.16%)."

new_wf = "While the full dataset (2008–2026, N = 4,512) incorporates historical market cycles (e.g., the 2008 global financial crisis, the 2014–2016 oil collapse, the 2020 COVID-19/OPEC+ price war, and the 2022 Russia–Ukraine outbreak) across expanding training partitions, the out-of-sample test windows (2024–2026) specifically stress-test model resilience under the recent era of clustered acute geopolitical shocks (namely, the Red Sea maritime shipping crisis, direct Middle East/Iran–Israel military escalations, Western energy sanctions enforcement, and OPEC+ supply quota interventions). Specifically, annualized realized return volatility during the short-term test window (100 days) surges to 73.04% for MG95 (1.90× historical training volatility of 38.45%) and 96.29% for DO 0.001% (2.90× training volatility of 33.16%)."

if old_wf in doc_xml:
    doc_xml = doc_xml.replace(old_wf, new_wf, 1)
    print("✓ Updated Walk-Forward text to clarify historical training vs. recent acute shock testing")
else:
    print("Warning: old_wf not matched exactly!")

# --- (F) Conclusion & Data and Code Availability Section (Comment 29 + GitHub) ---
old_conclusion_text = "Expanding walk-forward experiments on MG95 and DO 0.001% demonstrate that GUMNetHet achieves the lowest MAE across all evaluated baselines throughout H1–H60, yielding MAE reductions at H60 of 30.1% for MG95 and 22.9% for DO 0.001%."
new_conclusion_text = "Expanding walk-forward experiments on MG95 and DO 0.001% demonstrate that GUMNetHet achieves the lowest MAE across all evaluated baselines throughout H1–H60, yielding MAE reductions at H60 of 30.1% for MG95 (4.847 vs. 6.933) and 22.9% for DO 0.001% (7.066 vs. 9.167) relative to the strongest baselines."

if old_conclusion_text in doc_xml:
    doc_xml = doc_xml.replace(old_conclusion_text, new_conclusion_text, 1)
    print("✓ Updated Conclusion text with explicit comparative metrics")

# Add Data and Code Availability Section before REFERENCES
# Let's find <w:p ...><w:r><w:t>REFERENCES</w:t></w:r></w:p>
# and insert a dedicated Data and Code Availability section right before it
dca_xml = """<w:p xmlns:w="http://purl.oclc.org/ooxml/wordprocessingml/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"><w:pPr><w:pStyle w:val="BodyText"/><w:spacing w:before="6pt" w:after="4pt" w:line="12.60pt" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr><w:t xml:space="preserve">Data and Code Availability: </w:t></w:r><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr><w:t>All source code for model architectures, training pipelines, expanding walk-forward evaluation scripts, and benchmark dataset matrices are publicly available for full peer reproducibility at the project repository: https://github.com/NguyenPhuocAnhDung/oil_forecast_tail_risk.</w:t></w:r></w:p>"""

if '<w:t>REFERENCES</w:t>' in doc_xml:
    # Find the paragraph containing REFERENCES
    ref_idx = doc_xml.find('<w:t>REFERENCES</w:t>')
    p_start = doc_xml.rfind('<w:p', 0, ref_idx)
    doc_xml = doc_xml[:p_start] + dca_xml + doc_xml[p_start:]
    print("✓ Inserted Data and Code Availability section before REFERENCES")
else:
    print("Warning: REFERENCES heading not found directly in doc_xml!")

zip_entries['word/document.xml'] = doc_xml.encode('utf-8')

# Write back directly to docx_path
with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
    for filename, data in zip_entries.items():
        z_out.writestr(filename, data)

print(f"✓ Successfully updated {docx_path} directly!")
