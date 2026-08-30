import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_in = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'

with zipfile.ZipFile(docx_in, 'r') as z:
    root = ET.fromstring(z.read('word/document.xml'))

def get_text(node):
    txts = []
    for t in node.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            txts.append(t.text)
    return ''.join(txts)

body = root.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')

for i, child in enumerate(body):
    if child.tag.split('}')[-1] == 'p':
        txt = get_text(child).strip()
        if txt.startswith('Abstract—'):
            print(f"Abstract paragraph element tag: {child.tag}")
            print(f"Number of child runs: {len(list(child))}")
            print(f"Abstract text: {txt[:100]}...")
            break
