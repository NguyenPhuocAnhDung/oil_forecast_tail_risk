import zipfile
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_v4 = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv4_redline.docx'

with zipfile.ZipFile(file_v4, 'r') as z:
    root = ET.fromstring(z.read('word/document.xml'))

del_runs = []
ins_runs = []

for node in root.iter():
    tag = node.tag.split('}')[-1]
    if tag == 'del':
        t = "".join(node.itertext()).strip()
        author = node.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', '') or node.attrib.get('author', '')
        if t:
            del_runs.append((author, t))
    elif tag == 'ins':
        t = "".join(node.itertext()).strip()
        author = node.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', '') or node.attrib.get('author', '')
        if t:
            ins_runs.append((author, t))

print(f"Total deleted edits: {len(del_runs)}")
print(f"Total inserted edits: {len(ins_runs)}")

print("\n=== ALL 41 REDLINE EDITS IN GUMNETHet_FAIRv4_redline.docx ===")
for i in range(min(len(del_runs), len(ins_runs))):
    print(f"\n[Edit {i+1}]:")
    print(f"  ❌ CŨ (Xóa):  {del_runs[i][1]}")
    print(f"  ✅ MỚI (Sửa): {ins_runs[i][1]}")
