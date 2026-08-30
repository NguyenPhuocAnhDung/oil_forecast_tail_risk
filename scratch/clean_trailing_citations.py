import zipfile
import xml.etree.ElementTree as ET
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    entries = {name: z.read(name) for name in z.namelist()}

root = ET.fromstring(entries['word/document.xml'])
W_NS = 'http://purl.oclc.org/ooxml/wordprocessingml/main'

def get_p_text(p):
    txts = []
    for t in p.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            txts.append(t.text)
    return ''.join(txts)

for p in root.iter(f'{{{W_NS}}}p'):
    txt = get_p_text(p)
    if 'Recent deep learning models' in txt:
        print("Raw text before clean:")
        print(txt)
        # remove duplicate trailing citations if any
        cleaned = re.sub(r'(\[\d+\])+$', '', txt.strip()).strip()
        print("\nCleaned text:")
        print(cleaned)
        
        # update single run text
        runs = p.findall(f'{{{W_NS}}}r')
        for r in runs:
            p.remove(r)
        new_r = ET.SubElement(p, f'{{{W_NS}}}r')
        new_t = ET.SubElement(new_r, f'{{{W_NS}}}t')
        new_t.text = cleaned
        new_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

entries['word/document.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in entries.items():
        z.writestr(filename, data)

# Also update redline
with zipfile.ZipFile(r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_redline.docx', 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in entries.items():
        z.writestr(filename, data)

print("\n✓ Cleaned and saved!")
