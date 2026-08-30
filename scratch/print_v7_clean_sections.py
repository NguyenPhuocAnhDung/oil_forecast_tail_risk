import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

v7_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'

with zipfile.ZipFile(v7_path, 'r') as z:
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

print("Total paragraphs in v7:", len(paras))
print("\n[1. TITLE]:", paras[0] if paras else '')
print("\n[2. AUTHORS]:", paras[1] if len(paras) > 1 else '')
print("\n[3. ABSTRACT]:", paras[2] if len(paras) > 2 else '')
print("\n[4. KEYWORDS]:", paras[3] if len(paras) > 3 else '')

for p in paras:
    if 'Six representative baselines' in p or 'BiMamba' in p:
        print("\n[5. BASELINES & CITATION]:", p)
    if 'Data and Code Availability' in p:
        print("\n[6. DATA AVAILABILITY & GITHUB]:", p)

print("\n[7. EQUATIONS SAMPLES]:")
for tbl in root.iter():
    if tbl.tag.split('}')[-1] == 'tbl':
        txt = get_text(tbl).strip()
        if any(f'({k})' in txt for k in [1, 2, 4, 7, 10, 13]):
            print(" ", txt)
