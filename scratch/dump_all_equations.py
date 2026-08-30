import zipfile
import re
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

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

print("==================== ALL EQUATIONS IN MANUSCRIPT ====================")

for tbl in root.iter():
    tag = tbl.tag.split('}')[-1]
    if tag == 'tbl':
        tbl_text = get_text(tbl).strip()
        # check if it has equation numbering like (1), (2), etc.
        m = re.search(r'\(([0-9]+)\)', tbl_text)
        if m:
            print(f"\n--- Equation ({m.group(1)}) ---")
            print(tbl_text)

# Also check for standalone paragraphs with equations
for p in root.iter():
    tag = p.tag.split('}')[-1]
    if tag == 'p':
        p_text = get_text(p).strip()
        m = re.search(r'\(([0-9]+)\)$', p_text)
        if m and not any(k in p_text for k in ['Table', 'Fig']):
            print(f"\n--- Standalone Equation Paragraph ({m.group(1)}) ---")
            print(p_text)
