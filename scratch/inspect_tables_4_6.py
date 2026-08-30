import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_orig = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(backup_orig, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')

# Let's inspect Table 4 (Equations 3 & 4)
pos_eq4 = doc_xml.find('name="eq_4"')
tbl_start_4 = doc_xml.rfind('<w:tbl', 0, pos_eq4)
tbl_end_4 = doc_xml.find('</w:tbl>', pos_eq4) + 8
print("=== CURRENT TABLE 4 XML ===")
print(doc_xml[tbl_start_4:tbl_end_4])

# Let's inspect Table 6 (Equations 6 & 7)
pos_eq7 = doc_xml.find('name="eq_7"')
tbl_start_7 = doc_xml.rfind('<w:tbl', 0, pos_eq7)
tbl_end_7 = doc_xml.find('</w:tbl>', pos_eq7) + 8
print("\n=== CURRENT TABLE 6 XML ===")
print(doc_xml[tbl_start_7:tbl_end_7])
