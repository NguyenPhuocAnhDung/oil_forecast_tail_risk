import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_v4 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv4_redline.docx'

with zipfile.ZipFile(file_v4, 'r') as z:
    doc_xml = z.read('word/document.xml')
    print(f"doc_xml bytes: {len(doc_xml)}")
    print(doc_xml[:500].decode('utf-8'))

    root = ET.fromstring(doc_xml)
    print("Root tag:", root.tag)
    print("Children tags:", [c.tag for c in root[:10]])
