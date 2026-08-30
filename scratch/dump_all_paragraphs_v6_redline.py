import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_redline.docx'

with zipfile.ZipFile(file_path, 'r') as z:
    doc_tree = ET.fromstring(z.read('word/document.xml'))
    paras = []
    for p in doc_tree.iter():
        if p.tag.split('}')[-1] == 'p':
            t = "".join(p.itertext()).strip()
            if t:
                paras.append(t)

print(f"Total paragraphs: {len(paras)}")
print("\n=== LAST 35 PARAGRAPHS ===")
for i, p in enumerate(paras[-35:]):
    print(f"[{i+1}] {p}")
