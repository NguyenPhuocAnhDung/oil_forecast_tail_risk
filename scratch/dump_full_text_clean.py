import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml = z.read('word/document.xml')
    root = ET.fromstring(doc_xml)

def get_text(node):
    txts = []
    for t in node.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            txts.append(t.text)
    return ''.join(txts)

paras = []
for p in root.iter():
    if p.tag.split('}')[-1] == 'p':
        t = get_text(p).strip()
        if t:
            paras.append(t)

with open('scratch/full_manuscript_text.txt', 'w', encoding='utf-8') as f:
    for i, p in enumerate(paras):
        f.write(f"[{i+1}] {p}\n\n")

print(f"Dumped {len(paras)} paragraphs to scratch/full_manuscript_text.txt")
