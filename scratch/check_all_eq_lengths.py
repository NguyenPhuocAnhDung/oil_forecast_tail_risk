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

print("=== VERIFYING ALL EQUATION TABLES POST-FIX ===")
for tbl in root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tbl'):
    tbl_text = get_text(tbl).strip()
    if any(f'({k})' in tbl_text for k in range(1, 15)):
        print("\n-------------------------------------------")
        for tr in tbl.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}tr'):
            row_txt = get_text(tr).strip()
            print("Row:", row_txt)
