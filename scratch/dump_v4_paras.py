import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_v4 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv4_redline.docx'

with zipfile.ZipFile(file_v4, 'r') as z:
    root = ET.fromstring(z.read('word/document.xml'))

print("=== FIRST 20 PARAGRAPHS OF GUMNETHet_FAIRv4_redline.docx ===")
count = 0
for p in root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}p'):
    t = "".join(p.itertext()).strip()
    if t:
        count += 1
        print(f"[{count}] {t}")
        if count >= 20:
            break
