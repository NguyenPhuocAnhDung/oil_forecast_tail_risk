import zipfile
import xml.etree.ElementTree as ET
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

body = root.find(f'{{{W_NS}}}body')

# Look for duplicate paragraph in Conclusion
p_to_remove = None
for p in body.findall(f'{{{W_NS}}}p'):
    txt = get_p_text(p).strip()
    if txt.startswith('Expanding walk-forward experiments on MG95 and DO 0.001% show that GUMNetHet achieves'):
        p_to_remove = p
        break

if p_to_remove is not None:
    body.remove(p_to_remove)
    print("✓ Removed duplicate conclusion paragraph!")
else:
    print("Duplicate paragraph not found.")

entries['word/document.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in entries.items():
        z.writestr(filename, data)

with zipfile.ZipFile(r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_redline.docx', 'w', zipfile.ZIP_DEFLATED) as z:
    for filename, data in entries.items():
        z.writestr(filename, data)

print("🎉 Saved clean deduplicated manuscript!")
