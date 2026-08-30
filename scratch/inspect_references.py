import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_redline.docx'

with zipfile.ZipFile(file_path, 'r') as z:
    doc_tree = ET.fromstring(z.read('word/document.xml'))
    
    in_refs = False
    refs = []
    for p in doc_tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        t = "".join(p.itertext()).strip()
        if 'REFERENCES' in t or 'TÀI LIỆU THAM KHẢO' in t:
            in_refs = True
        if in_refs and t:
            refs.append(t)

print(f"Total reference paragraphs found: {len(refs)}")
for r in refs[:35]:
    print(r)
