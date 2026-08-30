import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

final_file = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(final_file, 'r') as z:
    xml = z.read('word/document.xml').decode('utf-8')
    img_size = len(z.read('word/media/image1.png'))
    namelist = z.namelist()

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s).strip()

print("=== LIVE PROOF REPORT FROM GUMNETHet_FAIRv6_final.docx ===")
print(f"1. Image1 size in docx: {img_size} bytes")
print(f"2. Total zip entries: {len(namelist)}")

# Extract Title
m_title = re.search(r'<w:p\s+[^>]*>.*?Robust Probabilistic Energy Forecasting.*?</w:p>', xml, re.DOTALL)
print("\n[PROVED 1: TITLE]")
print(strip_tags(m_title.group(0)) if m_title else "Not found")

# Extract Abstract (Comment 0)
m_abs = re.search(r'<w:p\s+[^>]*>.*?Abstract—.*?</w:p>', xml, re.DOTALL)
print("\n[PROVED 2: ABSTRACT (Comment 0)]")
print(strip_tags(m_abs.group(0)) if m_abs else "Not found")

# Extract Contributions & GitHub (Comment 1 + GitHub)
m_contrib = re.search(r'<w:p\s+[^>]*>.*?The principal contributions.*?</w:p>', xml, re.DOTALL)
print("\n[PROVED 3: CONTRIBUTIONS & GITHUB (Comment 1 + GitHub Link)]")
print(strip_tags(m_contrib.group(0)) if m_contrib else "Not found")

# Extract Equations 2, 4, 7 (Comments 4, 8, 12)
pos_eq2 = xml.find('name="eq_2"')
tr_start = xml.rfind('<w:tr ', 0, pos_eq2)
tr_end = xml.find('</w:tr>', pos_eq2) + 7
print("\n[PROVED 4: EQUATION (2) (Comment 4)]")
print(strip_tags(xml[tr_start:tr_end]))

pos_eq4 = xml.find('name="eq_4"')
tr_start = xml.rfind('<w:tr ', 0, pos_eq4)
tr_end = xml.find('</w:tr>', pos_eq4) + 7
print("\n[PROVED 5: EQUATION (4) (Comment 8)]")
print(strip_tags(xml[tr_start:tr_end]))

pos_eq7 = xml.find('name="eq_7"')
tr_start = xml.rfind('<w:tr ', 0, pos_eq7)
tr_end = xml.find('</w:tr>', pos_eq7) + 7
print("\n[PROVED 6: EQUATION (7) (Comment 12)]")
print(strip_tags(xml[tr_start:tr_end]))

# Extract Walk-forward Setup (Comment 20)
m_wf = re.search(r'<w:p\s+[^>]*>.*?To prevent look-ahead bias.*?</w:p>', xml, re.DOTALL)
print("\n[PROVED 7: WALK-FORWARD PROTOCOL (Comment 20)]")
print(strip_tags(m_wf.group(0)) if m_wf else "Not found")

# Extract Conclusion (Comment 29)
m_concl = re.search(r'<w:p\s+[^>]*>.*?Expanding walk-forward experiments on MG95.*?</w:p>', xml, re.DOTALL)
print("\n[PROVED 8: CONCLUSION (Comment 29)]")
print(strip_tags(m_concl.group(0)) if m_concl else "Not found")

# Extract Data and Code Availability
m_data = re.search(r'<w:p\s+[^>]*>.*?Data and Code Availability.*?</w:p>', xml, re.DOTALL)
print("\n[PROVED 9: DATA AND CODE AVAILABILITY SECTION]")
print(strip_tags(m_data.group(0)) if m_data else "Not found")
