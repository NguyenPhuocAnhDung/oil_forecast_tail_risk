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

# Extract only body paragraphs (not inside tables)
body = root.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')
if body is None:
    body = root.find('{http://purl.oclc.org/ooxml/wordprocessingml/main}body')

narrative = []
for child in body:
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        txt = get_text(child).strip()
        if txt:
            narrative.append(txt)

print(f"Total narrative paragraphs (outside tables): {len(narrative)}")
with open('scratch/narrative_paragraphs.txt', 'w', encoding='utf-8') as f:
    for i, p in enumerate(narrative):
        f.write(f"==================== [PARA {i+1}] ====================\n{p}\n\n")

print("Saved to scratch/narrative_paragraphs.txt")
