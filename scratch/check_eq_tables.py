import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    doc_xml = z.read('word/document.xml')
    root = ET.fromstring(doc_xml)

def get_node_text(elem):
    texts = []
    for t in elem.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            texts.append(t.text)
    return ''.join(texts)

for tbl_idx, tbl in enumerate(root.iter()):
    tag = tbl.tag.split('}')[-1]
    if tag == 'tbl':
        txt = get_node_text(tbl)
        if any(f'({k})' in txt for k in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]):
            print(f"=== TBL[{tbl_idx}] ===")
            for tr in tbl:
                if tr.tag.split('}')[-1] == 'tr':
                    cells = [c for c in tr if c.tag.split('}')[-1] == 'tc']
                    cell_txts = [get_node_text(c) for c in cells]
                    print("  Row:", " | ".join(cell_txts))
