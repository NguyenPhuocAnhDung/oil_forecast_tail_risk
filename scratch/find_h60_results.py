import zipfile
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

for i, tbl in enumerate(root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tbl')):
    txt = get_text(tbl)
    if 'H60' in txt:
        print(f"\n==================== TABLE {i+1} (Contains H60) ====================")
        for tr in tbl.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tr'):
            cells = [get_text(tc).strip() for tc in tr.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tc')]
            if any('H60' in c for c in cells):
                print(" | ".join(cells))
