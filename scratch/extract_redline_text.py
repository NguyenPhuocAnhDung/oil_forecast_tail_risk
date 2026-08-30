import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_v4 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv4_redline.docx'

with zipfile.ZipFile(file_v4, 'r') as z:
    root = ET.fromstring(z.read('word/document.xml'))

print("=== ALL REDLINE / RED TEXT IN GUMNETHet_FAIRv4_redline.docx ===")
for p in root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}p'):
    red_runs = []
    for r in p.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}r'):
        rPr = r.find('{http://purl.oclc.org/ooxml/wordprocessingml/main}rPr')
        if rPr is not None:
            color = rPr.find('{http://purl.oclc.org/ooxml/wordprocessingml/main}color')
            if color is not None and color.get('{http://purl.oclc.org/ooxml/wordprocessingml/main}val') == 'FF0000':
                t = "".join(r.itertext()).strip()
                if t:
                    red_runs.append(t)
    if red_runs:
        full_p = "".join(p.itertext()).strip()
        print(f"\n[PARAGRAPH WITH REDLINE]:\n{full_p}")
        print(f"-> Red text segments: {red_runs}")
