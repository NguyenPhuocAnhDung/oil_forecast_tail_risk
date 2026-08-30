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

# Extract Table III (MG95) and Table IV (DO 0.001%)
tables_data = []
for tbl in root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tbl'):
    txt = get_text(tbl)
    if 'TABLE III' in txt or 'MG95 GASOLINE' in txt:
        print("=== TABLE III (MG95 Gasoline) ===")
        for tr in tbl.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tr'):
            cells = [get_text(tc).strip() for tc in tr.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tc')]
            print(" | ".join(cells))
    elif 'TABLE IV' in txt or 'DO 0.001%' in txt:
        print("\n=== TABLE IV (DO 0.001% Diesel) ===")
        for tr in tbl.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tr'):
            cells = [get_text(tc).strip() for tc in tr.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tc')]
            print(" | ".join(cells))
