import zipfile
import re
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

final_file = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(final_file, 'r') as z:
    xml = z.read('word/document.xml').decode('utf-8')

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s).strip()

# 1. Abstract
m_abs = re.search(r'<w:p\s+[^>]*>.*?Abstract—.*?</w:p>', xml, re.DOTALL)
print("=== [1. ABSTRACT (Comment 0)] ===")
print(strip_tags(m_abs.group(0)) if m_abs else "Not found")

# 2. Contributions
m_contrib = re.search(r'<w:p\s+[^>]*>.*?The principal contributions.*?</w:p>', xml, re.DOTALL)
print("\n=== [2. CONTRIBUTIONS (Comment 1)] ===")
print(strip_tags(m_contrib.group(0)) if m_contrib else "Not found")

# 3. Equation 2
m_eq2 = re.search(r'<w:bookmarkStart[^>]*w:name="eq_2".*?</w:tr>', xml, re.DOTALL)
print("\n=== [3. EQUATION (2) (Comment 4)] ===")
# find the tr containing eq_2
pos_eq2 = xml.find('name="eq_2"')
tr_start = xml.rfind('<w:tr ', 0, pos_eq2)
tr_end = xml.find('</w:tr>', pos_eq2) + 7
print(strip_tags(xml[tr_start:tr_end]))

# 4. Equation 4
pos_eq4 = xml.find('name="eq_4"')
tr_start = xml.rfind('<w:tr ', 0, pos_eq4)
tr_end = xml.find('</w:tr>', pos_eq4) + 7
print("\n=== [4. EQUATION (4) (Comment 8)] ===")
print(strip_tags(xml[tr_start:tr_end]))

# 5. Equation 7
pos_eq7 = xml.find('name="eq_7"')
tr_start = xml.rfind('<w:tr ', 0, pos_eq7)
tr_end = xml.find('</w:tr>', pos_eq7) + 7
print("\n=== [5. EQUATION (7) (Comment 12)] ===")
print(strip_tags(xml[tr_start:tr_end]))

# 6. Walk-forward Setup
m_wf = re.search(r'<w:p\s+[^>]*>.*?To prevent look-ahead bias.*?</w:p>', xml, re.DOTALL)
print("\n=== [6. WALK-FORWARD SETUP (Comment 20)] ===")
print(strip_tags(m_wf.group(0)) if m_wf else "Not found")

# 7. Conclusion
m_concl = re.search(r'<w:p\s+[^>]*>.*?Expanding walk-forward experiments on MG95.*?</w:p>', xml, re.DOTALL)
print("\n=== [7. CONCLUSION (Comment 29)] ===")
print(strip_tags(m_concl.group(0)) if m_concl else "Not found")
