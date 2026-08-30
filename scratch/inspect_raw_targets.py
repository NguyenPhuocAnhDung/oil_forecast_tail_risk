import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

orig_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.backup_orig.docx'

with zipfile.ZipFile(orig_path, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')

print("Original doc_xml length:", len(doc_xml))

# Let's check our target substrings in original doc_xml

# 1. Title
title_str = "Heterogeneous Mixture-of-Experts for Probabilistic Multi-Horizon Forecasting of Refined Petroleum Prices under Geopolitical Shocks"
print("Title in doc_xml:", title_str in doc_xml)

# 2. Fig 1 Caption
fig1_cap = "Fig. 1. Architectural overview of GUMNetHet: (A) Feature partitioning, three heterogeneous experts, horizon-aware router, and multi-quantile head; (B) Paradigms of competitive baselines."
print("Fig 1 Caption in doc_xml:", fig1_cap in doc_xml)

# 3. Comment 0 in Abstract
# Let's find where Comment 0 is in doc_xml
c0_idx = doc_xml.find('commentReference w:id="0"')
if c0_idx != -1:
    print("\n=== COMMENT 0 RAW CONTEXT ===")
    print(doc_xml[max(0, c0_idx-300):min(len(doc_xml), c0_idx+300)])

# 4. Comment 1 in Contributions
c1_idx = doc_xml.find('commentReference w:id="1"')
if c1_idx != -1:
    print("\n=== COMMENT 1 RAW CONTEXT ===")
    print(doc_xml[max(0, c1_idx-300):min(len(doc_xml), c1_idx+300)])

# 5. Comment 4 in Eq 2
c4_idx = doc_xml.find('commentReference w:id="4"')
if c4_idx != -1:
    print("\n=== COMMENT 4 RAW CONTEXT ===")
    print(doc_xml[max(0, c4_idx-300):min(len(doc_xml), c4_idx+300)])

# 6. Comment 8 in Eq 4
c8_idx = doc_xml.find('commentReference w:id="8"')
if c8_idx != -1:
    print("\n=== COMMENT 8 RAW CONTEXT ===")
    print(doc_xml[max(0, c8_idx-300):min(len(doc_xml), c8_idx+300)])

# 7. Comment 12 in Eq 7
c12_idx = doc_xml.find('commentReference w:id="12"')
if c12_idx != -1:
    print("\n=== COMMENT 12 RAW CONTEXT ===")
    print(doc_xml[max(0, c12_idx-300):min(len(doc_xml), c12_idx+300)])

# 8. Comment 20 in Walk-Forward
c20_idx = doc_xml.find('commentReference w:id="20"')
if c20_idx != -1:
    print("\n=== COMMENT 20 RAW CONTEXT ===")
    print(doc_xml[max(0, c20_idx-300):min(len(doc_xml), c20_idx+300)])

# 9. Comment 29 in Conclusion
c29_idx = doc_xml.find('commentReference w:id="29"')
if c29_idx != -1:
    print("\n=== COMMENT 29 RAW CONTEXT ===")
    print(doc_xml[max(0, c29_idx-300):min(len(doc_xml), c29_idx+300)])
