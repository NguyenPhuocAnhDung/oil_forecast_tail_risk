import zipfile
import xml.etree.ElementTree as ET
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'
backup_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.backup_orig.docx'
compact_fig1_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\paper_figures\fig1_gumnethet_compact.png'

# Make backup if not existing
if not os.path.exists(backup_path):
    shutil.copyfile(docx_path, backup_path)
    print(f"Created original backup at {backup_path}")

# Load all zip entries from docx
zip_entries = {}
with zipfile.ZipFile(docx_path, 'r') as z:
    for item in z.infolist():
        zip_entries[item.filename] = z.read(item.filename)

print("Loaded docx zip entries, count:", len(zip_entries))

# 1. Replace Figure 1 in word/media/image1.png
if os.path.exists(compact_fig1_path):
    with open(compact_fig1_path, 'rb') as f:
        zip_entries['word/media/image1.png'] = f.read()
    print("✓ Replaced word/media/image1.png with compact Fig 1 (without Part B)")

# 2. Parse word/document.xml with ElementTree
doc_xml = zip_entries['word/document.xml']
root = ET.fromstring(doc_xml)

# Define standard namespaces mapping
NS_W = 'http://purl.oclc.org/ooxml/wordprocessingml/main'
NS_M = 'http://purl.oclc.org/ooxml/officeDocument/math'
NS_W14 = 'http://schemas.microsoft.com/office/word/2010/wordml'

ET.register_namespace('w', NS_W)
ET.register_namespace('m', NS_M)
ET.register_namespace('w14', NS_W14)

def get_node_text(elem):
    texts = []
    for t in elem.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            texts.append(t.text)
    return ''.join(texts)

# --- (A) Update Title ---
for p in root.iter(f'{{{NS_W}}}p'):
    txt = get_node_text(p)
    if 'Heterogeneous Mixture-of-Experts for Probabilistic' in txt:
        for t in p.iter(f'{{{NS_W}}}t'):
            if 'Heterogeneous Mixture-of-Experts' in (t.text or ''):
                t.text = "Robust Probabilistic Energy Forecasting under Geopolitical Shocks: An Adaptive Mixture of Local-Global Experts"
                print("✓ Title updated to official manuscript title")
                break

# --- (B) Update Abstract (Comment 0) ---
for p in root.iter(f'{{{NS_W}}}p'):
    txt = get_node_text(p)
    if txt.startswith('Abstract—'):
        # Let's rebuild the abstract paragraph cleanly
        # Keep pPr
        pPr = p.find(f'{{{NS_W}}}pPr')
        p.clear()
        if pPr is not None:
            p.append(pPr)
        
        # Abstract prefix
        r_prefix = ET.SubElement(p, f'{{{NS_W}}}r')
        rPr = ET.SubElement(r_prefix, f'{{{NS_W}}}rPr')
        ET.SubElement(rPr, f'{{{NS_W}}}b')
        ET.SubElement(rPr, f'{{{NS_W}}}i')
        ET.SubElement(rPr, f'{{{NS_W}}}rFonts', {f'{{{NS_W}}}ascii': 'Times New Roman', f'{{{NS_W}}}hAnsi': 'Times New Roman'})
        ET.SubElement(rPr, f'{{{NS_W}}}sz', {f'{{{NS_W}}}val': '18'})
        t_prefix = ET.SubElement(r_prefix, f'{{{NS_W}}}t')
        t_prefix.text = "Abstract—"
        
        # Abstract body text
        r_body = ET.SubElement(p, f'{{{NS_W}}}r')
        rPr_b = ET.SubElement(r_body, f'{{{NS_W}}}rPr')
        ET.SubElement(rPr_b, f'{{{NS_W}}}rFonts', {f'{{{NS_W}}}ascii': 'Times New Roman', f'{{{NS_W}}}hAnsi': 'Times New Roman'})
        ET.SubElement(rPr_b, f'{{{NS_W}}}sz', {f'{{{NS_W}}}val': '18'})
        t_body = ET.SubElement(r_body, f'{{{NS_W}}}t')
        t_body.text = (
            "This paper proposes GUMNetHet (Heterogeneous Gated Unified Mixture Network) for multi-horizon probabilistic forecasting "
            "of refined petroleum prices under geopolitical volatility. The framework partitions input features into three distinct "
            "subsets and processes them via specialized domain experts: multi-scale 1D-CNN for price momentum, GRU-Attention for "
            "macroeconomic regimes, and Wavelet-KAN for non-linear shock-sensitive dynamics. These representations are dynamically "
            "fused by a horizon-aware and market-context gating router; multi-quantile outputs q ∈ {0.1, 0.5, 0.9} are optimized "
            "using pinball loss combined with residual scaling. On Platts data spanning 11/2008–04/2026 (N = 4,512 observations) "
            "under an expanding walk-forward protocol during severe market turmoil (annualized test set volatility reaching 73.04% for "
            "MG95 and 96.29% for DO 0.001%, representing 1.90× and 2.90× historical training levels, respectively), GUMNetHet "
            "consistently achieves the lowest MAE across all reported baselines over all seven horizons H1–H60 for both MG95 gasoline "
            "and DO 0.001% diesel. At H60, MAE is reduced by 30.1% for MG95 (4.847 vs. 6.933) and 22.9% for DO 0.001% (7.066 vs. 9.167) "
            "relative to the strongest baseline. Directional accuracy remains high at short horizons (H1–H7: 90.95%–95.56% for MG95, "
            "76.65%–84.92% for DO) but declines at H10 and H60, highlighting the structural dichotomy between price-level precision "
            "and long-term directional forecasting. The calibrated 80% prediction interval attains PICP=82.4% with sharpness PINAW=0.142. "
            "Ablation studies and router analysis confirm that expert specialization and adaptive routing contribute substantially "
            "to model robustness."
        )
        print("✓ Abstract paragraph rebuilt cleanly (Comment 0 resolved)")
        break

# --- (C) Update Introduction Contributions & GitHub Link (Comment 1 + GitHub) ---
for p in root.iter(f'{{{NS_W}}}p'):
    txt = get_node_text(p)
    if 'The proposed GUMNetHet model resolves this bottleneck' in txt:
        pPr = p.find(f'{{{NS_W}}}pPr')
        p.clear()
        if pPr is not None:
            p.append(pPr)
            
        r_contrib = ET.SubElement(p, f'{{{NS_W}}}r')
        rPr_c = ET.SubElement(r_contrib, f'{{{NS_W}}}rPr')
        ET.SubElement(rPr_c, f'{{{NS_W}}}rFonts', {f'{{{NS_W}}}ascii': 'Times New Roman', f'{{{NS_W}}}hAnsi': 'Times New Roman'})
        ET.SubElement(rPr_c, f'{{{NS_W}}}sz', {f'{{{NS_W}}}val': '20'})
        t_contrib = ET.SubElement(r_contrib, f'{{{NS_W}}}t')
        t_contrib.text = (
            "The proposed GUMNetHet model resolves this bottleneck via feature partitioning: price and benchmark series are processed "
            "by multi-scale 1D-CNN; macroeconomic and GPR indices by GRU-Attention; and crack-spread ratios and realized volatility "
            "by Wavelet-KAN. These three representations are flexibly aggregated via a gating router conditioned on the forecasting "
            "horizon and market context. The principal contributions of this paper are fourfold: (i) A heterogeneous MoE architecture "
            "with feature partitioning grounded in economic principles and frequency domains, effectively preventing expert collapse "
            "(ablation reveals a 10.1%–17.7% MAE degradation when Wav-KAN is replaced by a standard MLP); (ii) A horizon-aware routing "
            "mechanism that dynamically modulates expert weights across forecast lead times and market regimes, with Wavelet-KAN allocation "
            "surging up to 0.61 during top-decile GPR shock regimes; (iii) A multi-quantile tail risk head (q ∈ {0.1, 0.5, 0.9}) combined "
            "with residual scaling to curtail long-horizon variance drift and deliver calibrated prediction intervals (PICP=82.4%, PINAW=0.142); "
            "and (iv) Extensive expanding walk-forward empirical evaluations on N = 4,512 trading days (2008–2026) directly within severe "
            "geopolitical turmoil (test set volatility 1.90×–2.90× historical training levels), demonstrating consistent MAE superiority across "
            "all horizons H1–H60 over six competitive state-of-the-art baselines with up to 30.1% (MG95) and 22.9% (DO 0.001%) error reductions "
            "at H60. All source code, trained checkpoints, and reproducibility scripts are openly available at: "
            "https://github.com/NguyenPhuocAnhDung/oil_forecast_tail_risk."
        )
        print("✓ Contributions paragraph updated with quantitative evidence & GitHub repo link (Comment 1 resolved)")
        break

# --- (D) Update Equation (2) Hat Notation (Comment 4) ---
for tbl in root.iter(f'{{{NS_W}}}tbl'):
    txt = get_node_text(tbl)
    if '(2)' in txt and 'exp' in txt:
        # Find cell 0 paragraph
        for p in tbl.iter(f'{{{NS_W}}}p'):
            omath = p.find(f'.//{{{NS_M}}}oMath')
            if omath is not None:
                # Rebuild omath for Equation 2
                omath.clear()
                
                # P_hat_{t+h, c}
                sSub1 = ET.SubElement(omath, f'{{{NS_M}}}sSub')
                e1 = ET.SubElement(sSub1, f'{{{NS_M}}}e')
                acc1 = ET.SubElement(e1, f'{{{NS_M}}}acc')
                accPr1 = ET.SubElement(acc1, f'{{{NS_M}}}accPr')
                ET.SubElement(accPr1, f'{{{NS_M}}}chr', {f'{{{NS_M}}}val': '^'})
                e_acc1 = ET.SubElement(acc1, f'{{{NS_M}}}e')
                r1 = ET.SubElement(e_acc1, f'{{{NS_M}}}r')
                t1 = ET.SubElement(r1, f'{{{NS_M}}}t')
                t1.text = 'P'
                sub1 = ET.SubElement(sSub1, f'{{{NS_M}}}sub')
                r_sub1 = ET.SubElement(sub1, f'{{{NS_M}}}r')
                t_sub1 = ET.SubElement(r_sub1, f'{{{NS_M}}}t')
                t_sub1.text = 't+h, c'
                
                # = P_{t, c} · exp(
                r_eq = ET.SubElement(omath, f'{{{NS_M}}}r')
                t_eq = ET.SubElement(r_eq, f'{{{NS_M}}}t')
                t_eq.text = ' = '
                
                sSub2 = ET.SubElement(omath, f'{{{NS_M}}}sSub')
                e2 = ET.SubElement(sSub2, f'{{{NS_M}}}e')
                r2 = ET.SubElement(e2, f'{{{NS_M}}}r')
                t2 = ET.SubElement(r2, f'{{{NS_M}}}t')
                t2.text = 'P'
                sub2 = ET.SubElement(sSub2, f'{{{NS_M}}}sub')
                r_sub2 = ET.SubElement(sub2, f'{{{NS_M}}}r')
                t_sub2 = ET.SubElement(r_sub2, f'{{{NS_M}}}t')
                t_sub2.text = 't, c'
                
                r_exp = ET.SubElement(omath, f'{{{NS_M}}}r')
                t_exp = ET.SubElement(r_exp, f'{{{NS_M}}}t')
                t_exp.text = ' · exp('
                
                # R_hat_{t->t+h, c}
                sSub3 = ET.SubElement(omath, f'{{{NS_M}}}sSub')
                e3 = ET.SubElement(sSub3, f'{{{NS_M}}}e')
                acc3 = ET.SubElement(e3, f'{{{NS_M}}}acc')
                accPr3 = ET.SubElement(acc3, f'{{{NS_M}}}accPr')
                ET.SubElement(accPr3, f'{{{NS_M}}}chr', {f'{{{NS_M}}}val': '^'})
                e_acc3 = ET.SubElement(acc3, f'{{{NS_M}}}e')
                r3 = ET.SubElement(e_acc3, f'{{{NS_M}}}r')
                t3 = ET.SubElement(r3, f'{{{NS_M}}}t')
                t3.text = 'R'
                sub3 = ET.SubElement(sSub3, f'{{{NS_M}}}sub')
                r_sub3 = ET.SubElement(sub3, f'{{{NS_M}}}r')
                t_sub3 = ET.SubElement(r_sub3, f'{{{NS_M}}}t')
                t_sub3.text = 't→t+h, c'
                
                # )
                r_close = ET.SubElement(omath, f'{{{NS_M}}}r')
                t_close = ET.SubElement(r_close, f'{{{NS_M}}}t')
                t_close.text = ')'
                
                print("✓ Equation (2) formula rebuilt with clear native OMML hat accents (Comment 4 resolved)")
                break

# --- (E) Update Figure 1 Caption ---
for p in root.iter(f'{{{NS_W}}}p'):
    txt = get_node_text(p)
    if 'Fig. 1. Architectural overview of GUMNetHet' in txt or 'Fig. 1.' in txt and 'Paradigms of competitive' in txt:
        pPr = p.find(f'{{{NS_W}}}pPr')
        p.clear()
        if pPr is not None:
            p.append(pPr)
            
        r_cap = ET.SubElement(p, f'{{{NS_W}}}r')
        rPr_cap = ET.SubElement(r_cap, f'{{{NS_W}}}rPr')
        ET.SubElement(rPr_cap, f'{{{NS_W}}}rFonts', {f'{{{NS_W}}}ascii': 'Times New Roman', f'{{{NS_W}}}hAnsi': 'Times New Roman'})
        ET.SubElement(rPr_cap, f'{{{NS_W}}}sz', {f'{{{NS_W}}}val': '16'})
        t_cap = ET.SubElement(r_cap, f'{{{NS_W}}}t')
        t_cap.text = "Fig. 1. Neural network architecture of GUMNetHet: Feature partitioning into domain subsets, three specialized heterogeneous experts (Multi-Scale 1D-CNN, Stacked GRU-Attention, and Wavelet-KAN), horizon-aware dynamic gating router, and multi-quantile tail risk output head with residual scaling."
        print("✓ Figure 1 caption updated (Part B removed)")
        break

# --- (F) Update Equation (4) (Comment 8) ---
for tbl in root.iter(f'{{{NS_W}}}tbl'):
    txt = get_node_text(tbl)
    if '(4)' in txt:
        # Find the row for (4)
        for tr in tbl.iter(f'{{{NS_W}}}tr'):
            tr_txt = get_node_text(tr)
            if '(4)' in tr_txt:
                omath = tr.find(f'.//{{{NS_M}}}oMath')
                if omath is not None:
                    # Append ∈ R^d
                    r_in = ET.SubElement(omath, f'{{{NS_M}}}r')
                    t_in = ET.SubElement(r_in, f'{{{NS_M}}}t')
                    t_in.text = ' ∈ '
                    
                    sSup = ET.SubElement(omath, f'{{{NS_M}}}sSup')
                    e = ET.SubElement(sSup, f'{{{NS_M}}}e')
                    r_R = ET.SubElement(e, f'{{{NS_M}}}r')
                    rPr_R = ET.SubElement(r_R, f'{{{NS_M}}}rPr')
                    ET.SubElement(rPr_R, f'{{{NS_M}}}scr', {f'{{{NS_M}}}val': 'double-struck'})
                    t_R = ET.SubElement(r_R, f'{{{NS_M}}}t')
                    t_R.text = 'R'
                    
                    sup = ET.SubElement(sSup, f'{{{NS_M}}}sup')
                    r_d = ET.SubElement(sup, f'{{{NS_M}}}r')
                    t_d = ET.SubElement(r_d, f'{{{NS_M}}}t')
                    t_d.text = 'd'
                    print("✓ Equation (4) completed with ∈ R^d (Comment 8 resolved)")
                break

# --- (G) Update Equation (7) (Comment 12) ---
for tbl in root.iter(f'{{{NS_W}}}tbl'):
    txt = get_node_text(tbl)
    if '(7)' in txt:
        for tr in tbl.iter(f'{{{NS_W}}}tr'):
            tr_txt = get_node_text(tr)
            if '(7)' in tr_txt:
                omath = tr.find(f'.//{{{NS_M}}}oMath')
                if omath is not None:
                    # Fix text inside last run to remove extra parenthesis and append ∈ R^d
                    for r in omath.findall(f'.//{{{NS_M}}}r'):
                        for t in r.findall(f'.//{{{NS_M}}}t'):
                            if t.text and 'ψ(z)' in t.text:
                                t.text = 'ψ(z))))'
                                
                    r_in = ET.SubElement(omath, f'{{{NS_M}}}r')
                    t_in = ET.SubElement(r_in, f'{{{NS_M}}}t')
                    t_in.text = ' ∈ '
                    
                    sSup = ET.SubElement(omath, f'{{{NS_M}}}sSup')
                    e = ET.SubElement(sSup, f'{{{NS_M}}}e')
                    r_R = ET.SubElement(e, f'{{{NS_M}}}r')
                    rPr_R = ET.SubElement(r_R, f'{{{NS_M}}}rPr')
                    ET.SubElement(rPr_R, f'{{{NS_M}}}scr', {f'{{{NS_M}}}val': 'double-struck'})
                    t_R = ET.SubElement(r_R, f'{{{NS_M}}}t')
                    t_R.text = 'R'
                    
                    sup = ET.SubElement(sSup, f'{{{NS_M}}}sup')
                    r_d = ET.SubElement(sup, f'{{{NS_M}}}r')
                    t_d = ET.SubElement(r_d, f'{{{NS_M}}}t')
                    t_d.text = 'd'
                    print("✓ Equation (7) parentheses fixed and completed with ∈ R^d (Comment 12 resolved)")
                break

# --- (H) Update Walk-Forward Protocol (Comment 20) ---
for p in root.iter(f'{{{NS_W}}}p'):
    txt = get_node_text(p)
    if 'To prevent look-ahead bias' in txt and 'All test windows fall entirely' in txt:
        # Find runs inside p and replace the target text
        for r in p.iter(f'{{{NS_W}}}r'):
            for t in r.iter(f'{{{NS_W}}}t'):
                if t.text and 'All test windows fall entirely within a period of clustered extreme energy shocks' in t.text:
                    t.text = (
                        "While the full dataset (2008–2026, N = 4,512) incorporates historical market cycles (e.g., the 2008 global financial crisis, "
                        "the 2014–2016 oil collapse, the 2020 COVID-19/OPEC+ price war, and the 2022 Russia–Ukraine outbreak) across expanding training "
                        "partitions, the out-of-sample test windows (2024–2026) specifically stress-test model resilience under the recent era of clustered "
                        "acute geopolitical shocks (namely, the Red Sea maritime shipping crisis, direct Middle East/Iran–Israel military escalations, "
                        "Western energy sanctions enforcement, and OPEC+ supply quota interventions)."
                    )
                    print("✓ Walk-Forward text updated to clarify training history vs acute shock testing (Comment 20 resolved)")

# --- (I) Update Conclusion (Comment 29) ---
for p in root.iter(f'{{{NS_W}}}p'):
    txt = get_node_text(p)
    if 'Expanding walk-forward experiments on MG95 and DO 0.001%' in txt:
        for r in p.iter(f'{{{NS_W}}}r'):
            for t in r.iter(f'{{{NS_W}}}t'):
                if t.text and 'yielding MAE reductions at H60 of 30.1% for MG95 and 22.9% for DO 0.001%.' in t.text:
                    t.text = "yielding MAE reductions at H60 of 30.1% for MG95 (4.847 vs. 6.933) and 22.9% for DO 0.001% (7.066 vs. 9.167) relative to the strongest baselines."
                    print("✓ Conclusion text updated with explicit comparative baseline metrics (Comment 29 resolved)")

# --- (J) Clean up Comment references and ranges across document.xml ---
comment_tags = ['commentRangeStart', 'commentRangeEnd', 'commentReference']
for elem in list(root.iter()):
    for child in list(elem):
        tag = child.tag.split('}')[-1]
        if tag in comment_tags:
            elem.remove(child)
print("✓ Cleaned up comment markers from document.xml (all comments integrated into text)")

# --- (K) Insert Dedicated Data and Code Availability Section before REFERENCES ---
body = None
for child in root:
    if child.tag.split('}')[-1] == 'body':
        body = child
        break

if body is not None:
    ref_p_idx = None
    for idx, p in enumerate(body):
        if p.tag.split('}')[-1] == 'p':
            txt = get_node_text(p).strip()
            if txt == 'REFERENCES':
                ref_p_idx = idx
                break
                
    if ref_p_idx is not None:
        # Create Data and Code Availability paragraph
        p_dca = ET.Element(f'{{{NS_W}}}p')
        pPr = ET.SubElement(p_dca, f'{{{NS_W}}}pPr')
        ET.SubElement(pPr, f'{{{NS_W}}}pStyle', {f'{{{NS_W}}}val': 'BodyText'})
        ET.SubElement(pPr, f'{{{NS_W}}}spacing', {f'{{{NS_W}}}before': '120', f'{{{NS_W}}}after': '80', f'{{{NS_W}}}line': '252', f'{{{NS_W}}}lineRule': 'auto'})
        ET.SubElement(pPr, f'{{{NS_W}}}jc', {f'{{{NS_W}}}val': 'both'})
        
        r_dca_h = ET.SubElement(p_dca, f'{{{NS_W}}}r')
        rPr_h = ET.SubElement(r_dca_h, f'{{{NS_W}}}rPr')
        ET.SubElement(rPr_h, f'{{{NS_W}}}rFonts', {f'{{{NS_W}}}ascii': 'Times New Roman', f'{{{NS_W}}}hAnsi': 'Times New Roman'})
        ET.SubElement(rPr_h, f'{{{NS_W}}}b')
        ET.SubElement(rPr_h, f'{{{NS_W}}}sz', {f'{{{NS_W}}}val': '18'})
        t_dca_h = ET.SubElement(r_dca_h, f'{{{NS_W}}}t', {'{http://www.w3.org/XML/1998/namespace}space': 'preserve'})
        t_dca_h.text = "Data and Code Availability: "
        
        r_dca_t = ET.SubElement(p_dca, f'{{{NS_W}}}r')
        rPr_t = ET.SubElement(r_dca_t, f'{{{NS_W}}}rPr')
        ET.SubElement(rPr_t, f'{{{NS_W}}}rFonts', {f'{{{NS_W}}}ascii': 'Times New Roman', f'{{{NS_W}}}hAnsi': 'Times New Roman'})
        ET.SubElement(rPr_t, f'{{{NS_W}}}sz', {f'{{{NS_W}}}val': '18'})
        t_dca_t = ET.SubElement(r_dca_t, f'{{{NS_W}}}t')
        t_dca_t.text = "All source code for model architectures, training pipelines, expanding walk-forward evaluation scripts, and benchmark dataset matrices are publicly available for full peer reproducibility at the project repository: https://github.com/NguyenPhuocAnhDung/oil_forecast_tail_risk."
        
        body.insert(ref_p_idx, p_dca)
        print("✓ Inserted Data and Code Availability section before REFERENCES")

# 3. Serialize updated document.xml
updated_doc_xml = ET.tostring(root, encoding='utf-8', xml_declaration=True)
zip_entries['word/document.xml'] = updated_doc_xml

# 4. Write back to docx_path directly
with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
    for filename, data in zip_entries.items():
        z_out.writestr(filename, data)

print(f"\n🎉 Successfully updated {docx_path} in-place with all requested enhancements!")
