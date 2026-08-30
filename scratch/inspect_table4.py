import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_orig = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(backup_orig, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')

print("Length of doc_xml:", len(doc_xml))

# Let's inspect how Eq (4) is currently represented in doc_xml
pos_eq4 = doc_xml.find('name="eq_4"')
tbl_4_start = doc_xml.rfind('<w:tbl', 0, pos_eq4)
tbl_4_end = doc_xml.find('</w:tbl>', pos_eq4) + 8
print("=== Table 4 before ===")
print(doc_xml[tbl_4_start:tbl_4_end])
