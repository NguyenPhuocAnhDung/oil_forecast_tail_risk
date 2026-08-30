import zipfile
import xml.etree.ElementTree as ET
import os
import shutil

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'
backup_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.backup.docx'

# Make backup first
if not os.path.exists(backup_path):
    shutil.copyfile(docx_path, backup_path)
    print(f"Backup created at {backup_path}")

# Let's inspect the entire document.xml to design exact XML replacements
with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml_str = z.read('word/document.xml').decode('utf-8')

print("Document XML loaded, length:", len(doc_xml_str))
