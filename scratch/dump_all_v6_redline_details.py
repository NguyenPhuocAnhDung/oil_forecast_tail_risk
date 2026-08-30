import zipfile
import xml.etree.ElementTree as ET
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'D:\1.Cong_Viec\NguyencuuKhoaHoc\oil_forecast_tail_risk\GUMNETHet_FAIRv6_redline.docx'

with zipfile.ZipFile(file_path, 'r') as z:
    doc_tree = ET.fromstring(z.read('word/document.xml'))
    
    # Check all action notes: e.g. 【HÀNH ĐỘNG...】 or 【...】
    full_text = "".join(doc_tree.itertext())
    action_notes = re.findall(r'【[^】]+】', full_text)
    
    del_nodes = []
    ins_nodes = []
    for node in doc_tree.iter():
        tag = node.tag.split('}')[-1]
        if tag == 'del':
            t = "".join(node.itertext()).strip()
            if t:
                del_nodes.append(t)
        elif tag == 'ins':
            t = "".join(node.itertext()).strip()
            if t:
                ins_nodes.append(t)

print("=== ALL ACTION NOTES (【...】) IN GUMNETHet_FAIRv6_redline.docx ===")
for note in action_notes:
    print(f"👉 {note}")

print(f"\nTotal action notes found: {len(action_notes)}")
print(f"Total deleted runs: {len(del_nodes)}, Total inserted runs: {len(ins_nodes)}")

# Let's save all changes to scratch/v6_redline_full_dump.txt
with open('scratch/v6_redline_full_dump.txt', 'w', encoding='utf-8') as f:
    f.write("=== ACTION NOTES ===\n")
    for note in action_notes:
        f.write(f"👉 {note}\n")
    f.write("\n=== ALL TRACKED CHANGES ===\n")
    for i in range(max(len(del_nodes), len(ins_nodes))):
        d_txt = del_nodes[i] if i < len(del_nodes) else ''
        i_txt = ins_nodes[i] if i < len(ins_nodes) else ''
        f.write(f"\n[Change #{i+1}]:\n")
        if d_txt:
            f.write(f"  ❌ Deleted : {d_txt}\n")
        if i_txt:
            f.write(f"  ✅ Inserted: {i_txt}\n")

print("Saved detailed dump to scratch/v6_redline_full_dump.txt")
