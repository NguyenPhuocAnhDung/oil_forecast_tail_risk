import zipfile
import xml.etree.ElementTree as ET
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

v7_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv7_final.docx'

with zipfile.ZipFile(v7_path, 'r') as z:
    doc_xml = z.read('word/document.xml').decode('utf-8')
    img1_size = len(z.read('word/media/image1.png'))
    root = ET.fromstring(doc_xml.encode('utf-8'))

def get_text(node):
    txts = []
    for t in node.iter():
        tag = t.tag.split('}')[-1]
        if tag in ['t', 'mText'] and t.text:
            txts.append(t.text)
    return ''.join(txts)

print("==================== VERIFICATION OF GUMNETHet_FAIRv7_final.docx ====================")
print(f"✓ Figure 1 image size: {img1_size} bytes (High-Res Vertical Architecture)")

# Check action notes
action_notes = re.findall(r'【[^】]+】', doc_xml)
print(f"Action notes remaining (should be 0): {len(action_notes)}")
if action_notes:
    print("WARNING - Action notes found:", action_notes)

# Check tracked changes
del_count = len(list(root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}del'))) + len(list(root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}del')))
ins_count = len(list(root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ins'))) + len(list(root.iter('{http://purl.oclc.org/ooxml/wordprocessingml/main}ins')))
print(f"Tracked changes remaining (should be 0): ins={ins_count}, del={del_count}")

# Check Title
print("\n[TITLE]:")
for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/main}p'):
    t = get_text(p)
    if 'Robust Probabilistic Energy' in t or 'GUMNetHet' in t:
        print(" ", t)
        break

# Check Abstract
print("\n[ABSTRACT]:")
for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/main}p'):
    t = get_text(p)
    if t.startswith('Abstract—'):
        print(" ", t[:300] + "...")
        break

# Check Baselines in Section IV
print("\n[BASELINES IN SECTION IV]:")
for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/main}p'):
    t = get_text(p)
    if 'Six representative baselines' in t or 'BiMamba' in t:
        print(" ", t)
        break

# Check Equations
print("\n[EQUATIONS SAMPLING]:")
for tbl in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/main}tbl'):
    t = get_text(tbl).strip()
    if '(4)' in t or '(7)' in t or '(13)' in t:
        print(" ", t)

print("\n==================== VERIFICATION COMPLETE ====================")
