import zipfile
import xml.etree.ElementTree as ET

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

print("=== ALL TABLES IN DOC ===")
tbl_idx = 0
for elem in root.iter():
    tag = elem.tag.split('}')[-1]
    if tag == 'tbl':
        tbl_idx += 1
        txt = get_node_text(elem)
        print(f"Table #{tbl_idx}: {txt[:100]}")
